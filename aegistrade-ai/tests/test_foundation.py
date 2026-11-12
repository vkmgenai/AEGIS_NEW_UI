import math
import pandas as pd
import pytest
from aegistrade.market import synthetic_market,validate_ohlcv
from aegistrade.strategies import prepare_indicators
from aegistrade.engine import backtest,allowable_shares,TradePolicy


def test_data_validated_and_duplicate_rejected():
    df=synthetic_market(n_days=100)
    assert df.groupby("Symbol").size().min()==100
    with pytest.raises(ValueError,match="Duplicate"):
        validate_ohlcv(pd.concat([df,df.iloc[:1]],ignore_index=True))


def test_no_lookahead_next_session_entry():
    df=prepare_indicators(synthetic_market())
    eq,events,metrics=backtest(df)
    assert len(eq)>100
    assert not events.empty
    buys=events[events.Event=="BUY"]
    # Our engine generates at completed close; first signals can never enter on very first bar.
    assert buys.Date.min()>df.Date.min()
    assert (eq.Cash>=-1e-6).all()
    assert (eq.Positions<=4).all()


def test_position_size_respects_risk_cash_exposure():
    p=TradePolicy()
    qty=allowable_shares(100,90,5000,100000,p)
    assert qty==49  # fees restrict cash: floor(5000/100.1)
    assert qty*(100-90)<=1000
    assert qty*100<=20000


def test_fill_uses_next_open_not_signal_close():
    from aegistrade.engine import backtest
    dates=pd.bdate_range("2025-01-06", periods=3)
    d=pd.DataFrame({
        "Date":dates,"Symbol":["TEST"]*3,
        "Open":[100.,120.,125.],"High":[105.,125.,131.],"Low":[99.,116.,120.],"Close":[104.,123.,128.],
        "Volume":[1_000_000]*3,"Ready":[True]*3,"EMA20":[102.,110.,117.],
        "EMA50":[100.,102.,105.],"ATR14":[5.,5.,5.],"ADX14":[25.,25.,25.],
        "RSI14":[60.,65.,63.],"Prior20High":[101.,110.,125.],
        "RealizedVol20":[.2]*3,"Regime":["TREND"]*3,"RoutedStrategy":["EMA_TREND"]*3
    })
    curve,events,metrics=backtest(d,"ROUTER",TradePolicy())
    buys=events.loc[events.Event=="BUY"]
    assert len(buys)==1
    assert buys.iloc[0].Date==dates[1]
    assert buys.iloc[0].Price==pytest.approx(120*(1+10/10000))
