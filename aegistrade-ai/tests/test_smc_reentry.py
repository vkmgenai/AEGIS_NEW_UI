"""SMC stop-first recovery: synthetic bars/sources, no real inference."""
from copy import deepcopy
from types import SimpleNamespace as Bar
import pandas as pd
import pytest
from aegistrade import smc_reentry
from aegistrade.c2_portfolio import create_run,execute_run,load,save,state_path
from aegistrade.engine import backtest
from aegistrade.simulation_service import policy_from_settings
from tests.test_c1_smc_portfolio import smc_history,cfg,researcher,single_result,prepare


def recovery_history():
    f=smc_history()
    f.loc[66,['Open','High','Low','Close']]=[101.,104.,97.,102.]
    f.loc[67,['Open','High','Low','Close']]=[102.,106.,101.,105.]
    f.loc[68,['Open','High','Low','Close']]=[105.,106.,104.,105.5]
    f.loc[69,['Open','High','Low','Close']]=[103.,104.,99.,102.]
    f.loc[70,['Open','High','Low','Close']]=[102.,107.,101.,106.]
    return f


def watch():
    watches={};ctx={'sweep_date':'2024-01-01','structure_date':'2024-01-02','sweep_level':99.,'structure_level':102.,'zone_low':97.,'zone_high':101.}
    smc_reentry.register_stop(watches,{'symbol':'DEMO','strategy':'SMC','stop':99.,'entry_date':'2024-01-04','smc_context':ctx},'2024-01-05',4,enabled=True)
    return watches


def test_positive_turn_requires_later_bullish_close_and_reclaimed_levels():
    w=watch()['DEMO'];base=dict(Ready=True,Regime='UNCERTAIN',Open=102.,Close=105.,PriorHigh=104.)
    assert not smc_reentry.recovery(Bar(**base),w,4)[0]
    assert smc_reentry.recovery(Bar(**base),w,5)[0]
    for field,value in [('Close',100.),('PriorHigh',106.),('Open',106.),('Regime','HIGH_VOL')]:
        assert not smc_reentry.recovery(Bar(**{**base,field:value}),w,5)[0]
    assert not smc_reentry.recovery(Bar(**base),w,15)[0]
    for status in ['EXHAUSTED','CANCELLED_ADVERSE']:
        assert not smc_reentry.recovery(Bar(**base),{**w,'status':status},5)[0]


@pytest.mark.parametrize('budget',[160,18])
def test_c1_stop_then_fresh_screen_recovery_buy_and_second_stop_exhaustion(completed_c2,budget):
    f=recovery_history();seen=[];c=cfg(f,max_model_calls=budget);rid=create_run(f,c)
    r=execute_run(rid,f,researcher=researcher(completed_c2,seen),preparer=prepare)
    if budget==18:
        assert r['status']=='PAUSED_BUDGET'
        state=load(rid);assert state['smc_reentry_watches']['DEMO']['status']=='WATCHING'
        state['call_limit']=160;save(state_path(rid),state)
        r=execute_run(rid,f,researcher=researcher(completed_c2,seen),preparer=prepare)
    assert r['status'].startswith('COMPLETED'),r
    trades=r['ledgers']['C1'];buys=[t for t in trades if t['event']=='BUY'];stops=[t for t in trades if t['event']=='SELL_STOP']
    assert len(buys)==len(stops)==2,trades
    assert buys[1]['entry_setup']=='SMC_RECOVERY' and buys[1]['smc_reentry']['id']==stops[0]['stop_watch_id']
    assert buys[1]['signal_date']>stops[0]['date'] and buys[1]['date']>buys[1]['signal_date']
    assert buys[1]['research_id']!=buys[0]['research_id']
    screen=next(s for s in seen if s['date']==buys[1]['signal_date'])
    assert screen['research_purpose']=='COMPANY_SCREEN' and screen['approved_candidate']=='NONE' and not screen.get('smc_context')
    assert len({(s['date'],s['research_purpose']) for s in seen})==len(seen)
    assert buys[1]['quantity']<=buys[0]['quantity']
    assert r['smc_reentry_watches'][0]['status']=='EXHAUSTED'
    assert abs(r['accounting']['equity_identity_error'])<1e-7
    from aegistrade.c2_portfolio import frame_for
    frame=frame_for(f,c,{})
    _,events,_=backtest(frame,mode='SMC',p=policy_from_settings(c),automatic_selection=True)
    assert list(events.Event)==[t['event'] for t in trades]
    assert sum(events.EntrySetup=='SMC_RECOVERY')==1


def test_disabled_policy_does_not_reenter_on_recovery_alone(completed_c2):
    f=recovery_history();rid=create_run(f,cfg(f,smc_reentry_enabled=False))
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert sum(t['event']=='BUY' for t in r['ledgers']['C1'])==1
    assert not r['smc_reentry_watches']


