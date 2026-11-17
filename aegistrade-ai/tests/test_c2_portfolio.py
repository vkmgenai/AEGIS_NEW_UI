"""Chronological portfolio/accounting/restart contracts; all generation is MOCKED."""
import json
from datetime import date
import pandas as pd
import pytest
from aegistrade.c2_portfolio import C2PortfolioSettings,create_run,execute_run,human_override_metrics,load,save,state_path,result_for,resolve_human_override
from tests.company_fixtures import FakeArchive
from aegistrade.company_research import prepare_company_research


def history(days=75):
    dates=pd.bdate_range('2024-01-01',periods=days)
    return pd.DataFrame([{'Date':d,'Symbol':'DEMO','Open':100.+i*.1,'High':102.+i*.1,'Low':99.+i*.1,
        'Close':101.+i*.1,'Volume':2_000_000,'Ready':True,'Regime':'TREND','RoutedStrategy':'EMA_TREND',
        'RSI14':50.,'ADX14':30.,'EMA20':99.,'EMA50':95.,'ATR14':2.,'Prior20High':200.,'RealizedVol20':.2}
        for i,d in enumerate(dates)])

def settings(f,budget=80,review=2,trailing=False):
    return C2PortfolioSettings(start_date=f.Date.iloc[60].date(),end_date=f.Date.iloc[-1].date(),max_model_calls=budget,
        holding_review_sessions=review,take_profit_percent=0,review_after_gap=False,trailing_stop_enabled=trailing,consent_to_paid_calls=True,approve_historical_rules=True)

def prepare(symbol,day):return prepare_company_research(symbol,day,provider=FakeArchive())

def runner(completed_c2,actions=None,seen=None):
    def research(snapshot,*a,**kw):
        if seen is not None:seen.append(snapshot.copy())
        out=completed_c2(snapshot)
        action='ENTER' if snapshot['research_purpose']=='ENTRY' else (actions.pop(0) if actions else 'HOLD')
        out['portfolio_action']=action;out['handoffs']['strategy']['payload']['portfolio_action']=action
        out['usage']=[{'total_tokens':123,'cost':.001}]
        return out
    return research


def test_full_c2_entry_hold_and_unsold_terminal_mark(completed_c2):
    f=history();seen=[];rid=create_run(f,settings(f));r=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    assert r['status']=='COMPLETED'
    buys=[x for x in r['ledgers']['C2'] if x['event']=='BUY'];assert len(buys)==1
    assert buys[0]['date']>buys[0]['signal_date']
    assert any(s['research_purpose']=='HOLDING_REVIEW' for s in seen)
    assert len(r['open_holdings'])==1 and not any(x['event'].startswith('SELL') for x in r['ledgers']['C2'])
    assert r['accounting']['forced_end_liquidation'] is False
    assert abs(r['accounting']['equity_identity_error'])<1e-7
    assert r['accounting']['unrealized_pnl']!=0 and r['accounting']['realized_pnl']==0
    assert r['model_usage']['attempted_calls']==6*len(seen)
    assert r['model_usage']['provider_cost_usd']==pytest.approx(.001*len(seen))


def test_c2_exit_fills_next_open_and_can_reenter(completed_c2):
    f=history(69);seen=[];rid=create_run(f,settings(f));r=execute_run(rid,f,researcher=runner(completed_c2,['EXIT'],seen),preparer=prepare)
    exit_decision=next(d for d in r['decisions'] if d['action']=='EXIT')
    sold=next(x for x in r['ledgers']['C2'] if x['event']=='SELL_C2')
    assert sold['date']>exit_decision['date'] and sold['research_id']==exit_decision['id']
    assert sold['entry_research_id'] and r['accounting']['realized_pnl']!=0
    assert abs(r['accounting']['equity_identity_error'])<1e-7


def test_stop_gap_exits_without_waiting_for_model(completed_c2):
    f=history(66);f.loc[62,['Open','Low']]=[90.,88.]
    rid=create_run(f,settings(f,review=60));r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    stop=next(x for x in r['ledgers']['C2'] if x['event']=='SELL_STOP')
    assert stop['price']==pytest.approx(90*(1-.001))
    assert not any(d['purpose']=='HOLDING_REVIEW' for d in r['decisions'] if 'purpose' in d)
    assert abs(r['accounting']['equity_identity_error'])<1e-7


