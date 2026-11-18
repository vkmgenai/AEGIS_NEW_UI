import json
import pytest
from fastapi.testclient import TestClient
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators,entry_signal

@pytest.fixture
def gated_api(monkeypatch,tmp_path,completed_c2):
    import app.api as api
    monkeypatch.setattr(api,'DATA',tmp_path)
    for name in ('_broker','_runs_db','_checkpointer'):monkeypatch.setattr(api,name,None)
    f=prepare_indicators(synthetic_market(n_days=180));monkeypatch.setattr(api,'_frame',f)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','mandatory-research-test-token')
    row=next(r for r in f.itertuples() if r.Ready and entry_signal(r,r.RoutedStrategy))
    snapshot={'symbol':row.Symbol,'date':str(row.Date.date()),'regime':row.Regime,'approved_candidate':row.RoutedStrategy,
              **{k:float(getattr(row,k)) for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14')}}
    out=completed_c2(snapshot);out['case_id']='test-case'
    folder=tmp_path/'research_runs';folder.mkdir();path=folder/('c'*32+'.json')
    def save():path.write_text(json.dumps({'outputs':[out]}))
    save()
    return api,TestClient(api.app),out,save,{'research_run_id':'c'*32,'research_case_id':'test-case'}


def test_no_research_cannot_reach_approval_or_stream(gated_api):
    api,c,_,_,_=gated_api
    for endpoint in ('/workflow/start','/workflow/start/stream'):
        response=c.post(endpoint,json={})
        assert response.status_code==422
    assert not api.broker().events()

@pytest.mark.parametrize('fault',['pending','critic_rejected','errors','C1','missing_handoff','no_citation_evidence'])
def test_incomplete_or_rejected_research_never_prepares_order(gated_api,fault):
    api,c,out,save,body=gated_api
    if fault=='pending':out['guard_pass']=False
    if fault=='critic_rejected':out['critic_accept']=False
    if fault=='errors':out['model_errors']=['Failed']
    if fault=='C1':out['config']='C1'
    if fault=='missing_handoff':out['handoffs'].pop('critic')
    if fault=='no_citation_evidence':out['tool_trace']=[]
    save()
    assert c.post('/workflow/start',json=body).status_code==422
    assert not api.broker().events()


def test_changed_research_blocks_approval_resume(gated_api):
    api,c,out,save,body=gated_api
    started=c.post('/workflow/start',json=body).json()
    pending=started['interrupts'][0]
    out['explanation']='Changed saved result after human saw proposal';save()
    result=c.post('/workflow/resume',json={'thread_id':started['thread_id'],'decision':'approve',
                  'payload_hash':pending['payload_hash']},headers={'X-Reviewer-Token':'mandatory-research-test-token'})
    assert result.status_code==409
    assert api.broker().reconcile(pending['order']['request_id'])['status']=='NOT_FOUND'


def test_changed_market_blocks_resume(gated_api):
    api,c,out,save,body=gated_api
    started=c.post('/workflow/start',json=body).json();pending=started['interrupts'][0]
    snap=out['snapshot'];mask=(api._frame.Symbol==snap['symbol'])&(api._frame.Date.dt.strftime('%Y-%m-%d')==snap['date'])
    api._frame.loc[mask,'Close']+=1
    response=c.post('/workflow/resume',json={'thread_id':started['thread_id'],'decision':'approve',
        'payload_hash':pending['payload_hash']},headers={'X-Reviewer-Token':'mandatory-research-test-token'})
    assert response.status_code==409
    assert api.broker().reconcile(pending['order']['request_id'])['status']=='NOT_FOUND'


def test_direct_graph_without_research_blocks_before_interrupt(tmp_path):
    from langgraph.checkpoint.memory import InMemorySaver
    from aegistrade.workflow import build_trade_graph
    from aegistrade.safety import AuditBroker,RiskInputs,RiskParameters
    from aegistrade.knowledge import PolicyRetriever
    from aegistrade.openrouter import BudgetedExplainer
    frame=prepare_indicators(synthetic_market(n_days=180))
    g=build_trade_graph(frame,AuditBroker(tmp_path/'b.sqlite'),RiskInputs(equity=100000,available_cash=100000,current_positions=0),
                        RiskParameters(),PolicyRetriever(),BudgetedExplainer(),InMemorySaver())
    result=g.invoke({'symbol':'RELIANCE','signal_date':'2022-06-01'}, {'configurable':{'thread_id':'no-research'}})
    assert result['status']=='BLOCKED' and '__interrupt__' not in result and 'proposal' not in result


def test_changed_company_evidence_invalidates_pending_approval(gated_api):
    from aegistrade.company_research import pack_path
    api,c,out,save,body=gated_api
    started=c.post('/workflow/start',json=body).json();pending=started['interrupts'][0]
    path=pack_path(out['snapshot']['symbol'],out['snapshot']['date'])
    pack=json.loads(path.read_text());pack['limitations'].append('New archive review after proposal');path.write_text(json.dumps(pack))
    response=c.post('/workflow/resume',json={'thread_id':started['thread_id'],'decision':'approve',
        'payload_hash':pending['payload_hash']},headers={'X-Reviewer-Token':'mandatory-research-test-token'})
    assert response.status_code==422
    assert api.broker().reconcile(pending['order']['request_id'])['status']=='NOT_FOUND'
