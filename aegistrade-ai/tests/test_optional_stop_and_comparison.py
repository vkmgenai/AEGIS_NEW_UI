from datetime import date
from types import SimpleNamespace

import pytest

from aegistrade.engine import TradePolicy, allowable_shares
from aegistrade.execution_policy import initial_stop_price, protective_exit
from aegistrade.simulation_service import SimulationSettings


def test_disabled_stop_uses_exposure_sizing_and_never_triggers_protective_sale():
    policy=TradePolicy(stop_loss_enabled=False,max_position_fraction=.2,risk_per_trade=.001)
    assert initial_stop_price(100,5,policy)==0
    assert allowable_shares(100,0,100_000,100_000,policy)==200
    position={'quantity':200,'entry_price':100,'entry_fee':10,'stop':0,'initial_stop':0}
    assert protective_exit(position,SimpleNamespace(Open=50,Low=1,High=101),policy) is None


def test_disabled_stop_rejects_trailing_and_recovery_settings():
    with pytest.raises(ValueError,match='require protective stop loss'):
        SimulationSettings(stop_loss_enabled=False,trailing_stop_enabled=True)
    settings=SimulationSettings(stop_loss_enabled=False,trailing_stop_enabled=False,
        breakout_reentry_enabled=False,smc_reentry_enabled=False)
    assert settings.stop_loss_enabled is False


def test_disabled_stop_still_allows_a_technical_entry():
    import pandas as pd
    from aegistrade.engine import backtest
    dates=pd.bdate_range('2025-01-06',periods=3)
    frame=pd.DataFrame({'Date':dates,'Symbol':['TEST']*3,'Open':[100.,101.,102.],'High':[102.,103.,104.],
        'Low':[95.,1.,100.],'Close':[101.,102.,103.],'Volume':[1_000_000]*3,'Ready':[True]*3,
        'EMA20':[100.]*3,'EMA50':[95.]*3,'ATR14':[5.]*3,'ADX14':[25.]*3,'RSI14':[60.]*3,
        'Prior20High':[99.,101.,102.],'RealizedVol20':[.2]*3,'Regime':['TREND']*3,'RoutedStrategy':['EMA_TREND']*3})
    policy=TradePolicy(stop_loss_enabled=False,trailing_stop_enabled=False,breakout_reentry_enabled=False,smc_reentry_enabled=False)
    _,events,_=backtest(frame,'ROUTER',policy)
    assert list(events.Event)==['BUY'] and events.iloc[0].InitialStop==0


def test_comparison_aggregates_c0_c1_c2_without_claiming_pure_ablation(monkeypatch,tmp_path):
    import aegistrade.portfolio_comparison as comparison
    from tests.test_c1_smc_portfolio import smc_history
    monkeypatch.setenv('AEGIS_DATA_DIR',str(tmp_path))
    launched=[]
    monkeypatch.setattr(comparison,'launch',lambda run_id,frame:launched.append(run_id))
    children={}
    def fake_create(frame,settings,**kwargs):
        run_id=('1' if settings.research_flow=='C1' else '2')*32;children[run_id]=settings.research_flow;return run_id
    monkeypatch.setattr(comparison,'create_run',fake_create)
    monkeypatch.setattr(comparison,'child_status',lambda run_id:{'run_id':run_id,'research_flow':children[run_id],
        'status':'QUEUED','metrics':[{'ending_equity':200000,'total_return_pct':0}],
        'curves':{children[run_id]:[]},'ledgers':{children[run_id]:[]},'model_usage':{},'progress':{},'worker_active':True})
    frame=smc_history();start=frame.Date.iloc[0].date();end=frame.Date.iloc[-1].date()
    settings=comparison.ComparisonSettings(symbol='DEMO',start_date=start,end_date=end,
        consent_to_paid_calls=True,approve_historical_rules=True)
    result=comparison.create(frame,settings)
    assert set(result['flows'])=={'C0','C1','C2'} and result['status']=='RUNNING'
    assert result['flows']['C0']['model_usage']['attempted_calls']==0
    assert 'not a pure agent-architecture ablation' in result['comparison_design']['interpretation']
    assert len(launched)==2


def test_comparison_api_requires_auth_and_returns_coordinated_result(monkeypatch):
    from fastapi.testclient import TestClient
    import app.api as api
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','comparison-reviewer-token')
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr(api,'require_backend_ready',lambda:None)
    monkeypatch.setattr(api,'market_snapshot_context',lambda:('FRAME','test',{}))
    expected={'run_id':'a'*32,'status':'RUNNING','flows':{'C0':{},'C1':{},'C2':{}}}
    import aegistrade.portfolio_comparison as comparison
    monkeypatch.setattr(comparison,'create',lambda *args,**kwargs:expected)
    body={'symbol':'RELIANCE','start_date':'2024-01-01','end_date':'2024-06-30',
          'consent_to_paid_calls':True,'approve_historical_rules':True}
    client=TestClient(api.app)
    assert client.post('/research/portfolio-comparison/run',json=body).status_code==403
    response=client.post('/research/portfolio-comparison/run',json=body,headers={'x-reviewer-token':'comparison-reviewer-token'})
    assert response.status_code==200 and set(response.json()['flows'])=={'C0','C1','C2'}