def test_code_exit_and_last_day_signal_do_not_force_a_sale(completed_c2):
    f=history(66);f.loc[f.index[-1],'EMA20']=90.;f.loc[f.index[-1],'EMA50']=95.
    rid=create_run(f,settings(f,review=60));r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert len(r['open_holdings'])==1
    assert any(o['side']=='SELL' for o in r['pending_orders'])
    assert not any(x['event'].startswith('SELL') for x in r['ledgers']['C2'])
    f=history(67);f.loc[64,'EMA20']=90.;f.loc[64,'EMA50']=95.
    rid=create_run(f,settings(f,review=60));r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert any(x['event']=='SELL_SIGNAL' and x['date']==str(f.Date.iloc[65].date()) for x in r['ledgers']['C2'])


def test_budget_pause_resume_retains_fills_and_no_duplicate_research(completed_c2):
    f=history(69);seen=[];rid=create_run(f,settings(f,budget=8));research=runner(completed_c2,seen=seen)
    first=execute_run(rid,f,researcher=research,preparer=prepare)
    assert first['status']=='PAUSED_BUDGET' and not first['comparison_valid_for_full_period']
    assert [x['mode'] for x in first['metrics']]==['C2']
    state=load(rid);assert state['phase']=='CLOSE' and len(first['ledgers']['C2'])==1
    state['call_limit']=100;save(state_path(rid),state)
    r=execute_run(rid,f,researcher=research,preparer=prepare)
    assert r['status']=='COMPLETED' and len(r['ledgers']['C2'])==1
    assert len({(x['date'],x['symbol'],x['research_purpose']) for x in seen})==len(seen)
    assert abs(r['accounting']['equity_identity_error'])<1e-7
    # Interrupt after a paid response is durable but before its action commits.
    # Resuming must reuse that response and apply its entry exactly once.
    new_seen=[];rid2=create_run(f,settings(f));called=False
    def crash_once(out,**kw):
        nonlocal called
        if not called:called=True;raise RuntimeError('Simulated process interruption')
    partial=execute_run(rid2,f,researcher=runner(completed_c2,seen=new_seen),preparer=prepare,validator=crash_once)
    assert partial['status']=='INTERRUPTED' and partial['model_usage']['attempted_calls']==6
    finished=execute_run(rid2,f,researcher=runner(completed_c2,seen=new_seen),preparer=prepare)
    assert finished['status']=='COMPLETED'
    assert sum(x['research_purpose']=='ENTRY' for x in new_seen)==1
    assert sum(x['event']=='BUY' for x in finished['ledgers']['C2'])==1


def test_insufficient_evidence_never_calls_model_or_buys(completed_c2,monkeypatch):
    monkeypatch.setenv('AEGIS_DATED_WEB_SEARCH','false')
    f=history(65);rid=create_run(f,settings(f))
    r=execute_run(rid,f,preparer=lambda *a:{'status':'INSUFFICIENT_EVIDENCE','reasons':['No filing']},
                  researcher=lambda *a,**kw:pytest.fail('No call without evidence'))
    assert r['status']=='COMPLETED_WITH_GAPS' and not r['ledgers']['C2']
    assert r['model_usage']['attempted_calls']==0 and not r['open_holdings']


