"""Separate immutable universes, safe activation and original-data resume."""
from pathlib import Path
from datetime import date
from concurrent.futures import Future
import hashlib,json
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from aegistrade import universes as u,nse_data as n,dataset_jobs as jobs
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators


def dataset(root,key,symbols=None):
    directory=root/u.PROFILES[key]['directory'];directory.mkdir(parents=True,exist_ok=True)
    symbols=symbols or (u.curated_members().Symbol.tolist() if key=='research30' else u.official_members()[0].Symbol.tolist() if key=='nifty100' else ['RELIANCE','INFY'])
    frame=synthetic_market(n_days=100,symbols=symbols);file=directory/'ohlcv.csv';frame.to_csv(file,index=False)
    manifest={'status':'complete','symbols':symbols,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'universe_id':key,'definition_sha256':u.definition_hash(key),'requested_start':'2022-01-03','requested_end':str(frame.Date.max().date()),'warmup_start':'2021-08-01'}
    (directory/'manifest.json').write_text(json.dumps(manifest));return directory,manifest,frame


def test_frozen_definitions_have_exact_members_and_dated_official_sources():
    members=u.curated_members();assert len(members)==30
    assert members.ResearchGroup.value_counts().to_dict()=={'established':21,'cyclical':6,'event_research':3}
    official,meta=u.official_members();assert len(official)==100 and meta['snapshot_date']=='2026-11-12'
    assert {'YESBANK','IDEA','ZEEL'}==set(members[members.ResearchGroup=='event_research'].Symbol)
    with pytest.raises(ValueError):u.profile('../arbitrary-folder')


def test_authenticated_switch_preserves_original_dataset_and_can_switch_back(tmp_path,monkeypatch):
    import app.api as api
    old,old_meta,_=dataset(tmp_path,'nifty20');new,_,_=dataset(tmp_path,'research30')
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','universe-review-token')
    client=TestClient(api.app);headers={'X-Reviewer-Token':'universe-review-token'}
    body={'universe_id':'research30','acknowledge_provisional_data':True}
    assert client.post('/market/dataset/activate',json=body).status_code==403
    result=client.post('/market/dataset/activate',json=body,headers=headers)
    assert result.status_code==200 and result.json()['symbols']==30
    assert len(client.get('/market/universe').json()['symbols'])==30
    assert client.get('/market/universe').json()['provenance']['universe_id']=='research30'
    rows=client.get('/market/datasets').json()['datasets']
    assert len(rows)==3 and next(r for r in rows if r['id']=='research30')['active']
    assert hashlib.sha256((old/'ohlcv.csv').read_bytes()).hexdigest()==old_meta['sha256']
    back=client.post('/market/dataset/activate',json={**body,'universe_id':'nifty20'},headers=headers)
    assert back.status_code==200 and len(client.get('/market/universe').json()['symbols'])==2
    assert client.get('/market/dataset?universe_id=research30').json()['active'] is False


def test_unprepared_or_mislabelled_universe_cannot_be_activated(tmp_path,monkeypatch):
    import app.api as api
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','universe-review-token');c=TestClient(api.app);headers={'X-Reviewer-Token':'universe-review-token'}
    assert c.get('/market/dataset?universe_id=../../bad').status_code==422
    body={'universe_id':'research30','acknowledge_provisional_data':True}
    assert c.post('/market/dataset/activate',json=body,headers=headers).status_code==422
    dataset(tmp_path,'research30',symbols=['FAKE'])
    assert c.post('/market/dataset/activate',json=body,headers=headers).status_code==422
    assert not (tmp_path/'market_config.json').exists()


def test_saved_c2_resolves_original_universe_after_switch(tmp_path,monkeypatch):
    import app.api as api
    from aegistrade.c2_portfolio import C2PortfolioSettings,create_run,frame_for,fingerprint
    old,meta,raw=dataset(tmp_path,'nifty20');dataset(tmp_path,'research30')
    raw,_=n.load_dataset(old)
    f=prepare_indicators(raw);cfg=C2PortfolioSettings(start_date=f.Date.iloc[-20].date(),end_date=f.Date.iloc[-1].date(),consent_to_paid_calls=True,approve_historical_rules=True)
    rid=create_run(f,cfg,source='nsepython',provenance=meta)
    (tmp_path/'market_config.json').write_text(json.dumps({'source':'nsepython','universe_id':'research30','dataset_dir':'nse_research30','legacy_dataset_dir':'nse_nifty20'}))
    original=api.frame_for_saved_portfolio(rid)
    assert set(original.Symbol)==set(raw.Symbol)
    assert fingerprint(frame_for(original,cfg,meta))==fingerprint(frame_for(f,cfg,meta))
    (old/'ohlcv.csv').write_text('changed')
    with pytest.raises(ValueError,match='checksum'):api.frame_for_saved_portfolio(rid)


class Immediate:
    def submit(self,fn,*args):
        future=Future()
        try:future.set_result(fn(*args))
        except BaseException as exc:future.set_exception(exc)
        return future


