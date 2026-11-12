"""Configurable initial stops are causal and identical across screening/replay."""
from dataclasses import replace
import math
import pytest
from aegistrade.engine import TradePolicy,allowable_shares,backtest
from aegistrade.execution_policy import initial_stop_price
from aegistrade.simulation_service import SimulationSettings
from aegistrade.c2_portfolio import create_run,execute_run,load
from tests.test_c2_portfolio import history,settings,prepare,runner


def test_stop_formula_and_legacy_default():
    p=TradePolicy()
    assert initial_stop_price(100,2,p)==96
    assert initial_stop_price(100,2,replace(p,atr_stop_multiple=3))==94
    assert initial_stop_price(100,2,replace(p,stop_loss_mode='PERCENT',stop_loss_percent=5))==95
    assert initial_stop_price(100,20,replace(p,stop_loss_mode='PERCENT',stop_loss_percent=5))==95


@pytest.mark.parametrize('changes',[{'stop_loss_mode':'DISABLED'},{'stop_loss_percent':0},{'stop_loss_percent':float('nan')},{'initial_stop_atr_multiple':float('inf')},{'initial_stop_atr_multiple':0}])
def test_invalid_stop_configuration_rejected(changes):
    with pytest.raises(ValueError):SimulationSettings(**changes)


def test_candidate_estimate_uses_selected_stop():
    from aegistrade.selection import prepare_selection_features,rank_candidates
    f=prepare_selection_features(history());day=f[f.Date==f.Date.iloc[60]];bar=day.iloc[0]
    for p in [TradePolicy(atr_stop_multiple=4),TradePolicy(stop_loss_mode='PERCENT',stop_loss_percent=1)]:
        rows=rank_candidates(day,equity=200000,cash=200000,trade_policy=p)
        assert rows[0]['eligible']
        assert rows[0]['estimated_quantity_at_signal_close']==allowable_shares(bar.Close,initial_stop_price(bar.Close,bar.ATR14,p),200000,200000,p)


def test_c2_and_technical_reference_share_percentage_stop_and_fills(completed_c2):
    f=history(68);f.loc[63,['Open','Low']]=[100,99]
    cfg=settings(f,review=60).model_copy(update={'stop_loss_mode':'PERCENT','stop_loss_percent':5.0})
    rid=create_run(f,cfg);out=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    ledger=out['ledgers']['C2'];buy=next(x for x in ledger if x['event']=='BUY')
    assert buy['initial_stop']==pytest.approx(f.Close.iloc[60]*.95)
    c2_stop=next(x for x in ledger if x['event']=='SELL_STOP')
    ref_stop=next(x for x in out['ledgers']['ROUTER'] if x['event']=='SELL_STOP')
    assert c2_stop['date']==ref_stop['date'] and c2_stop['quantity']==ref_stop['quantity']
    assert c2_stop['price']==pytest.approx(ref_stop['price'])
    assert out['initial_stop_loss']['mode']=='PERCENT' and load(rid)['settings']['stop_loss_percent']==5


def test_gap_below_fixed_percentage_stop_blocks_entry(completed_c2):
    f=history(64);f.loc[61,['Open','Low']]=[100,99]
    cfg=settings(f,review=60).model_copy(update={'stop_loss_mode':'PERCENT','stop_loss_percent':5.0})
    rid=create_run(f,cfg);out=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert not any(x['event']=='BUY' and x['date']==str(f.Date.iloc[61].date()) for x in out['ledgers']['C2'])


def test_larger_atr_initial_stop_is_used_before_trailing(completed_c2):
    f=history(65);cfg=settings(f,review=60).model_copy(update={'initial_stop_atr_multiple':3.0})
    rid=create_run(f,cfg);out=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    buy=next(x for x in out['ledgers']['C2'] if x['event']=='BUY')
    assert buy['initial_stop']==pytest.approx(f.Close.iloc[60]-3*f.ATR14.iloc[60])
    assert out['initial_stop_loss']['atr_multiple']==3
