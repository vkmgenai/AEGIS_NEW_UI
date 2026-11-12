import json,sqlite3,uuid
from datetime import timedelta
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from aegistrade.safety import RiskInputs,RiskParameters,make_demo_order,AuditBroker,utc_now
from aegistrade.knowledge import evaluate_retrieval
from aegistrade.engine import backtest,TradePolicy,buy_and_hold


def test_true_recall_is_not_any_hit():
    class Retriever:
        def search(self,*a,**kw):return [{'id':'A'}]
    score=evaluate_retrieval(Retriever(),[{'id':'q','query':'x','relevant_ids':['A','B']}])
    assert score['hit_at_k']==1 and score['recall_at_k']==.5


def test_nonfinite_values_fail_closed(tmp_path):
    with pytest.raises(ValueError):RiskInputs(equity=float('inf'),available_cash=1,current_positions=0)
    inputs=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    broker=AuditBroker(tmp_path/'broker.db');policy=RiskParameters()
    order=make_demo_order('DEMO',100,2,'EMA_TREND','2024-01-01',inputs,policy)
    assert broker.submit(order,broker.approve(order),float('nan'),utc_now().isoformat(),inputs,policy)['status']=='REJECTED'


def test_missing_bar_retains_position_value_and_daily_loss_gate():
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    f=prepare_indicators(synthetic_market(n_days=180,symbols=['RELIANCE']))
    full,events,_=backtest(f)
    first_buy=events[events.Event=='BUY'].iloc[0]
    next_dates=f[f.Date>first_buy.Date].Date
    missing_date=next_dates.iloc[0]
    # Another symbol maintains the portfolio session while the held asset has no bar.
    other=f[f.Date==missing_date].copy();other['Symbol']='OTHER';other['Ready']=False
    partial=pd.concat([f[f.Date!=missing_date],other],ignore_index=True)
    curve,_,_=backtest(partial)
    r=curve[curve.Date==missing_date].iloc[0]
    assert r.Equity>r.Cash and r.Positions>0
    benchmark,metrics=buy_and_hold(f,TradePolicy())
    assert len(benchmark)==180 and metrics['ending_equity']>0


def test_reflection_never_learns_from_heldout_or_provider_failure():
    from aegistrade.reflection import reflect_development_failure
    with pytest.raises(ValueError,match='development'):
        reflect_development_failure({'settings':{'dataset_split':'heldout'}},'x','unused')
    with pytest.raises(ValueError,match='operational fix'):
        reflect_development_failure({'settings':{'dataset_split':'development'},'outputs':[
            {'case_id':'x','config':'C2','model_errors':['provider failed'],'trajectory':[]}]},'x','unused')


def test_sqlite_checkpoint_survives_rebuilding_graph_and_edit(tmp_path,researched_context):
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.types import Command
    from aegistrade.workflow import build_trade_graph
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators,entry_signal
    from aegistrade.knowledge import PolicyRetriever
    from aegistrade.openrouter import BudgetedExplainer
    f=prepare_indicators(synthetic_market(n_days=180))
    row=next(r for r in f.itertuples() if r.Ready and entry_signal(r,r.RoutedStrategy))
    inputs=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    broker=AuditBroker(tmp_path/'broker.db');cfg={'configurable':{'thread_id':uuid.uuid4().hex}}
    def graph(saver):return build_trade_graph(f,broker,inputs,RiskParameters(),PolicyRetriever(),BudgetedExplainer(),saver,
            research_context=researched_context(row),quote_price=float(row.Close),quote_observed_utc=utc_now().isoformat())
    with SqliteSaver.from_conn_string(str(tmp_path/'checkpoints.db')) as saver:
        paused=graph(saver).invoke({'symbol':row.Symbol,'signal_date':str(row.Date.date())},cfg)
        old_hash=paused['__interrupt__'][0].value['payload_hash']
    with SqliteSaver.from_conn_string(str(tmp_path/'checkpoints.db')) as saver:
        g=graph(saver)
        assert g.get_state(cfg).next==('approval',)
        edited=g.invoke(Command(resume={'decision':'edit','changes':{'quantity':1}}),cfg)
        new_hash=edited['__interrupt__'][0].value['payload_hash']
        assert new_hash!=old_hash
        blocked=g.invoke(Command(resume={'decision':'approve','payload_hash':old_hash}),cfg)
        assert blocked['status']=='REJECTED'
    assert not broker.conn.execute('SELECT * FROM orders').fetchall()


def test_research_provenance_blocks_invalid_link(monkeypatch,tmp_path):
    import app.api as api
    monkeypatch.setattr(api,'DATA',tmp_path)
    folder=tmp_path/'research_runs';folder.mkdir()
    runid='a'*32
    (folder/(runid+'.json')).write_text(json.dumps({'outputs':[{'config':'C2','case_id':'bad','guard_pass':False}]}))
    c=TestClient(api.app)
    response=c.post('/workflow/start',json={'research_run_id':runid,'research_case_id':'bad'})
    assert response.status_code==422


def test_passing_c2_case_links_to_exact_human_review(monkeypatch,tmp_path,completed_c2):
    import app.api as api
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators,entry_signal
    from aegistrade.research_service import select_cases,ResearchSettings
    monkeypatch.setattr(api,'DATA',tmp_path)
    for name in ('_broker','_runs_db','_checkpointer'):monkeypatch.setattr(api,name,None)
    f=prepare_indicators(synthetic_market(n_days=180))
    monkeypatch.setattr(api,'_frame',f)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','private-integration-reviewer')
    row=next(r for r in f.itertuples() if r.Ready and entry_signal(r,r.RoutedStrategy))
    snapshot={'symbol':row.Symbol,'date':str(row.Date.date()),'regime':row.Regime,'approved_candidate':row.RoutedStrategy,
              **{k:float(getattr(row,k)) for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14')}}
    folder=tmp_path/'research_runs';folder.mkdir();runid='b'*32;caseid=row.Symbol+'-'+snapshot['date']
    output=completed_c2(snapshot);output['case_id']=caseid
    (folder/(runid+'.json')).write_text(json.dumps({'outputs':[output]}))
    c=TestClient(api.app)
    start=c.post('/workflow/start',json={'research_run_id':runid,'research_case_id':caseid})
    assert start.status_code==200,start.text
    data=start.json();pending=data['interrupts'][0]
    assert pending['research']['run_id']==runid and pending['order']['symbol']==row.Symbol
    assert pending['explanation']==output['explanation']
    finished=c.post('/workflow/resume',json={'thread_id':data['thread_id'],'decision':'approve','payload_hash':pending['payload_hash']},
                    headers={'X-Reviewer-Token':'private-integration-reviewer'})
    assert finished.status_code==200 and finished.json()['status']=='ACCEPTED_SIMULATED'