def test_public_preparation_reuses_history_and_does_not_activate(tmp_path,monkeypatch):
    old,old_meta,old_frame=dataset(tmp_path,'nifty20');original=(old/'ohlcv.csv').read_bytes();calls=[]
    def fake(symbol,start,end,cache_dir,**kw):
        calls.append(symbol)
        return synthetic_market(n_days=100,symbols=[symbol])
    monkeypatch.setattr(n,'fetch_symbol',fake);monkeypatch.setattr(jobs,'_executor',Immediate())
    jobs.prepare(tmp_path,'research30',date(2022,1,3),date(2022,5,20))
    state=jobs.status(tmp_path,'research30');assert state['status']=='COMPLETE',state
    data,manifest=n.load_dataset(tmp_path/'nse_research30')
    assert len(manifest['symbols'])==30 and len(data.Symbol.unique())==30
    assert {'RELIANCE','INFY'}.issubset({r['symbol'] for r in manifest['reused_symbols']})
    assert 'RELIANCE' not in calls and 'INFY' not in calls
    assert not (tmp_path/'market_config.json').exists() and (old/'ohlcv.csv').read_bytes()==original


def test_failed_public_preparation_stays_unavailable_and_records_no_generation(tmp_path,monkeypatch):
    def fail(*args,**kwargs):raise RuntimeError('Public archive unavailable')
    monkeypatch.setattr(n,'fetch_symbol',fail);monkeypatch.setattr(jobs,'_executor',Immediate())
    jobs.prepare(tmp_path,'research30',date(2022,1,3),date(2022,5,20))
    status=jobs.status(tmp_path,'research30');assert status['status']=='FAILED' and status['generation_calls']==0
    assert not (tmp_path/'market_config.json').exists()
    with pytest.raises(ValueError):n.load_dataset(tmp_path/'nse_research30')


def test_new_listings_are_retained_with_disclosed_shorter_history(tmp_path,monkeypatch):
    members=tmp_path/'members.csv';pd.DataFrame({'Symbol':['AAA','BBB']}).to_csv(members,index=False)
    def fake(symbol,start,end,cache_dir,**kwargs):
        start=max(start,date(2024,2,1)) if symbol=='BBB' else start
        dates=pd.bdate_range(start,end)
        return pd.DataFrame({'Date':dates,'Symbol':symbol,'Open':100,'High':102,'Low':99,'Close':101,'Volume':100000})
    monkeypatch.setattr(n,'fetch_symbol',fake)
    manifest=n.build_dataset(tmp_path/'new',date(2024,1,1),date(2024,3,1),selection_mode='all_members',universe_id='nifty100',constituent_path=members)
    frame,_=n.load_dataset(tmp_path/'new')
    assert set(frame.Symbol)=={'AAA','BBB'} and manifest['coverage_policy']=='observed_listing_span'
    assert frame[frame.Symbol=='BBB'].Date.min()==pd.Timestamp('2024-02-01')


def test_official_symbol_intervals_and_new_listing_start():
    from aegistrade.security_identity import segments
    assert [x[0] for x in segments('LTM',date(2021,1,1),date(2026,10,1))]==['LTI','LTIM','LTM']
    assert segments('HYUNDAI',date(2021,1,1),date(2026,10,1))[0][1]==date(2024,10,22)


def test_history_requests_verified_predecessor_and_normalizes_identifier(tmp_path):
    from aegistrade.security_identity import segments
    calls=[]
    def fake(symbol,series,start,end):
        calls.append(symbol);d=pd.to_datetime(start,dayfirst=True)
        return pd.DataFrame([{'CH_TIMESTAMP':str(d.date()),'CH_SYMBOL':symbol,'CH_SERIES':'EQ','CH_OPENING_PRICE':100,'CH_TRADE_HIGH_PRICE':102,'CH_TRADE_LOW_PRICE':99,'CH_CLOSING_PRICE':101,'CH_TOT_TRADED_QTY':1000}])
    f=n.fetch_symbol('ADANIENSOL',date(2023,8,22),date(2023,8,25),tmp_path,fetcher=fake,pause=0,identity=True)
    assert calls==['ADANITRANS','ADANIENSOL'] and set(f.Symbol)=={'ADANIENSOL'} and len(f)==2


def test_ui_selects_and_activates_prepared_universe_without_generation(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from urllib.parse import urlsplit
    from streamlit.testing.v1 import AppTest
    import requests,app.api as api
    dataset(tmp_path,'nifty20');dataset(tmp_path,'research30')
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','universe-ui-reviewer');client=TestClient(api.app);writes=[]
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        parsed=urlsplit(url);return adapt(client.get(parsed.path+('?' +parsed.query if parsed.query else '')))
    def post(url,json=None,headers=None,**kw):
        parsed=urlsplit(url);writes.append((parsed.path,json));return adapt(client.post(parsed.path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app/ui.py',default_timeout=30).run()
    assert at.selectbox(key='market_universe_choice').options==[u.profile(k)['name'] for k in u.PROFILES]
    at.selectbox(key='market_universe_choice').select('research30').run()
    next(x for x in at.checkbox if x.label.startswith('Use this provisional')).check().run()
    next(x for x in at.button if x.label=='Use downloaded NSE data').click().run()
    assert not at.exception
    assert len(client.get('/market/universe').json()['symbols'])==30
    assert writes==[('/market/dataset/activate',{'acknowledge_provisional_data':True,'universe_id':'research30'})]


def test_ui_unprepared_profile_has_protected_preparation_control(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from urllib.parse import urlsplit
    from streamlit.testing.v1 import AppTest
    import requests,app.api as api
    client=TestClient(api.app)
    def get(url,**kw):
        parsed=urlsplit(url);r=client.get(parsed.path+('?' +parsed.query if parsed.query else ''))
        return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    monkeypatch.setattr(requests,'get',get)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app/ui.py',default_timeout=30).run()
    at.selectbox(key='market_universe_choice').select('nifty100').run()
    assert not at.exception
    assert next(x for x in at.button if x.label=='Prepare selected universe').disabled
    assert not any(x.label=='Use downloaded NSE data' for x in at.button)
