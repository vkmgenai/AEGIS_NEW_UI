from datetime import date
import json,hashlib
import pandas as pd
import pytest
from aegistrade.nse_data import normalize_nse_history,fetch_symbol,rank_universe,load_dataset
from aegistrade.selection import rank_candidates,prepare_selection_features
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators


def test_nse_schema_aliases_and_unrelated_symbol():
    raw=pd.DataFrame([{'CH_TIMESTAMP':'2024-01-02','CH_SYMBOL':'ZOMATO','CH_SERIES':'EQ',
        'CH_OPENING_PRICE':100,'CH_TRADE_HIGH_PRICE':102,'CH_TRADE_LOW_PRICE':99,
        'CH_CLOSING_PRICE':101,'CH_TOT_TRADED_QTY':100000}])
    f=normalize_nse_history(raw,'ETERNAL')
    assert f.Symbol.iloc[0]=='ETERNAL' and f.Volume.iloc[0]==100000
    with pytest.raises(ValueError,match='unverified'):normalize_nse_history(raw,'RELIANCE')


def test_chunk_cache_is_resumable_and_requests_are_bounded(tmp_path):
    calls=[]
    def fake(symbol,series,start,end):
        a=pd.to_datetime(start,dayfirst=True);b=pd.to_datetime(end,dayfirst=True)
        assert (b-a).days<40
        calls.append((start,end))
        return pd.DataFrame([{'CH_TIMESTAMP':str(a.date()),'CH_SYMBOL':symbol,'CH_OPENING_PRICE':100,
                              'CH_TRADE_HIGH_PRICE':102,'CH_TRADE_LOW_PRICE':99,'CH_CLOSING_PRICE':101,'CH_TOT_TRADED_QTY':1000}])
    kwargs=dict(fetcher=fake,pause=0)
    f=fetch_symbol('M&M',date(2024,1,1),date(2024,3,1),tmp_path,**kwargs)
    assert len(calls)==2 and len(f)==2
    fetch_symbol('M&M',date(2024,1,1),date(2024,3,1),tmp_path,**kwargs)
    assert len(calls)==2


def test_universe_ranking_never_uses_evaluation_prices():
    f=synthetic_market(n_days=100,symbols=['AAA','BBB'])
    when=f.Date.unique()[70];before=rank_universe(f,pd.Timestamp(when).date(),limit=2)
    f.loc[(f.Symbol=='BBB')&(f.Date>=when),'Volume']=10**15
    assert rank_universe(f,pd.Timestamp(when).date(),limit=2)==before


def test_picker_filters_capital_discontinuities_and_sorts_signals():
    base={'Date':pd.Timestamp('2024-01-02'),'Ready':True,'HistorySessions':100,'Regime':'TREND',
          'RoutedStrategy':'EMA_TREND','Close':110.,'EMA20':100.,'EMA50':90.,'ATR14':2.,'ADX14':30.,
          'RSI14':50.,'Prior20High':115.,'AverageTurnover20':1e9,'RelativeVolume20':1.2,
          'Momentum20':.05,'RecentDiscontinuity':False}
    f=pd.DataFrame([{**base,'Symbol':'AAA'},{**base,'Symbol':'BBB','Momentum20':.10},
                    {**base,'Symbol':'CCC','RecentDiscontinuity':True},
                    {**base,'Symbol':'DDD','Close':10000.}])
    result=rank_candidates(f,equity=1000,cash=1000)
    assert [x['symbol'] for x in result if x['selected']]==['BBB','AAA']
    by={x['symbol']:x for x in result}
    assert 'UNREVIEWED_PRICE_DISCONTINUITY' in by['CCC']['reasons']
    assert 'CAPITAL_OR_RISK_LIMIT' in by['DDD']['reasons']


def test_selection_features_are_causal():
    f=prepare_indicators(synthetic_market(n_days=150))
    when=f.Date.unique()[100]
    full=prepare_selection_features(f);prefix=prepare_selection_features(f[f.Date<=when])
    cols=['Date','Symbol','HistorySessions','AverageTurnover20','RelativeVolume20','Momentum20','RecentDiscontinuity']
    pd.testing.assert_frame_equal(full[full.Date<=when][cols].reset_index(drop=True),prefix[cols].reset_index(drop=True))


def test_empty_shortlist_prevents_model_spend(monkeypatch):
    from aegistrade.research_service import ResearchSettings,execute_research
    import aegistrade.research_service as svc
    f=prepare_indicators(synthetic_market(n_days=150));f['Regime']='HIGH_VOL';f['RoutedStrategy']='NONE'
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY')
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr(svc,'run_research_case',lambda *a,**kw:pytest.fail('No eligible stock must mean no model call'))
    with pytest.raises(ValueError,match='No eligible stock'):
        execute_research(f,ResearchSettings(configuration='C2',automatic_stock_selection=True,consent_to_paid_calls=True),model='unused')


