"""Actual NSE bars + actual stdio MCP/neural RAG, MOCKED generation, isolated ledger.

No OpenRouter request is made. The saved report is explicitly not a genuine C2
performance result; no mock run is placed in the production portfolio history.
"""
import json,os,shutil,tempfile
from pathlib import Path
from unittest.mock import patch
from scripts.launch_local import read_env


def main():
    project=Path(__file__).resolve().parents[1];os.environ.update(read_env(project/'.env'))
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    os.environ['AEGIS_LLM_BACKEND']='openrouter'
    os.environ.pop('AEGIS_LLM_MODEL',None)
    from aegistrade.llm_research import RouterClient
    from aegistrade.c2_portfolio import create_run,execute_run,C2PortfolioSettings
    from aegistrade.company_research import read_company_research
    frame=prepare_indicators(load_configured_market());data=Path(os.getenv('AEGIS_DATA_DIR','data')).resolve()
    lengths=[]
    def mock(self,messages,**kw):
        self.calls+=1;lengths.append(len(json.dumps(messages)))
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        observed=[json.loads(m['content']) for m in messages if m['role']=='tool']
        if not observed:
            tools={'market':['market_snapshot','company_evidence'],'strategy':['check_strategy','search_policy'],
                   'critic':['company_evidence','check_strategy','search_policy']}[role]
            return {'tool_calls':[{'id':n,'type':'function','function':{'name':n,'arguments':json.dumps({'query':'human approval'} if n=='search_policy' else {})}} for n in tools]}
        if role=='market':
            market=next(o['data'] for o in observed if isinstance(o.get('data'),dict) and 'regime' in o['data'])
            pack=next(o for o in observed if 'pack_sha256' in o);doc=next(d for d in pack['documents'] if d.get('financial_content_detected'))
            value={'regime':market['regime'],'explanation':'MOCKED market interpretation.',
                   'company':{'status':'SUFFICIENT','summary':'MOCKED company interpretation, not actual model research.',
                              'citations':[doc['id']],'event_risks':[],'limitations':['MOCKED generation, real cached sources.']}}
        elif role=='strategy':
            route=next(o['data']['approved_strategy'] for o in observed if 'approved_strategy' in o.get('data',{}))
            policy=next(d['id'] for o in observed for d in o.get('results',[]) if d.get('authority')=='project_policy')
            action='HOLD' if 'Purpose: HOLDING_REVIEW' in json.dumps(messages) else 'ENTER'
            value={'strategy':route,'portfolio_action':action,'citations':[policy],'explanation':'MOCKED constrained portfolio action.'}
        else:value={'accept':True,'reason':'MOCKED critic for integration verification.'}
        return {'content':json.dumps(value)}
    with tempfile.TemporaryDirectory(prefix='aegis-c2-portfolio-') as temp:
        target=Path(temp)/'company_research'/'packs';target.mkdir(parents=True)
        for symbol in ['TCS','INFY']:
            path=data/'company_research'/'packs'/f'{symbol}_2026-10-23.json'
            if path.exists():shutil.copy2(path,target/path.name)
        os.environ.update(AEGIS_DATA_DIR=temp,AEGIS_MODEL_CACHE=str(data/'model_cache'),AEGIS_CHROMA_PATH=str(data/'rag'/'chroma'))
        cfg=C2PortfolioSettings(start_date='2026-10-23',end_date='2026-11-06',max_model_calls=48,
                               consent_to_paid_calls=True,approve_historical_rules=True)
        rid=create_run(frame,cfg,source='nsepython',provenance={'requested_start':'2021-11-08','requested_end':'2026-11-08'})
        with patch.object(RouterClient,'chat',mock):result=execute_run(rid,frame,preparer=read_company_research)
        report={'generation':'MOCKED; not authentic C2 investment performance','paid_model_calls':0,
                'data':'Actual NSE20 OHLCV, 2026-10-23 through 2026-11-06','mcp':'Actual stdio; neural retrieval',
                'status':result['status'],'model_requests_mocked':result['model_usage']['attempted_calls'],
                'max_serialized_context_chars':max(lengths) if lengths else 0,
                'completed_sessions':result['progress']['completed_sessions'],'ledger_events':len(result['ledgers']['C2']),
                'open_holdings':len(result['open_holdings']),'forced_end_liquidation':result['accounting']['forced_end_liquidation'],
                'accounting_identity_error':result['accounting']['equity_identity_error'],
                'blocked_missing_evidence':sum(d['action']=='BLOCKED' for d in result['decisions'])}
    (project/'reports'/'c2_portfolio_integration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    return 0 if report['status'].startswith('COMPLETED') and report['model_requests_mocked']>=6 and abs(report['accounting_identity_error'])<.00001 else 1

if __name__=='__main__':raise SystemExit(main())
