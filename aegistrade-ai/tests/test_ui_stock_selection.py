from types import SimpleNamespace
from pathlib import Path
from urllib.parse import urlsplit
import pytest


def test_ui_dataset_backtest_and_research_handoff(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    from fastapi.testclient import TestClient
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    import app.api as api
    import requests
    monkeypatch.setattr(api,'DATA',tmp_path)
    monkeypatch.setattr(api,'_frame',prepare_indicators(synthetic_market(n_days=230)))
    monkeypatch.setattr(api,'_broker',None)
    client=TestClient(api.app);sent=[]
    def adapt(response):
        return SimpleNamespace(ok=response.status_code<400,status_code=response.status_code,text=response.text,json=response.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,json=None,headers=None,**kw):
        sent.append((urlsplit(url).path,json));return adapt(client.post(urlsplit(url).path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    assert not at.exception
    assert at.selectbox(key='aegis_workspace').value=='Market Data'
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    assert not at.exception
    at.radio(key='simulation_engine').set_value('Technical-only baseline').run()
    next(x for x in at.checkbox if x.label.startswith('I approve these')).check()
    next(x for x in at.button if x.label=='Run historical portfolio simulation').click().run()
    assert not at.exception
    assert any(path=='/simulation/run' and body['automatic_stock_selection'] for path,body in sent)
    next(x for x in at.button if x.label=='Research automatically selected stocks with C2').click().run()
    assert not at.exception
    assert at.selectbox(key='aegis_workspace').value=='AI Agent Experiments'
    assert next(x for x in at.checkbox if x.label=='Research automatically ranked eligible stocks').value
    at.selectbox(key='aegis_workspace').select('Supervised Trading').run()
    assert not at.exception
    assert next(x for x in at.button if x.label=='Prepare researched order for human review').disabled
    at.selectbox(key='aegis_workspace').select('Policy Knowledge').run()
    assert not at.exception
    next(x for x in at.button if x.label=='Search policy knowledge').click().run()
    assert not at.exception and at.session_state['aegis_passages']['results']
    assert at.session_state['aegis_passages']['corpus_sha256']
    assert not any(path=='/research/experiments/run' for path,_ in sent)


def test_ui_historical_company_cache_inspection_has_no_paid_calls(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    from fastapi.testclient import TestClient
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    import app.api as api
    import requests
    monkeypatch.setattr(api,'DATA',tmp_path)
    monkeypatch.setattr(api,'_frame',prepare_indicators(synthetic_market(n_days=180)))
    client=TestClient(api.app);sent=[]
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);sent.append(('GET',u.path));return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,json=None,headers=None,**kw):
        u=urlsplit(url);sent.append(('POST',u.path));return adapt(client.post(u.path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    at.selectbox(key='aegis_workspace').select('AI Agent Experiments').run()
    next(x for x in at.button if x.label=='Inspect cached company evidence').click().run()
    assert not at.exception
    assert at.session_state['company_pack']['status']=='INSUFFICIENT_EVIDENCE'
    memory=next(x for x in at.checkbox if x.label=='Use frozen human-reviewed lessons')
    assert memory.disabled and memory.value is False
    assert not any(path=='/research/experiments/run' for method,path in sent)
    assert next(x for x in at.button if x.label=='Prepare historical company evidence').disabled


def test_ui_c2_portfolio_requires_and_sends_paid_rule_consent(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    from fastapi.testclient import TestClient
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    import app.api as api
    import aegistrade.c2_portfolio as portfolio
    import requests
    monkeypatch.setattr(api,'DATA',tmp_path)
    monkeypatch.setattr(api,'_frame',prepare_indicators(synthetic_market(n_days=180)))
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','portfolio-ui-test-reviewer')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY')
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr(portfolio,'active',lambda *a:True)
    monkeypatch.setattr(portfolio,'launch',lambda *a:None)  # no background/model work in UI contract
    client=TestClient(api.app);sent=[];status_reads=[]
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url)
        if u.path.startswith('/simulation/c2/status/'):status_reads.append(u.path)
        return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,json=None,headers=None,**kw):
        u=urlsplit(url);sent.append((u.path,json));return adapt(client.post(u.path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    next(x for x in at.text_input if 'token' in x.label.lower()).input('portfolio-ui-test-reviewer').run()
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    assert at.radio(key='simulation_engine').value=='C2 historical portfolio'
    at.selectbox(key='initial_stop_method').select('Percentage below signal close').run()
    next(x for x in at.number_input if x.label=='Initial stop loss (% below signal close)').set_value(3.0)
    next(x for x in at.checkbox if x.label.startswith('I approve these')).check()
    next(x for x in at.checkbox if x.label.startswith('I authorize external inference for this historical')).check()
    next(x for x in at.button if x.label=='Run historical portfolio simulation').click().run()
    assert not at.exception
    body=next(body for path,body in sent if path=='/simulation/c2/run')
    assert body['consent_to_paid_calls'] and body['approve_historical_rules'] and body['max_model_calls']==48
    assert body['trailing_stop_enabled'] is True and body['trailing_atr_multiple']==2.0
    assert body['take_profit_percent']==8.0 and body['review_after_gap'] is True
    assert body['stop_loss_mode']=='PERCENT' and body['stop_loss_percent']==3.0
    assert at.session_state['simulation_result']['initial_stop_loss']['mode']=='PERCENT'
    assert at.text_input(key='c2_job_input').value==at.session_state['simulation_result']['run_id']

    assert status_reads  # fragment performs a read-only poll immediately
    before=len(status_reads)
    next(x for x in at.button if x.label=='Refresh AI progress').click().run()
    assert not at.exception and len(status_reads)>before
    assert sum(path=='/simulation/c2/run' for path,_ in sent)==1
    assert next(x for x in at.number_input if x.label=='Initial stop loss (% below signal close)').value==3.0


def test_research_failure_shows_specific_api_reason_and_action(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    from fastapi.testclient import TestClient
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    import app.api as api
    import requests
    monkeypatch.setattr(api,'_frame',prepare_indicators(synthetic_market(n_days=180)))
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','research-ui-test-reviewer')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY');monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    client=TestClient(api.app)
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    def post(url,json=None,headers=None,**kw):
        if urlsplit(url).path=='/research/experiments/run':
            return SimpleNamespace(ok=False,status_code=422,text='unused',json=lambda:{'detail':{
                'code':'MEMORY_NOT_READY','message':'No frozen reviewed playbook exists.','action':'Leave memory off.'}})
        return adapt(client.post(urlsplit(url).path,json=json,headers=headers or {}))
    monkeypatch.setattr(requests,'get',get);monkeypatch.setattr(requests,'post',post)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    next(x for x in at.text_input if 'token' in x.label.lower()).input('research-ui-test-reviewer').run()
    at.selectbox(key='aegis_workspace').select('AI Agent Experiments').run()
    next(x for x in at.checkbox if x.label.startswith('I authorize this run to use the selected')).check()
    next(x for x in at.button if x.label=='Run AI experiment').click().run()
    assert not at.exception
    assert any('No frozen reviewed playbook exists' in x.value for x in at.error)
    assert any('Leave memory off.' in x.value for x in at.info)
    assert not any('Check model ID, API credits' in x.value for x in at.error)