def test_human_evidence_override_opens_linked_position_without_overwriting_c2_block(completed_c2,monkeypatch):
    import aegistrade.c2_portfolio as portfolio
    f=history(66);cfg=settings(f,review=60);cfg=cfg.model_copy(update={'human_override_mode':True})
    def blocked(snapshot,*a,**kw):
        out=completed_c2(snapshot);out['guard_pass']=False
        out['model_errors']=['COMPANY_ASSESSMENT_BLOCKED: evidence coverage is INSUFFICIENT_EVIDENCE; no concrete adverse event identified.']
        out['usage']=[{'total_tokens':10,'cost':.001}];return out
    rid=create_run(f,cfg);paused=execute_run(rid,f,researcher=blocked,preparer=prepare)
    assert paused['status']=='PAUSED_HUMAN_OVERRIDE'
    pending=paused['pending_human_override'];assert pending['marker']=='HUMAN_EVIDENCE_OVERRIDE' and pending['proposed_action']=='BUY'
    assert pending['signal_close_price']>0 and pending['entry_price'] is None and pending['quantity'] is None
    assert next(d for d in paused['decisions'] if d['symbol']=='DEMO')['action']=='BLOCKED'
    monkeypatch.setattr(portfolio,'launch',lambda *a,**kw:None)
    resolve_human_override(rid,f,pending['override_id'],'APPROVE_OVERRIDE','KK','Positive technical signal; accept evidence uncertainty for the study.')
    resumed=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    buy=next(x for x in resumed['ledgers']['C2'] if x['event']=='BUY')
    assert buy['marker']=='HUMAN_EVIDENCE_OVERRIDE' and buy['human_override_id']==pending['override_id']
    assert any(x['event']=='HUMAN_DECISION' and x['decision']=='APPROVE_OVERRIDE' for x in resumed['human_override_ledger'])
    assert any(x['event']=='POSITION_OPENED' for x in resumed['human_override_ledger'])
    outcome=next(x for x in resumed['human_override_outcomes'] if x['override_id']==pending['override_id'])
    assert outcome['outcome']=='INCONCLUSIVE_OPEN' and outcome['lesson_status']=='WAIT_FOR_EXIT'


def test_human_override_metrics_follow_entry_when_sell_has_separate_override_id():
    state={'settings':{'initial_capital':100000},'human_override_ledger':[
        {'event':'HUMAN_DECISION','purpose':'ENTRY','proposed_action':'BUY','decision':'APPROVE_OVERRIDE','override_id':'entry-1'},
        {'event':'HUMAN_DECISION','purpose':'HOLDING_REVIEW','proposed_action':'SELL','decision':'APPROVE_OVERRIDE','override_id':'exit-1'},
        {'event':'HUMAN_DECISION','purpose':'ENTRY','proposed_action':'BUY','decision':'KEEP_BLOCKED','override_id':'blocked-1'}],
        'ledger':[{'event':'BUY','symbol':'DEMO','human_override_id':'entry-1'},
                  {'event':'SELL_HUMAN_OVERRIDE','symbol':'DEMO','human_override_id':'exit-1','realized_pnl':1250}]}
    metrics=human_override_metrics(state,[])
    assert metrics['human_override_realized_pnl']==1250
    assert metrics['human_override_total_pnl']==1250
    assert metrics['human_override_return_pct']==pytest.approx(1.25)
    assert metrics['human_override_closed_positions']==1


def test_human_evidence_override_can_close_existing_holding_and_link_exit(completed_c2,monkeypatch):
    import aegistrade.c2_portfolio as portfolio
    f=history(68);cfg=settings(f,review=1);cfg=cfg.model_copy(update={'human_override_mode':True})
    def entry_then_blocked_sell(snapshot,*a,**kw):
        out=completed_c2(snapshot);out['usage']=[{'total_tokens':10,'cost':.001}]
        if snapshot['research_purpose']=='ENTRY':
            out['portfolio_action']='ENTER';out['handoffs']['strategy']['payload']['portfolio_action']='ENTER'
        else:
            out['guard_pass']=False;out['portfolio_action']='HOLD'
            out['handoffs']['strategy']['payload']['portfolio_action']='HOLD'
            out['model_errors']=['COMPANY_ASSESSMENT_BLOCKED: holding evidence is REVIEW_REQUIRED; no concrete adverse event identified.']
        return out
    rid=create_run(f,cfg);paused=execute_run(rid,f,researcher=entry_then_blocked_sell,preparer=prepare)
    assert paused['status']=='PAUSED_HUMAN_OVERRIDE' and paused['pending_human_override']['proposed_action']=='SELL'
    pending=paused['pending_human_override']
    assert pending['signal_close_price']>0 and pending['entry_price']>0 and pending['quantity']>0
    assert pending['gross_position_return_pct_at_signal']==pytest.approx(100*(pending['signal_close_price']/pending['entry_price']-1))
    monkeypatch.setattr(portfolio,'launch',lambda *a,**kw:None)
    resolve_human_override(rid,f,pending['override_id'],'APPROVE_OVERRIDE','KK','Exit the holding under evidence uncertainty.')
    finished=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    sold=next(x for x in finished['ledgers']['C2'] if x['event']=='SELL_HUMAN_OVERRIDE')
    assert sold['marker']=='HUMAN_EVIDENCE_OVERRIDE' and sold['human_override_id']==pending['override_id']
    assert any(x['event']=='POSITION_CLOSED' and x['exit_reason']=='SELL_HUMAN_OVERRIDE' for x in finished['human_override_ledger'])
    outcome=next(x for x in finished['human_override_outcomes'] if x['override_id']==pending['override_id'])
    assert outcome['outcome'] in {'SUPPORTED','NOT_SUPPORTED'} and outcome['lesson_status']=='ELIGIBLE_FOR_HUMAN_REVIEW'


