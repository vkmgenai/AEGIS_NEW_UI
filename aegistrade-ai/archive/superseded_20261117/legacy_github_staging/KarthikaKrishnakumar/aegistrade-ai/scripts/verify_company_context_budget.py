"""Real NSE/MCP/neural context-size smoke, MOCKED generation; zero model requests."""
import os,json
from pathlib import Path
from unittest.mock import patch
from scripts.launch_local import read_env


def main():
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    os.environ['AEGIS_LLM_BACKEND']='openrouter';os.environ.pop('AEGIS_LLM_MODEL',None)
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.agentic import run_agentic_case
    from aegistrade.llm_research import RouterClient
    frame=prepare_indicators(load_configured_market());reports=[]
    for symbol in ['TMPV','BHARTIARTL','AXISBANK','HINDALCO']:
        row=frame[(frame.Symbol==symbol)&(frame.Date.astype(str)=='2023-12-01')].iloc[0]
        snapshot={'symbol':symbol,'date':'2023-12-01','regime':row.Regime,'approved_candidate':row.RoutedStrategy,
            **{k:float(row[k]) for k in ['Close','RSI14','ADX14','EMA20','EMA50','ATR14']}}
        contexts=[]
        def mock(self,messages,**kw):
            self.calls+=1;contexts.append(len(json.dumps(messages)))
            role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
            observations=[json.loads(m['content']) for m in messages if m['role']=='tool']
            if not observations:
                names={'market':['market_snapshot','company_evidence'],'strategy':['search_policy','check_strategy'],
                       'critic':['company_evidence','search_policy','check_strategy']}[role]
                return {'tool_calls':[{'id':n,'type':'function','function':{'name':n,'arguments':json.dumps({'query':'human approval risk'} if n=='search_policy' else {})}} for n in names]}
            if role=='market':
                pack=next(o for o in observations if 'pack_sha256' in o);doc=next(d for d in pack['documents'] if d['financial_content_detected'])
                payload={'regime':snapshot['regime'],'explanation':'MOCKED for context-budget validation.',
                    'company':{'status':'SUFFICIENT','summary':'MOCKED interpretation; no genuine model conclusion.',
                        'citations':[doc['id']],'event_risks':[],'limitations':['MOCKED generation; actual public source context.']}}
            elif role=='strategy':
                policy=next(d['id'] for o in observations for d in o.get('results',[]) if d.get('authority')=='project_policy')
                payload={'strategy':snapshot['approved_candidate'],'portfolio_action':'ENTER','citations':[policy],
                    'explanation':'MOCKED for context-budget validation.'}
            else:payload={'accept':True,'reason':'MOCKED critic for context-budget validation.'}
            return {'content':json.dumps(payload)}
        with patch.object(RouterClient,'chat',mock):out=run_agentic_case(snapshot,model='MOCKED_CONTEXT_TEST',backend='openrouter')
        reports.append({'symbol':symbol,'guard_pass':out['guard_pass'],'max_context_chars':max(contexts),
            'model_responses':'MOCKED','actual_model_requests':0,'errors':out['model_errors']})
    (root/'reports'/'company_context_budget_smoke.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
    return 0 if all(r['guard_pass'] for r in reports) else 1

if __name__=='__main__':raise SystemExit(main())
