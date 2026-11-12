"""Stop/rebound contracts: mocked C2 only, no provider requests."""
from types import SimpleNamespace as Row
import pandas as pd
import pytest
from aegistrade.breakout_reentry import register_breakout_stop,reentry_candidates
from aegistrade.strategies import pullback_entry,exit_signal,prepare_indicators
from aegistrade.trailing_stop import advance_trailing_stop
from aegistrade.engine import TradePolicy,backtest,allowable_shares
from aegistrade.execution_policy import policy_for_strategy,initial_stop_price
from aegistrade.simulation_service import SimulationSettings,policy_from_settings
from tests.test_c2_portfolio import history,settings,runner
from tests.company_fixtures import BreakoutArchive
from aegistrade.company_research import prepare_company_research

def prepare(symbol,day):return prepare_company_research(symbol,day,provider=BreakoutArchive())
from aegistrade.c2_portfolio import create_run,execute_run,load,save,state_path


def watch():
    w={};register_breakout_stop(w,{'symbol':'DEMO','strategy':'BREAKOUT','stop':101.,'entry_date':'2024-01-01'},'2024-01-04',3)
    return w


def candidate(**kw):
    return pd.DataFrame([dict(Symbol='DEMO',Ready=True,Regime='TREND',RoutedStrategy='EMA_TREND',ADX14=25.,Close=105.,EMA20=103.,PriorHigh=104.,**kw)])


def test_bounce_requires_later_close_and_expires():
    w=watch();assert reentry_candidates(candidate(),w,3).iloc[0].RoutedStrategy=='NONE'
    assert reentry_candidates(candidate(),w,4).iloc[0].Regime=='BREAKOUT_BOUNCE'
    for field,value in [('Close',101.),('ADX14',17.),('PriorHigh',106.),('Regime','HIGH_VOL')]:
        f=candidate();f[field]=value
        assert reentry_candidates(f,w,4).iloc[0].RoutedStrategy=='NONE'
    assert reentry_candidates(candidate(),w,13).iloc[0].Regime=='BREAKOUT_BOUNCE'
    assert reentry_candidates(candidate(),w,14).iloc[0].Regime=='TREND' and not w


def test_second_stop_exhausts_and_other_strategies_do_not_register():
    w=watch();w['DEMO']['status']='CANCELLED_ADVERSE'
    assert reentry_candidates(candidate(),w,4).iloc[0].RoutedStrategy=='NONE'
    register_breakout_stop(w,{'symbol':'DEMO','strategy':'BREAKOUT','stop':102.,'entry_date':'2024-01-05','breakout_reentry_count':1},'2024-01-08',5)
    assert w['DEMO']['status']=='EXHAUSTED'
    assert reentry_candidates(candidate(),w,6).iloc[0].RoutedStrategy=='NONE'
    w={};register_breakout_stop(w,{'symbol':'DEMO','strategy':'EMA_TREND'},'2024-01-04',3)
    assert not w


def test_separate_risk_and_atr_sizing_and_percent_override():
    p=TradePolicy();b=policy_for_strategy(p,'BREAKOUT')
    assert b.risk_per_trade==.005 and initial_stop_price(100,2,b)==95
    assert initial_stop_price(100,2,p)==96
    q=allowable_shares(100,95,200000,200000,b)
    assert q*5<=1000
    b=policy_for_strategy(policy_from_settings(SimulationSettings(breakout_stop_loss_mode='PERCENT',breakout_stop_loss_percent=7)),'BREAKOUT')
    assert initial_stop_price(100,2,b)==93
    with pytest.raises(ValueError):SimulationSettings(breakout_risk_percent=float('nan'))


def test_trailing_waits_original_one_r_and_never_lowers():
    p={'entry_price':100.,'entry_signal_atr':2.,'initial_stop':95.,'stop':95.}
    assert advance_trailing_stop(p,104,'2024-01-02',2.5,activation_r=1) is None
    assert p['stop']==95 and not p['trailing_activated']
    update=advance_trailing_stop(p,105,'2024-01-03',2.5,activation_r=1)
    assert update['new_stop']==100 and update['effective_after_close']=='2024-01-03'
    assert advance_trailing_stop(p,110,'2024-01-03',2.5,activation_r=1) is None
    advance_trailing_stop(p,103,'2024-01-04',2.5,activation_r=1)
    assert p['stop']==100