def test_override_bought_position_requires_human_confirmation_for_c2_exit(completed_c2,monkeypatch):
    import aegistrade.c2_portfolio as portfolio
    f=history(70);cfg=settings(f,review=1).model_copy(update={'human_override_mode':True})
    def blocked_entry_then_exit(snapshot,*a,**kw):
        out=completed_c2(snapshot);out['usage']=[{'total_tokens':10,'cost':.001}]
        if snapshot['research_purpose']=='ENTRY':
            out['guard_pass']=False
            out['model_errors']=['COMPANY_ASSESSMENT_BLOCKED: evidence coverage is INSUFFICIENT_EVIDENCE; no adverse event.']
        else:
            out['portfolio_action']='EXIT';out['handoffs']['strategy']['payload']['portfolio_action']='EXIT'
        return out
    rid=create_run(f,cfg);first=execute_run(rid,f,researcher=blocked_entry_then_exit,preparer=prepare)
    entry_id=first['pending_human_override']['override_id'];monkeypatch.setattr(portfolio,'launch',lambda *a,**kw:None)
    resolve_human_override(rid,f,entry_id,'APPROVE_OVERRIDE','KK','Approve the governed entry study.')
    exit_pause=execute_run(rid,f,researcher=blocked_entry_then_exit,preparer=prepare)
    assert exit_pause['status']=='PAUSED_HUMAN_OVERRIDE'
    assert exit_pause['pending_human_override']['override_id']==entry_id
    assert exit_pause['pending_human_override']['review_trigger']=='LINKED_POSITION_EXIT'
    resolve_human_override(rid,f,entry_id,'APPROVE_OVERRIDE','KK','Approve the linked C2 exit.')
    after_exit=execute_run(rid,f,researcher=blocked_entry_then_exit,preparer=prepare)
    assert any(x['event']=='SELL_HUMAN_APPROVED_C2' and x['human_override_id']==entry_id for x in after_exit['ledgers']['C2'])


def test_notification_inbox_lists_only_pending_human_overrides():
    from fastapi.testclient import TestClient
    import app.api as api
    f=history(65);rid=create_run(f,settings(f).model_copy(update={'human_override_mode':True}))
    state=load(rid);state['status']='PAUSED_HUMAN_OVERRIDE';state['pending_human_override']={
        'override_id':'b'*32,'symbol':'DEMO','proposed_action':'BUY','signal_date':'2024-03-01',
        'signal_close_price':123.45,'entry_price':None,'quantity':None,
        'review_trigger':'EVIDENCE_BLOCK','technical_strategy':'EMA_TREND','blocking_reason':'Insufficient dated evidence.'}
    save(state_path(rid),state)
    inbox=TestClient(api.app).get('/simulation/c2/notifications')
    assert inbox.status_code==200 and inbox.json()['count']==1
    alert=inbox.json()['notifications'][0]
    assert alert['run_id']==rid and alert['notification_id']=='b'*32 and alert['symbol']=='DEMO'
    assert alert['signal_close_price']==123.45 and alert['entry_price'] is None


def test_changed_input_blocks_resume_without_model_calls(completed_c2):
    f=history(65);rid=create_run(f,settings(f));f.loc[62,'Close']+=1
    with pytest.raises(ValueError,match='changed'):execute_run(rid,f,researcher=lambda *a,**kw:pytest.fail('No calls'))


def test_missing_final_bar_retains_last_known_holding_mark(completed_c2):
    f=history(67);other=f.copy();other['Symbol']='OTHER';other['Volume']=1  # not eligible
    f=pd.concat([f.iloc[:-1],other],ignore_index=True).sort_values(['Date','Symbol']).reset_index(drop=True)
    cfg=C2PortfolioSettings(start_date=f.Date.sort_values().unique()[60].date(),end_date=f.Date.max().date(),
        max_model_calls=80,holding_review_sessions=60,consent_to_paid_calls=True,approve_historical_rules=True)
    rid=create_run(f,cfg);r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    holding=next(h for h in r['open_holdings'] if h['symbol']=='DEMO')
    assert holding['mark_date']<r['period']['end']
    assert abs(r['accounting']['equity_identity_error'])<1e-7