def test_adverse_evidence_cancels_recovery_watch(completed_c2):
    f=recovery_history();day=str(f.Date.iloc[67].date())
    def adverse(snapshot,config,**kw):
        out=single_result(completed_c2,snapshot)
        if snapshot['date']==day:
            out['company_assessment'].update(status='REVIEW_REQUIRED',adverse_risk='ADVERSE_EVENT_FOUND',event_risks=['Synthetic contract-test adverse disclosure.'])
        return out
    rid=create_run(f,cfg(f));r=execute_run(rid,f,researcher=adverse,preparer=prepare)
    assert sum(t['event']=='BUY' for t in r['ledgers']['C1'])==1
    assert r['smc_reentry_watches'][0]['status']=='CANCELLED_ADVERSE'


def test_recovery_fill_cannot_forge_its_recorded_stop(completed_c2):
    f=recovery_history();rid=create_run(f,cfg(f));day=str(f.Date.iloc[68].date())
    def pause():
        state=load(rid)
        return state['day_index']<len(state['dates']) and state['dates'][state['day_index']]==day and state['phase']=='OPEN'
    first=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare,should_cancel=pause)
    assert first['status']=='PAUSED_USER'
    state=load(rid);order=next(o for o in state['queued'] if o['side']=='BUY')
    state['smc_reentry_watches']['DEMO']['stop_level']-=1
    order['smc_reentry']['stop_level']-=1 # matching forged watch/order still lacks matching ledger proof
    save(state_path(rid),state)
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert not any(t['event']=='BUY' and t['date']==day for t in r['ledgers']['C1'])
    assert any(d['action']=='FILL_BLOCKED' and d['date']==day for d in r['decisions'])


def test_old_stop_watch_expires_and_cannot_create_watch_for_non_smc():
    w=watch();smc_reentry.expire(w,15)
    assert w['DEMO']['status']=='EXPIRED'
    assert smc_reentry.register_stop({}, {'strategy':'EMA_TREND'},'2024-01-05',4,enabled=True) is None


def test_watch_priority_precedes_price_and_respects_company_screen_limit():
    from aegistrade.c2_portfolio import frame_for
    from aegistrade.smc import screening_candidates
    f=recovery_history();prepared=frame_for(f,cfg(f),{})
    daily=prepared[prepared.Date==f.Date.iloc[67]].copy()
    other=daily.copy();other['Symbol']='OTHER';other['AverageTurnover20']*=2
    daily=pd.concat([daily,other],ignore_index=True)
    audit=screening_candidates(daily,set(),7,limit=1,priority_symbols=['DEMO'])
    assert [r['symbol'] for r in audit if r['selected']]==['DEMO']
    daily['SMCSignal']=False;daily['SMCContext']=None;daily['Regime']='UNCERTAIN'
    assert audit==screening_candidates(daily,set(),7,limit=1,priority_symbols=['DEMO'])


def test_profit_exit_does_not_create_recovery_watch(completed_c2):
    f=smc_history();rid=create_run(f,cfg(f))
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert any(t['event']=='SELL_TAKE_PROFIT' for t in r['ledgers']['C1'])
    assert not r['smc_reentry_watches']


def test_reentry_settings_reject_invalid_windows():
    f=recovery_history()
    for value in [0,31]:
        with pytest.raises(ValueError):cfg(f,smc_reentry_window_sessions=value)


def test_adverse_exit_with_stop_gap_never_opens_eligible_recovery(completed_c2):
    f=recovery_history();f.loc[66,['Open','High','Low','Close']]=[103.,105.,102.,104.]
    f.loc[67,['Open','High','Low','Close']]=[95.,106.,94.,105.]
    day=str(f.Date.iloc[66].date())
    def adverse(snapshot,config,**kw):
        out=single_result(completed_c2,snapshot)
        if snapshot['date']==day and snapshot['research_purpose']=='HOLDING_REVIEW':
            out['company_assessment'].update(status='REVIEW_REQUIRED',adverse_risk='ADVERSE_EVENT_FOUND',event_risks=['Synthetic adverse exit contract.'])
            out['portfolio_action']='EXIT';out['handoffs']['single']['payload']['portfolio_action']='EXIT'
        return out
    rid=create_run(f,cfg(f,take_profit_percent=100,holding_review_sessions=1))
    r=execute_run(rid,f,researcher=adverse,preparer=prepare)
    assert sum(t['event']=='BUY' for t in r['ledgers']['C1'])==1
    assert any(t['event']=='SELL_STOP' and t['research_id'] for t in r['ledgers']['C1'])
    assert r['smc_reentry_watches'][0]['status']=='CANCELLED_ADVERSE'
