"""Read-only real-data/MCP smoke with explicitly MOCKED generation; zero paid calls."""
import json,os
from pathlib import Path
from unittest.mock import patch
from scripts.launch_local import read_env


def main():
    root=Path(__file__).resolve().parents[1]
    os.environ.update(read_env(root/'.env'))
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.agentic import run_agentic_case
    from aegistrade.research_gate import validate_completed_c2
    from aegistrade.llm_research import RouterClient
    f=prepare_indicators(load_configured_market())
    row=f[(f.Symbol=='TCS')&(f.Date.astype(str)=='2026-10-23')].iloc[0]
    snapshot={'symbol':'TCS','date':'2026-10-23','regime':row.Regime,'approved_candidate':row.RoutedStrategy,
              **{k:float(row[k]) for k in ['Close','RSI14','ADX14','EMA20','EMA50','ATR14']}}
    lengths=[]
    def mock(self,messages,**kw):
        self.calls+=1;lengths.append(len(json.dumps(messages)))
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        seen=[m for m in messages if m['role']=='tool']
        if not seen:
            names={'market':['market_snapshot','company_evidence'],'strategy':['search_policy','check_strategy'],
                   'critic':['company_evidence','search_policy','check_strategy']}[role]
            return {'tool_calls':[{'id':n,'type':'function','function':{'name':n,'arguments':json.dumps({'query':'human approval'} if n=='search_policy' else {})}} for n in names]}
        observations=[json.loads(m['content']) for m in seen]
        if role=='market':
            pack=next(x for x in observations if 'pack_sha256' in x)
            doc=next(d for d in pack['documents'] if d.get('financial_content_detected'))
            payload={'regime':snapshot['regime'],'explanation':'MOCKED technical interpretation for protocol verification.',
                     'company':{'status':'SUFFICIENT','summary':'MOCKED company interpretation; not real model analysis.',
                     'citations':[doc['id']],'event_risks':[],'limitations':['MOCKED generation, actual cached sources.']}}
        elif role=='strategy':
            policies=next(x['results'] for x in observations if 'results' in x)
            pid=next(d['id'] for d in policies if d.get('authority')=='project_policy')
            payload={'strategy':snapshot['approved_candidate'],'citations':[pid],'explanation':'MOCKED constrained route.'}
        else:payload={'accept':True,'reason':'MOCKED critic for protocol verification.'}
        return {'content':json.dumps(payload)}
    with patch.object(RouterClient,'chat',mock):out=run_agentic_case(snapshot,backend="openrouter")
    out['snapshot']=snapshot
    validated=validate_completed_c2(out)['validated_c2'] if out['guard_pass'] else False
    result={'generation':'MOCKED; not authentic paid research','paid_model_calls':0,'actual_data':'NSE TCS 2026-10-23',
            'actual_mcp_transport':out.get('tool_transport'),'retrieval_mode':os.getenv('AEGIS_RETRIEVAL_MODE'),
            'guard_pass':out['guard_pass'],'research_gate_pass':validated,'mock_llm_requests':out['llm_calls'],
            'tool_calls':out['tool_calls'],'tools_observed':out['tools_observed'],'max_serialized_context_chars':max(lengths),
            'company_documents':len(out.get('company_research',{}).get('documents',[])),'errors':out['model_errors']}
    (root/'reports'/'company_research_mcp_integration.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    return 0 if validated else 1

if __name__=='__main__':raise SystemExit(main())
