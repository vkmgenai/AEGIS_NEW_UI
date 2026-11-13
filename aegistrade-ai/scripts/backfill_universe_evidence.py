"""Download missing dated public NSE evidence; no LLM calls or trading actions."""
from pathlib import Path
from datetime import date,timedelta,datetime,timezone
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,as_completed
import argparse,json,os
from scripts.launch_local import read_env


def work_one(task):
    from types import SimpleNamespace
    symbol,phase,start,end,ocr=task;a=SimpleNamespace(phase=phase,ocr=ocr)
    from aegistrade.company_research import NSEArchive,store_root,prepare_company_research
    from aegistrade.evidence_library import fetch_archive,read_archive,prefetch_documents,SELECTION_VERSION
    provider=NSEArchive()
    if a.phase=='metadata':
        raw=fetch_archive(symbol,start,end,provider,progress=lambda msg:print(msg,flush=True))
        return {'symbol':symbol,'metadata_rows':len(raw['rows']),'windows':len(raw['windows']),'failed_windows':sum(not w.get('complete') for w in raw['windows'])}
    if a.phase=='documents':
        raw=read_archive(symbol)
        if not raw:return {'symbol':symbol,'error':'No dated metadata catalogue'}
        repair=None
        if a.ocr:
            from aegistrade.financial_ocr import repair_pdf
            repair=repair_pdf
        saved=store_root()/'issuer_archives'/(symbol+'.documents.json')
        existing=json.loads(saved.read_text()) if saved.exists() else None
        if existing and existing.get('metadata_sha256')==raw['payload_sha256'] and existing.get('selection_version')==SELECTION_VERSION:
            docs=existing
            return {'symbol':symbol,'documents':len(docs['documents']),'financial_readable':sum(bool(d.get('financial_content')) for d in docs['documents']),'unavailable':sum(d['status'] in {'unavailable','unreadable'} for d in docs['documents']),'reused_completed_download':True}
        docs=prefetch_documents(raw,end,provider,repair_financial=repair,progress=lambda msg:print(msg,flush=True))
        return {'symbol':symbol,'documents':len(docs['documents']),'financial_readable':sum(bool(d.get('financial_content')) for d in docs['documents']),
                'unavailable':sum(d['status'] in {'unavailable','unreadable'} for d in docs['documents'])}
    from aegistrade.evidence_library import atomic
    from aegistrade.company_research import digest
    metadata=read_archive(symbol);document_file=store_root()/'issuer_archives'/(symbol+'.documents.json')
    if not document_file.exists():return {'symbol':symbol,'status':'DEFERRED_DOCUMENTS_INCOMPLETE'}
    doc_manifest=json.loads(document_file.read_text())
    if not metadata or (doc_manifest.get('metadata_sha256')!=metadata['payload_sha256'] or doc_manifest.get('selection_version')!=SELECTION_VERSION):return {'symbol':symbol,'status':'DEFERRED_DOCUMENTS_INCOMPLETE'}
    receipt=store_root()/'issuer_archives'/(symbol+'.repairs.json')
    paths=sorted((store_root()/'packs').glob(symbol+'_*.json'))
    current_hashes={p.name:digest(json.loads(p.read_text())) for p in paths}
    if receipt.exists():
        previous=json.loads(receipt.read_text())
        if previous.get('document_sha256')==digest(doc_manifest) and previous.get('pack_hashes')==current_hashes:
            return {**previous['result'],'reused_completed_repairs':True}
    class ReuseAttachments:
        def __init__(self,source):self.source=source;self.refresh=False;self.failed={}
        def announcements(self,*args):return self.source.announcements(*args)
        def pdf_text(self,url):
            if url in self.failed:raise ValueError('Previously unavailable attachment in this backfill: '+self.failed[url])
            self.source.refresh=False
            try:value=self.source.pdf_text(url)
            except Exception as exc:self.failed[url]=type(exc).__name__;raise
            self.last_pdf_retrieved_at=self.source.last_pdf_retrieved_at
            return value
    reuse=ReuseAttachments(provider)
    packs=[]
    for path in sorted((store_root()/'packs').glob(symbol+'_*.json')):
        raw=json.loads(path.read_text());day=raw['decision_at'][:10]
        # Existing snapshots are retained by _persist_pack; do not alter reviewer imports.
        web_ids=set(raw.get('web_search',{}).get('accepted_document_ids',[]))
        reviewed=[d for d in raw.get('documents',[]) if d['kind'] in {'news','newsletter'} or d['id'] in web_ids]
        try:
            fresh=prepare_company_research(symbol,day,provider=reuse,refresh=True)
            if reviewed:
                from aegistrade.company_research import _persist_pack,read_company_research
                updated=json.loads(path.read_text());urls={d['source_url'] for d in updated['documents']}
                updated['documents'].extend(d for d in reviewed if d['source_url'] not in urls)
                if raw.get('web_search'):updated['web_search']=raw['web_search']
                _persist_pack(path,updated);fresh=read_company_research(symbol,day)
            packs.append({'date':day,'status':fresh['status'],'adverse_ready':fresh['adverse_scan']['ready'],'pack_sha256':fresh['pack_sha256']})
        except Exception as exc:packs.append({'date':day,'status':'FAILED','error':type(exc).__name__})
        print(symbol+' repair '+day+' '+packs[-1]['status'],flush=True)
    result={'symbol':symbol,'packs':packs}
    atomic(receipt,{'document_sha256':digest(doc_manifest),'pack_hashes':{p.name:digest(json.loads(p.read_text())) for p in paths},'result':result})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--universe',default='research30',choices=['research30','nifty20','nifty100','all'])
    p.add_argument('--phase',choices=['metadata','documents','repair'],default='metadata')
    p.add_argument('--workers',type=int,default=3,choices=[1,2,3,4,5,6])
    p.add_argument('--ocr',action='store_true')
    a=p.parse_args();root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    data=Path(os.getenv('AEGIS_DATA_DIR',str(root/'data')))
    from aegistrade.universes import folder
    manifests=[json.loads((folder(data,key)/'manifest.json').read_text()) for key in (['research30','nifty20','nifty100'] if a.universe=='all' else [a.universe])]
    symbols=list(dict.fromkeys(s for m in manifests for s in m['symbols']));start=min(date.fromisoformat(m['requested_start']) for m in manifests)-timedelta(days=180);end=max(date.fromisoformat(m['requested_end']) for m in manifests)
    from aegistrade.company_research import NSEArchive,store_root,prepare_company_research
    from aegistrade.evidence_library import fetch_archive,read_archive,prefetch_documents,SELECTION_VERSION,atomic
    results=[]
    report=data/'company_research'/('backfill_'+a.universe+'_'+a.phase+'.json')
    executor=ThreadPoolExecutor if a.phase=='metadata' else ProcessPoolExecutor
    with executor(max_workers=a.workers) as pool:
        futures={pool.submit(work_one,(s,a.phase,start,end,a.ocr)):s for s in symbols}
        for future in as_completed(futures):
            try:r=future.result()
            except Exception as exc:r={'symbol':futures[future],'error':type(exc).__name__}
            results.append(r)
            value={'universe':a.universe,'phase':a.phase,'window_start':str(start),'window_end':str(end),'completed_symbols':len(results),'total_symbols':len(symbols),
                   'model_calls':0,'updated_utc':datetime.now(timezone.utc).isoformat(),'results':results}
            atomic(report,value);print('DONE '+json.dumps(r),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
