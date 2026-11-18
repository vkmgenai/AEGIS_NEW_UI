"""Asynchronous, resumable public-data preparation; no LLM or active-data switch."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import json,threading,uuid,os
from .universes import profile,folder,curated_members,definition_hash,PROFILES,official_members,validate_manifest
from .nse_data import constituents,build_dataset,load_dataset

_executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='universe-data')
_jobs={};_lock=threading.RLock()


def _now():return datetime.now(timezone.utc).isoformat()
def _job_key(root,key):return (str(Path(root).resolve()),key)
def _path(root,key):return Path(root)/'dataset_jobs'/(profile(key)['id']+'.json')
def _save(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(payload,indent=2));tmp.replace(path)


def _owner_alive(pid):
    if not isinstance(pid,int) or pid<=0:return False
    try:os.kill(pid,0);return True
    except PermissionError:return True
    except ProcessLookupError:return False


def status(root,key):
    path=_path(root,key)
    if not path.exists():return None
    payload=json.loads(path.read_text())
    with _lock:active=_job_key(root,key) in _jobs and not _jobs[_job_key(root,key)].done()
    if not active and payload.get('owner_pid')!=os.getpid() and payload['status'] in {'QUEUED','PREPARING'}:active=_owner_alive(payload.get('owner_pid'))
    payload['worker_active']=active
    if payload['status'] in {'QUEUED','PREPARING'} and not active:payload['status']='INTERRUPTED'
    return payload


def prepare(root,key,start,end,*,legacy=None):
    root=Path(root);p=profile(key);target=folder(root,key,legacy)
    if start>=end:raise ValueError('Start must precede end')
    if end>=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Choose completed historical dates before today')
    manifest_path=target/'manifest.json'
    if manifest_path.exists():
        existing=json.loads(manifest_path.read_text())
        if existing.get('definition_sha256') and existing['definition_sha256']!=definition_hash(key):raise ValueError('Frozen definition changed; preserve the existing dataset and use a separately reviewed version')
        if existing.get('status')=='complete':
            _,complete=load_dataset(target);validate_manifest(key,complete)
            return {'status':'COMPLETE','already_prepared':True,'universe_id':key,'generation_calls':0}
        if existing.get('requested_start')!=str(start) or existing.get('requested_end')!=str(end):
            raise ValueError('Resume this dataset with its original frozen date range')
    previous=status(root,key)
    if previous and previous.get('worker_active'):raise ValueError('This universe preparation is already queued or running')
    with _lock:
        if _job_key(root,key) in _jobs and not _jobs[_job_key(root,key)].done():raise ValueError('This universe preparation is already queued or running')
        payload={'universe_id':key,'status':'QUEUED','start':str(start),'end':str(end),'created_at':_now(),'updated_at':_now(),
            'message':'Waiting for public-data worker','owner_pid':os.getpid(),'generation_calls':0,'error':None,'definition_sha256':definition_hash(key)}
        _save(_path(root,key),payload)
        _jobs[_job_key(root,key)]=_executor.submit(_prepare,root,key,start,end,target,payload,legacy)
    return payload


def _prepare(root,key,start,end,target,payload,legacy):
    path=_path(root,key);p=profile(key)
    def progress(message):
        payload.update(status='PREPARING',updated_at=_now(),message=message);_save(path,payload)
    try:
        target.mkdir(parents=True,exist_ok=True);members_file=target/'constituents.csv'
        progress('Freezing constituent snapshot')
        if not members_file.exists():
            members=curated_members() if key=='research30' else official_members()[0] if key=='nifty100' else constituents(index=p['index'])
            if len(members)!=p['count'] and key!='nifty20':raise ValueError('Official snapshot count differs from the expected universe; review before preparation')
            tmp=members_file.with_suffix('.tmp');members.to_csv(tmp,index=False);tmp.replace(members_file)
        reuse=[folder(root,k,legacy) for k in PROFILES if k!=key]
        snapshot_date=date.fromisoformat(official_members()[1]['snapshot_date']) if key=='nifty100' else date(2026,11,12) if key=='research30' else None
        manifest=build_dataset(target,start,end,top_n=p['count'],constituent_path=members_file,
            selection_mode=p['selection'],index=p['index'] or 'nifty100',universe_id=key,reuse_dirs=reuse,progress=progress,snapshot_date=snapshot_date)
        manifest.update(universe_name=p['name'],definition_sha256=definition_hash(key),
            constituent_source='config/universes/research30.csv; curated research selection' if key=='research30' else 'Official '+p['index']+' constituent CSV frozen at preparation time')
        _save(target/'manifest.json',manifest)
        payload.update(status='COMPLETE',message=f"Validated {len(manifest['symbols'])} stocks; activate explicitly in Market Data",updated_at=_now())
    except Exception as exc:
        payload.update(status='FAILED',message='Preparation stopped; no active dataset changed. Resume cached downloads after resolving the source error.',
            error=type(exc).__name__,error_detail=str(exc)[:400] if isinstance(exc,ValueError) else 'Public archive request/download failed. Inspect connectivity and source availability.',updated_at=_now())
    _save(path,payload)
