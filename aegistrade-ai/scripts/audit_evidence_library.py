"""Summarise actual downloaded evidence and point-in-time financial coverage."""
from pathlib import Path
from datetime import date,datetime,time,timedelta,timezone
from bisect import bisect_right
from collections import Counter
import argparse,json,os,csv
from scripts.launch_local import read_env


def build(stage='after'):
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    data=Path(os.getenv('AEGIS_DATA_DIR',str(root/'data')))
    from aegistrade.universes import PROFILES,folder
    from aegistrade.evidence_library import read_archive,atomic
    from aegistrade.company_research import store_root,_has_financial_content,RISK_SCAN_VERSION,IST
    from aegistrade.nse_data import load_dataset
    symbols=[];days={};definitions={}
    for key in PROFILES:
        frame,manifest=load_dataset(folder(data,key));definitions[key]=manifest['symbols']
        for symbol in manifest['symbols']:
            if symbol not in symbols:symbols.append(symbol)
            dates=frame.loc[(frame.Symbol==symbol)&(frame.Date.dt.date>=date.fromisoformat(manifest['requested_start']))&(frame.Date.dt.date<=date.fromisoformat(manifest['requested_end'])),'Date']
            days.setdefault(symbol,set()).update(d.date() for d in dates)
    rows={s:{'symbol':s,'existing_packs':0,'packs_financial_ready':0,'packs_adverse_ready':0,'pack_gaps':[]} for s in symbols}
    for path in (store_root()/'packs').glob('*.json'):
        try:r=json.loads(path.read_text())
        except (OSError,ValueError):continue
        s=r.get('symbol')
        if s not in rows:continue
        row=rows[s];row['existing_packs']+=1;cutoff=datetime.fromisoformat(r['decision_at']);docs=r.get('documents',[])
        financial=any(d['kind'] in {'financial_results','annual_report'} and d['extraction_status']=='readable' and _has_financial_content(d['text']) and timedelta(0)<=cutoff-datetime.fromisoformat(d['available_at'])<=timedelta(days=180) for d in docs)
        scan=r.get('risk_scan',{});urls=scan.get('selected_urls',[])
        adverse=r.get('risk_scan_version')==RISK_SCAN_VERSION and r.get('coverage',{}).get('exchange_scan_complete') and scan.get('candidate_count',999)<=scan.get('bounded_limit',0) and all(any(d['source_url']==u and d['extraction_status']=='readable' for d in docs) for u in urls)
        row['packs_financial_ready']+=bool(financial);row['packs_adverse_ready']+=bool(adverse)
        reasons=[]
        if not financial:reasons.append('NO_READABLE_FINANCIAL')
        if r.get('risk_scan_version')!=RISK_SCAN_VERSION:reasons.append('STALE_SCAN_VERSION')
        if scan.get('candidate_count',999)>scan.get('bounded_limit',0):reasons.append('SCAN_CAP_OR_MISSING_SCAN')
        if not r.get('coverage',{}).get('exchange_scan_complete'):reasons.append('INCOMPLETE_METADATA')
        if any(not any(d['source_url']==u and d['extraction_status']=='readable' for d in docs) for u in urls):reasons.append('UNREADABLE_RISK_ATTACHMENT')
        if reasons:row['pack_gaps'].append({'date':r['decision_at'][:10],'reasons':reasons})
    for s,row in rows.items():
        catalogue=read_archive(s);docfile=store_root()/'issuer_archives'/(s+'.documents.json')
        docs=json.loads(docfile.read_text()).get('documents',[]) if docfile.exists() else []
        row.update(metadata_rows=len(catalogue['rows']) if catalogue else 0,
            failed_metadata_windows=sum(not w.get('complete') for w in catalogue['windows']) if catalogue else None,
            selected_documents=len(docs),readable_documents=sum(d.get('status')=='readable' for d in docs),
            financial_documents=sum(bool(d.get('financial_content')) for d in docs),ocr_documents=sum(bool(d.get('ocr')) for d in docs),
            unavailable_documents=sum(d.get('status') in {'unavailable','unreadable'} for d in docs))
        financial=sorted(datetime.fromisoformat(d['available_at']) for d in docs if d.get('status')=='readable' and d.get('financial_content'))
        covered=0;missing=[]
        for day in sorted(days.get(s,[])):
            at=datetime.combine(day,time(15,30),IST);i=bisect_right(financial,at)-1
            if i>=0 and at-financial[i]<=timedelta(days=180):covered+=1
            else:missing.append(str(day))
        row['evaluated_trading_sessions']=len(days.get(s,[]));row['sessions_with_recent_downloaded_financial']=covered
        row['financial_coverage_pct']=round(100*covered/max(1,len(days.get(s,[]))),2)
        row['financial_gap_date_examples']=missing[:10]
    totals={k:sum(r[k] for r in rows.values()) for k in ['existing_packs','packs_financial_ready','packs_adverse_ready','metadata_rows','selected_documents','readable_documents','financial_documents','ocr_documents','unavailable_documents','evaluated_trading_sessions','sessions_with_recent_downloaded_financial']}
    report={'stage':stage,'generated_utc':datetime.now(timezone.utc).isoformat(),'universes':definitions,'unique_stocks':len(symbols),'totals':totals,'stocks':list(rows.values()),
            'model_calls':0,'limits':['Financial coverage counts recent readable cached source text, not financial accuracy or an adverse-free company.','Native OCR text is machine extracted and must be checked against original PDF table columns.','Publication/dissemination cutoffs remain authoritative; current retrieval is not a certified historical page-version chain.','Selected official issuer sources are not an exhaustive independent-news/newsletter archive.','Pre-listing sessions are excluded using actual available OHLCV bars.']}
    target=root/'reports'/('universe_evidence_coverage_'+stage+'.json');atomic(target,report)
    if stage=='after':atomic(store_root()/'library_status.json',report)
    csvpath=target.with_suffix('.csv')
    with csvpath.open('w',newline='') as out:
        keys=[k for k in next(iter(rows.values())) if k not in {'pack_gaps','financial_gap_date_examples'}]
        writer=csv.DictWriter(out,fieldnames=keys,extrasaction='ignore');writer.writeheader();writer.writerows(rows.values())
    print(json.dumps({'path':str(target),'unique_stocks':len(symbols),'totals':totals},indent=2));return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['before','after'],default='after');a=p.parse_args();build(a.stage)
if __name__=='__main__':main()
