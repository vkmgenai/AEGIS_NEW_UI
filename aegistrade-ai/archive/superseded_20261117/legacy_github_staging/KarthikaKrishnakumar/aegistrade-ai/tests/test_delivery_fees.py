import pytest
from pydantic import ValidationError
from aegistrade.fees import BUY_FEE_BPS, SELL_FEE_BPS, charge_breakdown
from aegistrade.engine import TradePolicy, allowable_shares
from aegistrade.simulation_service import SimulationSettings


def test_screenshot_components_and_side_specific_stamp():
    buy=charge_breakdown(100000,'BUY');sell=charge_breakdown(100000,'SELL')
    assert buy==pytest.approx(dict(brokerage=0,stt=100,stamp_duty=15,exchange=3.07,sebi=.10,gst=.5706,total=118.7406))
    assert sell['total']==pytest.approx(103.7406)
    assert BUY_FEE_BPS==pytest.approx(11.87406)
    assert SELL_FEE_BPS==pytest.approx(10.37406)


def test_fee_override_rejected_and_sizing_accounts_for_buy_cost():
    with pytest.raises(ValidationError):SimulationSettings(fee_bps=0)
    with pytest.raises(TypeError):TradePolicy(fee_bps=0)
    p=TradePolicy(max_position_fraction=1,risk_per_trade=1)
    qty=allowable_shares(100,90,1000,1000,p)
    assert qty==9
    assert qty*100+charge_breakdown(qty*100,'BUY')['total']<=1000
