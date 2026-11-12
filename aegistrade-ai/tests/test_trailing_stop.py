"""Causal trailing exits and checkpoint behavior. No genuine model calls."""
import copy,math
import pandas as pd
import pytest
from aegistrade.trailing_stop import advance_trailing_stop,stop_exit_reason
from aegistrade.engine import backtest,TradePolicy
from aegistrade.c2_portfolio import create_run,execute_run,load
from tests.test_c2_portfolio import history,settings,prepare,runner


def rising_then_gap():
    f=history(64)
    f.loc[61,['Open','High','Low','Close','ATR14']]=[110.,130.,108.,120.,12.]
    f.loc[62,['Open','High','Low','Close','ATR14']]=[122.,126.,119.,123.,20.]
    f.loc[63,['Open','High','Low','Close']]=[118.,120.,115.,117.]
    return f


def test_stop_ratchets_without_widening_and_is_idempotent():
    pos={'stop':90.,'initial_stop':90.,'entry_signal_atr':5.,'highest_close':None}
    changes=[]
    for day,close in [('1',100.),('2',120.),('3',115.),('4',118.),('5',125.)]:
        update=advance_trailing_stop(pos,close,day)
        if update:changes.append(update['new_stop'])
    assert changes==[110.,115.] and pos['highest_close']==125.
    before=copy.deepcopy(pos)
    assert advance_trailing_stop(pos,125.,'5') is None and pos==before
    assert stop_exit_reason(pos)=='SELL_TRAILING_STOP'


@pytest.mark.parametrize('bad',[0,-1,float('nan'),float('inf')])
def test_invalid_input_does_not_mutate_protection(bad):
    pos={'stop':90.,'entry_signal_atr':5.};before=pos.copy()
    with pytest.raises(ValueError):advance_trailing_stop(pos,bad,'day')
    assert pos==before


def test_c2_trail_uses_signal_atr_and_only_triggers_next_session(completed_c2):
    f=rising_then_gap();rid=create_run(f,settings(f,review=60,trailing=True))
    seen=[];result=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    assert result['status']=='COMPLETED'
    buy,sell=result['ledgers']['C2']
    assert buy['event']=='BUY' and buy['date']==str(f.Date.iloc[61].date())
    # The fill day's low108 is below the newly computed116 stop; it must survive.
    assert sell['date']==str(f.Date.iloc[63].date()) and sell['event']=='SELL_TRAILING_STOP'
    assert sell['price']==pytest.approx(118*.999)  # Gap: cannot guarantee119.
    assert sell['stop_price']==119 and sell['initial_stop']==pytest.approx(103.)
    assert [u['new_stop'] for u in result['stop_updates']]==[116.,119.]
    assert all(u['entry_signal_atr']==2. for u in result['stop_updates'])
    assert len(seen)==1 and result['model_usage']['attempted_calls']==6
    assert abs(result['accounting']['equity_identity_error'])<1e-7


def test_disabled_trailing_keeps_initial_stop(completed_c2):
    f=rising_then_gap();rid=create_run(f,settings(f,review=60,trailing=False))
    result=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert not result['stop_updates'] and len(result['open_holdings'])==1
    assert result['open_holdings'][0]['stop']==103.
    assert not any(e['event'].startswith('SELL') for e in result['ledgers']['C2'])


def test_technical_engine_matches_c2_stop_timing():
    f=rising_then_gap().iloc[60:].copy()
    curve,events,_=backtest(f,p=TradePolicy(initial_cash=200000,trailing_stop_enabled=True),automatic_selection=False)
    sold=events[events.Event=='SELL_TRAILING_STOP'].iloc[0]
    assert sold.Date==f.Date.iloc[-1] and sold.Price==pytest.approx(118*.999)
    assert [u['new_stop'] for u in curve.attrs['stop_updates']]==[116.,119.]


def test_final_close_can_raise_stop_without_forced_sale(completed_c2):
    f=rising_then_gap().iloc[:-1].copy();rid=create_run(f,settings(f,review=60,trailing=True))
    result=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert len(result['open_holdings'])==1 and result['open_holdings'][0]['stop']==119.
    assert result['stop_updates'][-1]['effective_after_close']==str(f.Date.iloc[-1].date())
    assert result['accounting']['forced_end_liquidation'] is False


def test_close_pause_resume_does_not_repeat_stop_updates_or_fills(completed_c2):
    f=rising_then_gap();rid=create_run(f,settings(f,review=1,trailing=True));seen=[]
    paused=False
    def cancel_after_second_ratchet():
        nonlocal paused
        if not paused and len(load(rid)['stop_updates'])>=2:
            paused=True;return True
        return False
    first=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare,should_cancel=cancel_after_second_ratchet)
    assert first['status']=='PAUSED_USER' and len(first['stop_updates'])==2
    assert first['open_holdings'][0]['stop']==119.
    final=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    assert final['status']=='COMPLETED' and len(final['stop_updates'])==2
    assert [e['event'] for e in final['ledgers']['C2']]==['BUY','SELL_TRAILING_STOP']
    assert len(seen)==2 and abs(final['accounting']['equity_identity_error'])<1e-7


def test_missing_bar_does_not_advance_stop(completed_c2):
    f=rising_then_gap();other=f.copy();other['Symbol']='OTHER';other['Volume']=1
    f=pd.concat([f.drop(index=62),other],ignore_index=True)
    from aegistrade.c2_portfolio import C2PortfolioSettings
    original=rising_then_gap()
    cfg=C2PortfolioSettings(start_date=original.Date.iloc[60].date(),end_date=original.Date.iloc[63].date(),
        max_model_calls=80,holding_review_sessions=60,take_profit_percent=0,review_after_gap=False,trailing_stop_enabled=True,consent_to_paid_calls=True,approve_historical_rules=True)
    rid=create_run(f,cfg);result=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert [u['new_stop'] for u in result['stop_updates']]==[116.]
    sold=next(e for e in result['ledgers']['C2'] if e['event']=='SELL_TRAILING_STOP')
    assert sold['price']==pytest.approx(116*.999)


def test_old_engine_run_cannot_resume_with_changed_stop_rules():
    from aegistrade.c2_portfolio import save,state_path,resume
    f=rising_then_gap();rid=create_run(f,settings(f,trailing=True))
    state=load(rid);state['version']='c2-portfolio-v1';state['status']='PAUSED_USER';save(state_path(rid),state)
    with pytest.raises(ValueError,match='changed'):execute_run(rid,f)
    with pytest.raises(ValueError,match='exit-policy'):resume(rid,f,0)


def test_new_simulation_defaults_enable_trailing_and_reject_bad_distance():
    from aegistrade.simulation_service import SimulationSettings
    from pydantic import ValidationError
    assert SimulationSettings().trailing_stop_enabled and SimulationSettings().trailing_atr_multiple==2.
    for bad in [0,float('nan'),float('inf')]:
        with pytest.raises(ValidationError):SimulationSettings(trailing_atr_multiple=bad)
