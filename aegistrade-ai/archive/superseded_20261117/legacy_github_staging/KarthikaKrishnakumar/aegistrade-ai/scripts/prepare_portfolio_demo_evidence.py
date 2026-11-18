"""Repair known cached quarterly attachments for the tiny UI demo. Zero inference.

Uses only previously selected official URLs and preserved publication timestamps.
Original pack versions remain content-addressed; changed evidence needs fresh C2.
"""
import json,os,hashlib
from datetime import datetime,timezone
from pathlib import Path
from scripts.launch_local import read_env


def main():
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    from aegistrade.company_research import NSEArchive,pack_path,_persist_pack,read_company_research,EVIDENCE_VIEW_VERSION,CompanyDocument
    archive=NSEArchive();reports=[]
    for symbol in ['TMPV','BHARTIARTL','AXISBANK','HINDALCO']:
        path=pack_path(symbol,'2023-12-01')
        if not path.exists():raise ValueError('Prepare the exact dated company pack first: '+symbol)
        raw=json.loads(path.read_text());repairs=[]
        for doc in raw['documents']:
            if doc['kind']!='financial_results' or doc['extraction_status']=='readable':continue
            try:
                text,sha=archive.pdf_text(doc['source_url'])
                if len(text.strip())<300:
                    repairs.append({'id':doc['id'],'status':'still_unreadable'});continue
                doc.update(text=text,archive_sha256=sha,content_sha256=hashlib.sha256(text.encode()).hexdigest(),
                    extraction_status='readable',retrieved_at=archive.last_pdf_retrieved_at)
                CompanyDocument.model_validate(doc);repairs.append({'id':doc['id'],'status':'repaired','characters':len(text)})
            except Exception as exc:repairs.append({'id':doc['id'],'status':'unavailable','error_type':type(exc).__name__})
        raw['evidence_view_version']=EVIDENCE_VIEW_VERSION
        if repairs:raw.setdefault('repair_events',[]).append({'at':datetime.now(timezone.utc).isoformat(),'attachments':repairs})
        _persist_pack(path,raw);pack=read_company_research(symbol,'2023-12-01')
        reports.append({'symbol':symbol,'status':pack['status'],'view_version':pack['evidence_view_version'],
            'pack_sha256':pack['pack_sha256'],'repairs':repairs,'tool_payload_chars':len(json.dumps(pack))})
    (root/'reports'/'portfolio_demo_evidence.json').write_text(json.dumps({'date':'2023-12-01','model_calls':0,'packs':reports},indent=2))
    print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
