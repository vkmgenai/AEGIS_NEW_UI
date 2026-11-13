"""Reusable, point-in-time NSE metadata. Never a clean-company assessment.

Successful date windows and rejected rows are recorded separately. Downloaded
financial/issuer sources enter the existing company packs and temporal gates.
"""
from datetime import date,datetime,time,timedelta,timezone
from pathlib import Path
from collections import Counter
import json,os,uuid
from .company_research import store_root,digest,normalize_announcement,cutoff_for,_stamp,_has_financial_content

VERSION='nse-dated-evidence-library-v1'
SELECTION_VERSION='official-results-before-transcripts-v2'


def archive_path(symbol):
    cutoff_for(symbol,'2000-01-01')
    return store_root()/'issuer_archives'/(symbol+'.json')


def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temp.write_text(json.dumps(value,indent=2));temp.replace(path)
    finally:temp.unlink(missing_ok=True)


def read_archive(symbol):
    try:
        raw=json.loads(archive_path(symbol).read_text())
        if raw['version']!=VERSION or raw['symbol']!=symbol:return None
        if raw['payload_sha256']!=digest({'rows':raw['rows'],'windows':raw['windows']}):return None
        return raw
    except (OSError,ValueError,KeyError,TypeError):return None


def cached_announcements(symbol,start,end):
    raw=read_archive(symbol)
    if not raw:return None
    covered=start
    for w in sorted(raw['windows'],key=lambda w:w['start']):
        if not w.get('complete'):continue
        left=date.fromisoformat(w['start']);right=date.fromisoformat(w['end'])
        if right<covered:continue
        if left>covered:break
        covered=max(covered,right+timedelta(days=1))
        if covered>end:break
    if covered<=end:return None
    result=[]
    for row in raw['rows']:
        try:day=_stamp(row['an_dt']).date()
        except (ValueError,TypeError,KeyError):
            result.append(row);continue # Preserve invalid timestamps so scan cannot claim completeness.
        if start<=day<=end:result.append(row)
    return result


def fetch_archive(symbol,start,end,provider,progress=None):
    raw=read_archive(symbol) or {'version':VERSION,'symbol':symbol,'rows':[],'windows':[]}
    def fetch(left,right):
        if cached_announcements(symbol,left,right) is not None:return
        try:
            # Use the network method explicitly to avoid accidentally certifying a partial catalogue.
            rows=provider._network_announcements(symbol,left,right)
        except ValueError as exc:
            if 'truncated' in str(exc).lower() and (right-left).days>7:
                middle=left+(right-left)//2;fetch(left,middle);fetch(middle+timedelta(days=1),right);return
            raw['windows'].append({'start':str(left),'end':str(right),'complete':False,'error':type(exc).__name__});persist();return
        except Exception as exc:
            raw['windows'].append({'start':str(left),'end':str(right),'complete':False,'error':type(exc).__name__});persist();return
        valid=[];outside=0
        for r in rows:
            try:
                day=_stamp(r['an_dt']).date()
                if not left<=day<=right:outside+=1;continue
            except (ValueError,KeyError,TypeError):pass
            valid.append(r)
        raw['rows'].extend(valid)
        raw['rows']=list({digest(r):r for r in raw['rows']}.values())
        raw['windows'].append({'start':str(left),'end':str(right),'complete':outside==0,'rows':len(valid),
                               'out_of_range_rows':outside,'source':'https://www.nseindia.com/api/corporate-announcements'})
        persist()
    def persist():
        raw['retrieved_at']=datetime.now(timezone.utc).isoformat()
        raw['payload_sha256']=digest({'rows':raw['rows'],'windows':raw['windows']})
        atomic(archive_path(symbol),raw)
    cursor=start
    while cursor<=end:
        right=min(cursor+timedelta(days=364),end)
        if progress:progress(symbol+' metadata '+str(cursor)+' to '+str(right))
        fetch(cursor,right);cursor=right+timedelta(days=1)
    return read_archive(symbol)