def test_dataset_checksum_and_incomplete_status(tmp_path):
    data=synthetic_market(n_days=10,symbols=['AAA']);data.to_csv(tmp_path/'ohlcv.csv',index=False)
    metadata={'status':'downloading','symbols':['AAA'],'sha256':hashlib.sha256((tmp_path/'ohlcv.csv').read_bytes()).hexdigest()}
    (tmp_path/'manifest.json').write_text(json.dumps(metadata))
    with pytest.raises(ValueError,match='incomplete'):load_dataset(tmp_path)
    metadata['status']='complete';(tmp_path/'manifest.json').write_text(json.dumps(metadata))
    assert len(load_dataset(tmp_path)[0])==10
    (tmp_path/'ohlcv.csv').write_text('tampered')
    with pytest.raises(ValueError,match='checksum'):load_dataset(tmp_path)


def test_backtest_handoff_researches_only_server_saved_selected_stocks(tmp_path,monkeypatch):
    from aegistrade.research_service import ResearchSettings,execute_research
    f=prepare_indicators(synthetic_market(n_days=150,symbols=['AAA','BBB','CCC','DDD','EEE']))
    f['Ready']=True;f['Regime']='TREND';f['RoutedStrategy']='EMA_TREND'
    f['EMA20']=f.Close*.99;f['EMA50']=f.Close*.97;f['ATR14']=f.Close*.02;f['ADX14']=30.;f['RSI14']=50.
    prepared=prepare_selection_features(f);when=prepared.Date.max()
    ranked=rank_candidates(prepared[prepared.Date==when],equity=200000,cash=200000)
    target=[r for r in ranked if r['eligible']][-1]['symbol']
    run='d'*32;folder=tmp_path/'simulation_runs';folder.mkdir()
    (folder/(run+'.json')).write_text(json.dumps({'stock_selection':{'audits':{'ROUTER':[
        {'date':str(when.date()),'symbol':target,'selected':True}]}}}))
    monkeypatch.setenv('AEGIS_DATA_DIR',str(tmp_path))
    result=execute_research(f,ResearchSettings(configuration='C0',automatic_stock_selection=True,
            selection_run_id=run,end_date=when.date(),cases=3),model='unused')
    assert [x['snapshot']['symbol'] for x in result['outputs']]==[target]
    assert result['summary'][0]['model_calls']==0


def test_dataset_activation_is_authenticated_and_validated(tmp_path,monkeypatch):
    from fastapi.testclient import TestClient
    import app.api as api
    monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_frame',None)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','test-dataset-reviewer')
    c=TestClient(api.app);headers={'X-Reviewer-Token':'test-dataset-reviewer'}
    assert c.post('/market/dataset/activate',json={'acknowledge_provisional_data':True}).status_code==403
    assert c.post('/market/dataset/activate',json={'acknowledge_provisional_data':True},headers=headers).status_code==422
    folder=tmp_path/'nse_nifty20';folder.mkdir()
    f=synthetic_market(n_days=100,symbols=['AAA','BBB']);f.to_csv(folder/'ohlcv.csv',index=False)
    metadata={'status':'complete','symbols':['AAA','BBB'],'sha256':hashlib.sha256((folder/'ohlcv.csv').read_bytes()).hexdigest()}
    (folder/'manifest.json').write_text(json.dumps(metadata))
    assert c.post('/market/dataset/activate',json={},headers=headers).status_code==400
    activated=c.post('/market/dataset/activate',json={'acknowledge_provisional_data':True},headers=headers)
    assert activated.status_code==200
    assert c.get('/health').json()['data_source']=='nsepython'
    export=c.get('/market/ohlcv.csv')
    assert export.status_code==200 and export.text.startswith('Date,Symbol,Open,High,Low,Close,Volume')


def test_frozen_universe_cannot_backtest_its_selection_warmup():
    from aegistrade.simulation_service import execute_simulation,SimulationSettings
    f=prepare_indicators(synthetic_market(n_days=150))
    provenance={'requested_start':'2022-04-01','requested_end':'2022-07-29'}
    with pytest.raises(ValueError,match='Warm-up rows'):
        execute_simulation(f,SimulationSettings(start_date='2022-01-03'),source='nsepython',provenance=provenance)
    result=execute_simulation(f,SimulationSettings(mode='ROUTER'),source='nsepython',provenance=provenance)
    assert result['period']['start']>='2022-04-01'
