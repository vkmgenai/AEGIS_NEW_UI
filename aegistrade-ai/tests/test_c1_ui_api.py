from types import SimpleNamespace
from pathlib import Path
from urllib.parse import urlsplit
import json
import pytest
from fastapi.testclient import TestClient
from tests.test_c1_smc_portfolio import smc_history,cfg


@pytest.mark.parametrize('completed',[False,True])
def test_three_flow_ui_posts_c1_with_consent_and_default_profit(monkeypatch,tmp_path,completed_c2,completed):
    from streamlit.testing.v1 import AppTest
    import app.api as api
    import aegistrade.c2_portfolio as portfolio
    import requests
    monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_frame',smc_history())
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c1-portfolio-contract-token')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY');monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    from tests.test_c1_smc_portfolio import researcher,prepare
    monkeypatch.setattr(portfolio,'active',lambda *a:not completed)
    monkeypatch.setattr(portfolio,'launch',lambda rid,frame:portfolio.execute_run(rid,frame,researcher=researcher(completed_c2),preparer=prepare) if completed else None)
    client=TestClient(api.app);sent=[]
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,json=None,headers=None,**kw):
        path=urlsplit(url).path;sent.append((path,json));return adapt(client.post(path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    next(x for x in at.text_input if 'token' in x.label.lower()).input('c1-portfolio-contract-token').run()
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    flow=at.radio(key='simulation_engine')
    assert flow.options==['C2 historical portfolio','C1 SMC portfolio','Technical-only baseline']
    flow.set_value('C1 SMC portfolio').run();assert not at.exception
    assert next(x for x in at.selectbox if x.label=='Strategies to run').value=='SMC'
    assert next(x for x in at.number_input if x.label.startswith('Take-profit target')).value==4.
    assert not next(x for x in at.checkbox if x.label=='Enable trailing stop').value
    next(x for x in at.checkbox if x.label.startswith('I approve these')).check()
    next(x for x in at.checkbox if x.label.startswith('I authorize external inference')).check()
    next(x for x in at.button if x.label=='Run historical portfolio simulation').click().run()
    assert not at.exception
    body=next(b for path,b in sent if path=='/simulation/c1/run')
    assert body['mode']=='SMC' and body['consent_to_paid_calls'] and body['take_profit_percent']==4
    assert body['screening_candidates_per_session']==3 and not body['breakout_reentry_enabled']
    assert at.session_state['simulation_result']['research_flow']=='C1'
    if completed:
        tables=[x.value for x in at.dataframe if 'Stage' in x.value.columns]
        assert tables and not tables[0].empty
        assert set(tables[0]['Stage'])=={'Before SMC signal'}
        assert tables[0]['Estimated shares'].isna().all()
        assert set(tables[0]['Strategy'])=={'Not evaluated yet'}
    before=len(sent)
    next(x for x in at.button if x.label=='Refresh AI progress').click().run()
    assert not at.exception and len(sent)==before


def test_c1_api_requires_auth_consent_and_fixed_flow(monkeypatch):
    import app.api as api
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','c1-portfolio-contract-token')
    client=TestClient(api.app);body=cfg(smc_history()).model_dump(mode='json')
    assert client.post('/simulation/c1/run',json=body).status_code==403
    assert client.post('/simulation/c2/run',json=body).status_code==422
    body['consent_to_paid_calls']=False
    assert client.post('/simulation/c1/run',json=body,headers={'x-reviewer-token':'c1-portfolio-contract-token'}).status_code==422


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