def document_candidates(raw,end):
    cutoff=cutoff_for(raw['symbol'],str(end));items={};invalid=0
    for row in raw['rows']:
        try:item=normalize_announcement(row,raw['symbol'],cutoff)
        except (ValueError,KeyError,TypeError):invalid+=1;continue
        if item:items[item['source_url']]=item
    return sorted(items.values(),key=lambda d:d['available_at'],reverse=True),invalid


def prefetch_documents(raw,end,provider,*,repair_financial=None,progress=None):
    """Financial sources every quarter, issuer releases every quarter, annual fallback.

    Download a second results attachment if the first is not financially readable.
    Other event attachments are obtained when dated packs select them, preserving
    the existing adverse-scan policy and context bounds.
    """
    items,invalid=document_candidates(raw,end);groups={}
    for item in items:
        day=date.fromisoformat(item['available_at'][:10]);quarter=(day.year,(day.month-1)//3+1)
        if item['kind']=='financial_results':key=('financial',*quarter)
        elif item['kind']=='company_news':key=('issuer_news',*quarter)
        elif item['kind']=='annual_report':key=('annual',day.year)
        else:continue
        groups.setdefault(key,[]).append(item)
    result=[]
    previous_path=store_root()/'issuer_archives'/(raw['symbol']+'.documents.json')
    previous={d['source_url']:d for d in json.loads(previous_path.read_text()).get('documents',[])} if previous_path.exists() else {}
    for key,candidates in sorted(groups.items(),key=lambda x:str(x[0])):
        if key[0]=='financial':candidates.sort(key=lambda d:0 if d['title'].lower().startswith('financial result') else 1)
        for item in candidates[:2 if key[0]=='financial' else 1]:
            entry={k:item[k] for k in ('symbol','kind','title','source_url','published_at','available_at','timestamp_basis')}
            prior=previous.get(item['source_url'],{})
            if prior.get('status')=='unavailable' and prior.get('reason') in {'PDF page bound exceeded','PDF exceeds 32MB download bound'}:
                result.append(prior);continue
            try:
                text,sha=provider.pdf_text(item['source_url']);entry.update(status='readable' if len(text.strip())>=300 else 'unreadable',characters=len(text),archive_sha256=sha,
                    financial_content=_has_financial_content(text) if item['kind'] in {'financial_results','annual_report'} else None)
                if key[0]=='financial' and not entry['financial_content'] and repair_financial:
                    try:repaired=repair_financial(item['source_url'])
                    except Exception as exc:repaired=None;entry['ocr_error']=type(exc).__name__
                    if repaired:
                        text,sha=repaired;entry.update(status='readable' if len(text.strip())>=300 else 'unreadable',characters=len(text),archive_sha256=sha,financial_content=_has_financial_content(text),ocr=True)
            except Exception as exc:entry.update(status='unavailable',error=type(exc).__name__,reason=str(exc)[:120] if isinstance(exc,ValueError) else 'Public source request/extraction failed')
            result.append(entry)
            if progress:progress(raw['symbol']+' '+item['kind']+' '+entry['status'])
            if key[0]!='financial' or entry.get('financial_content'):break
    manifest={'version':VERSION,'selection_version':SELECTION_VERSION,'symbol':raw['symbol'],'metadata_sha256':raw['payload_sha256'],
              'invalid_metadata_rows':invalid,'documents':result,'updated_utc':datetime.now(timezone.utc).isoformat(),
              'scope':'Selected quarterly financial and issuer releases plus annual reports; not exhaustive news/adverse coverage.'}
    atomic(store_root()/'issuer_archives'/(raw['symbol']+'.documents.json'),manifest)
    return manifest


def library_status():
    """Cheap persisted summary for UI; never performs downloads or model calls."""
    path=store_root()/'library_status.json'
    if path.exists():
        report=json.loads(path.read_text())
        return {'available':True,'state':'AUDITED','report':report}
    progress={}
    for phase in ('metadata','documents','repair'):
        p=store_root()/('backfill_all_'+phase+'.json')
        if p.exists():
            r=json.loads(p.read_text());progress[phase]={k:r[k] for k in ('completed_symbols','total_symbols','updated_utc')}
    return {'available':bool(progress),'state':'PREPARING' if progress else 'NOT_PREPARED','progress':progress}
