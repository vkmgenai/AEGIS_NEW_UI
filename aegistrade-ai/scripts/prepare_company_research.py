"""Prepare dated official company research, without paid model calls.

Example: python -m scripts.prepare_company_research --symbols TCS INFY --date 2026-10-23
"""
import argparse,json,os
from pathlib import Path
from scripts.launch_local import read_env
from aegistrade.company_research import prepare_company_research,import_archived_news


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--symbols',nargs='+',required=True)
    p.add_argument('--date',required=True)
    p.add_argument('--refresh',action='store_true')
    p.add_argument('--import-news',type=Path)
    p.add_argument('--reviewer')
    a=p.parse_args()
    if a.import_news and (len(a.symbols)!=1 or not a.reviewer):p.error('News import needs one symbol and a named --reviewer')
    root=Path(__file__).resolve().parents[1]
    for key,value in read_env(root/'.env').items():os.environ.setdefault(key,value)
    rows=[]
    for symbol in a.symbols:
        try:
            pack=prepare_company_research(symbol.upper(),a.date,refresh=a.refresh,progress=lambda s:print(s,flush=True))
            if a.import_news:pack=import_archived_news(symbol.upper(),a.date,a.import_news,a.reviewer)
            rows.append({k:pack[k] for k in ('symbol','decision_at','status','pack_sha256','reasons')})
            rows[-1]['documents']=[{k:d[k] for k in ('id','kind','title','source_url','available_at','extraction_status')} for d in pack['documents']]
        except Exception as exc:rows.append({'symbol':symbol,'status':'FAILED','error_type':type(exc).__name__})
    result={'paid_model_calls':0,'results':rows}
    target=root/'reports'/'company_research_preparation.json';target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
    return 0 if all(r['status']=='SUFFICIENT' for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