def test_holding_exit_with_review_required_is_not_entry_authority(completed_c2):
    from aegistrade.research_gate import validate_completed_c2
    from aegistrade.c2_portfolio import case_snapshot
    f=history();row=next(f.iloc[[64]].itertuples())
    snapshot=case_snapshot(row,purpose='HOLDING_REVIEW',position={'quantity':2,'entry_price':100,'stop':95,
        'strategy':'EMA_TREND','entry_index':61},index=64)
    out=completed_c2(snapshot);out['handoffs']['market']['payload']['company']['status']='REVIEW_REQUIRED'
    out['company_assessment']=out['handoffs']['market']['payload']['company']
    out['handoffs']['strategy']['payload']['portfolio_action']='EXIT';out['portfolio_action']='EXIT'
    assert validate_completed_c2(out,purpose='HOLDING_REVIEW')['portfolio_action']=='EXIT'
    with pytest.raises(ValueError,match='purpose'):validate_completed_c2(out)
    out['handoffs']['strategy']['payload']['portfolio_action']='HOLD';out['portfolio_action']='HOLD'
    with pytest.raises(ValueError):validate_completed_c2(out,purpose='HOLDING_REVIEW')


def test_resume_unknown_inflight_calls_keeps_conservative_budget(completed_c2):
    f=history(65);rid=create_run(f,settings(f,budget=8));s=load(rid)
    s['budget_charged']=8;s['inflight']={'id':'f'*32,'key':'interrupted_request','reserved':8};save(state_path(rid),s)
    r=execute_run(rid,f,researcher=lambda *a,**kw:pytest.fail('Uncertain calls must consume budget'),preparer=prepare)
    assert r['status']=='PAUSED_BUDGET'
    assert r['model_usage']['uncertain_calls_reserved']==8 and not r['model_usage']['cost_reporting_complete']


def test_api_requires_auth_consent_and_does_not_run_models_on_create(monkeypatch):
    from fastapi.testclient import TestClient
    import app.api as api
    import aegistrade.c2_portfolio as portfolio
    f=history(66);monkeypatch.setattr(api,'_frame',f)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c2-portfolio-test-reviewer')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY_NOT_A_KEY')
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    launched=[];monkeypatch.setattr(portfolio,'launch',lambda rid,frame:launched.append(rid))
    client=TestClient(api.app);payload=settings(f).model_dump(mode='json')
    assert client.post('/simulation/c2/run',json=payload).status_code==403
    headers={'X-Reviewer-Token':'c2-portfolio-test-reviewer'}
    response=client.post('/simulation/c2/run',json=payload,headers=headers)
    assert response.status_code==200 and launched==[response.json()['run_id']]
    rid=response.json()['run_id']
    assert response.json()['model_usage']['attempted_calls']==0
    assert client.get('/simulation/c2/status/'+rid).status_code==200
    assert client.post('/simulation/c2/resume/'+rid,json={'additional_model_calls':8,'consent_to_paid_calls':False},headers=headers).status_code==400
    assert client.post('/simulation/c2/pause/'+rid,headers=headers).status_code==200


def test_provider_error_pauses_without_spending_whole_allowance(completed_c2):
    f=history(65);rid=create_run(f,settings(f))
    def fail(snapshot,*a,**kw):return {'guard_pass':False,'llm_calls':1,'model_errors':['Provider refused'],
                                    'usage':[{'error':'HTTPError','http_status':402}]}
    first=execute_run(rid,f,researcher=fail,preparer=prepare)
    assert first['status']=='PAUSED_PROVIDER' and first['model_usage']['attempted_calls']==1
    assert not first['ledgers']['C2'] and first['decisions'][0]['action']=='PROVIDER_FAILURE'
    r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert r['status'].startswith('COMPLETED') and any(x['event']=='BUY' for x in r['ledgers']['C2'])
    assert r['model_usage']['attempted_calls']>1