def test_pullback_requires_rebound_and_causal_indicators():
    base=dict(PullbackRecent=True,ADX14=25.,EMA20=100.,EMA50=95.,Close=103.,PriorHigh=102.,Ready=True)
    assert pullback_entry(Row(**base))
    for field,value in [('PullbackRecent',False),('Close',101.),('ADX14',21.)]:
        assert not pullback_entry(Row(**{**base,field:value}))
    assert exit_signal(Row(**{**base,'EMA20':94.}),'EMA_PULLBACK')
    from aegistrade.market import synthetic_market
    raw=synthetic_market(n_days=120);cut=raw.Date.sort_values().unique()[89]
    a=prepare_indicators(raw);b=prepare_indicators(raw[raw.Date<=cut])
    pd.testing.assert_frame_equal(a[a.Date<=cut].reset_index(drop=True),b.reset_index(drop=True))


def rebound_history():
    f=history(69);f['PriorHigh']=f.High.shift(1);f['PullbackRecent']=False
    f['Regime']='BREAKOUT';f['RoutedStrategy']='BREAKOUT';f['Prior20High']=90.
    # First signal 107 -> stop 102. Later stop session closes back above level,
    # but only the following session's confirming close is eligible.
    f.loc[62,['Open','High','Low','Close']]=[108.,110.,100.,109.]
    f.loc[63,['Open','High','Low','Close','PriorHigh']]=[109.,112.,108.,111.,110.]
    f.loc[64:,['Open','High','Low','Close']]=[112.,114.,110.,113.]
    f.loc[65,['Open','High','Low','Close']]=[110.,112.,100.,111.]  # second stop, no third buy
    return f


@pytest.mark.parametrize('budget',[80,8])
def test_c2_and_reference_stop_then_fresh_research_later_open(completed_c2,budget):
    f=rebound_history();seen=[];cfg=settings(f,review=60,budget=budget)
    rid=create_run(f,cfg)
    result=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    if budget==8:
        assert result['status']=='PAUSED_BUDGET'
        state=load(rid);assert state['breakout_reentry_watches']['DEMO']['status']=='WATCHING'
        state['call_limit']=80;save(state_path(rid),state)
        result=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    assert len({(s['date'],s['research_purpose']) for s in seen})==len(seen)
    assert result['status'].startswith('COMPLETED'),result
    ledger=result['ledgers']['C2'];buys=[x for x in ledger if x['event']=='BUY']
    stops=[x for x in ledger if x['event']=='SELL_STOP']
    assert len(buys)==2 and len(stops)==2, [d.get("errors") for d in result["decisions"]]
    bounce=next(s for s in seen if s['regime']=='BREAKOUT_BOUNCE')
    assert bounce['date']>stops[0]['date'] and buys[1]['date']>bounce['date']
    assert buys[1]['entry_setup']=='BREAKOUT_BOUNCE'
    assert buys[0]['research_id']!=buys[1]['research_id']
    assert buys[1]['risk_percent_used']==.5
    assert abs(result['accounting']['equity_identity_error'])<1e-7
    assert any(w['status']=='EXHAUSTED' for w in result['breakout_reentry_watches'])
    _,events,_=backtest(f[f.Date>=cfg.start_date.isoformat()],p=policy_from_settings(cfg))
    assert len(events[events.Event=='BUY'])==2
    # A bounce cannot pass C2 by omitting the normal breakout source quote.
    from aegistrade.research_gate import validate_completed_c2
    invalid=completed_c2(bounce);invalid['handoffs']['critic']['payload'].pop('breakout_evidence')
    with pytest.raises(ValueError):validate_completed_c2(invalid)


def test_pullback_typed_c2_route_and_confirmation_proof(completed_c2):
    from tests.test_signal_evidence import TREND
    from aegistrade.research_gate import validate_completed_c2
    from aegistrade.agent_tools import CaseEvidence
    snapshot={**TREND,'regime':'PULLBACK','approved_candidate':'EMA_PULLBACK',
              'Close':105.,'EMA20':100.,'EMA50':95.,'ADX14':25.,'PriorHigh':104.,'PullbackRecent':True}
    assert validate_completed_c2(completed_c2(snapshot))['strategy']=='EMA_PULLBACK'
    with pytest.raises(ValueError):CaseEvidence.from_snapshot({**snapshot,'PullbackRecent':False})
    with pytest.raises(ValueError):CaseEvidence.from_snapshot({**snapshot,'PriorHigh':106.})
