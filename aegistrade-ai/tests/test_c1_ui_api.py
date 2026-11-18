from types import SimpleNamespace
from pathlib import Path
from urllib.parse import urlsplit
import json
import pytest
from fastapi.testclient import TestClient
from tests.test_c1_smc_portfolio import smc_history,cfg


def test_c1_portfolio_is_hidden_from_new_run_ui_but_evaluation_baseline_remains(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    import app.api as api
    import requests
    monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_frame',smc_history())
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c1-portfolio-contract-token')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY');monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    client=TestClient(api.app)
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    monkeypatch.setattr(requests,'get',get)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    assert not any(x.key=='simulation_engine' for x in at.radio)
    assert not any(x.label=='Stock to compare' for x in at.selectbox)
    assert any(x.label=='Run C2 backtest' for x in at.button)
    at.selectbox(key='aegis_workspace').select('AI Agent Experiments').run()
    experiment=next(x for x in at.selectbox if x.label=='Experiment configuration')
    assert set(experiment.options)=={'All: C0 reference + C1 single agent + C2 multi-agent',
        'C0 — deterministic reference','C1 — single-agent baseline','C2 — multi-agent team'}
    health=client.get('/health').json()
    assert health['portfolio_flows']==['C2','TECHNICAL'] and health['c1_portfolio_legacy_readable']


def test_c1_api_requires_auth_consent_and_fixed_flow(monkeypatch):
    import app.api as api
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c1-portfolio-contract-token')
    client=TestClient(api.app);body=cfg(smc_history()).model_dump(mode='json')
    response=client.post('/simulation/c1/run',json=body)
    assert response.status_code==410 and 'AI Experiment' in response.json()['detail']
    assert client.post('/simulation/c2/run',json=body).status_code==422


def test_reviewed_news_endpoint_rejects_future_or_unverified(monkeypatch):
    import app.api as api
    from tests.company_fixtures import FakeArchive
    from aegistrade.company_research import prepare_company_research
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c1-portfolio-contract-token')
    prepare_company_research('DEMO','2024-04-01',provider=FakeArchive())
    client=TestClient(api.app);row={'symbol':'DEMO','kind':'newsletter','title':'Synthetic archived excerpt',
      'publisher':'Test publisher','source_url':'https://publisher.example/contract','published_at':'2024-04-02',
      'text':'Synthetic licensed excerpt for contract testing only. '*5,'original_publication_verified':True}
    body={'symbol':'DEMO','signal_date':'2024-04-01','reviewer':'Contract reviewer','jsonl':json.dumps(row)}
    assert client.post('/company-research/import-news',json=body).status_code==403
    headers={'x-reviewer-token':'c1-portfolio-contract-token'}
    assert client.post('/company-research/import-news',json=body,headers=headers).status_code==422
    row['published_at']='2024-03-31';body['jsonl']=json.dumps(row)
    r=client.post('/company-research/import-news',json=body,headers=headers)
    assert r.status_code==200,r.text
    assert any(d['kind']=='newsletter' for d in r.json()['documents'])


def test_hidden_legacy_c1_does_not_replace_c2_or_technical_ui_state(monkeypatch,tmp_path,completed_c2):
    from streamlit.testing.v1 import AppTest
    import app.api as api
    import aegistrade.c2_portfolio as portfolio
    from tests.test_c1_smc_portfolio import researcher,prepare
    from tests.test_c2_portfolio import settings
    from aegistrade.simulation_service import SimulationSettings,execute_simulation
    import requests
    f=smc_history();monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_frame',f)
    c1=portfolio.create_run(f,cfg(f));portfolio.execute_run(c1,f,researcher=researcher(completed_c2),preparer=prepare)
    c2=portfolio.create_run(f,settings(f));client=TestClient(api.app);posts=[]
    technical=execute_simulation(f,SimulationSettings(start_date=f.Date.iloc[20].date(),end_date=f.Date.iloc[-1].date()))
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,**kw):posts.append(url);raise AssertionError('Opening/restoring a flow must not submit work')
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30)
    at.session_state['simulation_result']=technical;at.run()
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    assert not at.exception and at.session_state['simulation_result']['run_id']==c2
    assert not any(x.key=='simulation_engine' for x in at.radio)
    assert at.session_state['simulation_result']['run_id']!=technical['run_id']
    assert portfolio.load(c1)['research_flow']=='C1'  # Legacy record remains readable through the API/data layer.
    assert not posts
