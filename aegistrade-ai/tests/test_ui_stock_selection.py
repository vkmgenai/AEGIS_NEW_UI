from types import SimpleNamespace
from pathlib import Path
from urllib.parse import urlsplit
import pytest


def test_ui_keeps_c2_portfolio_and_agent_comparison_separate(monkeypatch,tmp_path):
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
    assert not any(x.key=='simulation_engine' for x in at.radio)
    assert any(x.label=='Run C2 backtest' for x in at.button)
    assert not any(x.label=='Run C0 backtest' for x in at.button)
    at.selectbox(key='aegis_workspace').select('AI Agent Experiments').run()
    assert at.selectbox(key='aegis_workspace').value=='AI Agent Experiments'
    assert not any(x.label=='Research automatically ranked eligible stocks' for x in at.checkbox)
    assert not any(x.label=='C2 decision scenario' for x in at.radio)
    assert not any('Capstone minimum-bar evidence' in x.label for x in at.expander)
    assert 'Supervised Trading' not in at.selectbox(key='aegis_workspace').options
    assert 'Broker Audit' not in at.selectbox(key='aegis_workspace').options
    at.selectbox(key='aegis_workspace').select('Policy Knowledge').run()
    assert not at.exception
    next(x for x in at.button if x.label=='Search policy knowledge').click().run()
    assert not at.exception and at.session_state['aegis_passages']['results']
    assert at.session_state['aegis_passages']['corpus_sha256']
    assert not any(path=='/research/experiments/run' for path,_ in sent)


def test_ai_experiment_hides_manual_company_preparation_and_advanced_controls(monkeypatch,tmp_path):
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
    assert not at.exception
    assert not any(x.label=='Inspect cached company evidence' for x in at.button)
    assert not any(x.label=='Prepare historical company evidence' for x in at.button)
    assert not any(x.label=='Response-token budget per case (CLI: guidance)' for x in at.selectbox)
    assert not any(x.label=='Use frozen human-reviewed lessons' for x in at.checkbox)
    assert not any(x.label=='C2 decision scenario' for x in at.radio)
    assert not any(path=='/research/experiments/run' for method,path in sent)


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
    at.selectbox(key='aegis_workspace').select('Strategy Backtests').run()
    assert not any(x.key=='simulation_engine' for x in at.radio)
    assert not any(x.label=='Initial stop loss (% below signal close)' for x in at.number_input)
    assert not any(x.label=='Slippage (basis points per transaction)' for x in at.number_input)
    assert not any(x.label=='Breakout risk per trade (%)' for x in at.number_input)
    next(x for x in at.checkbox if x.label.startswith('I approve these')).check()
    next(x for x in at.checkbox if x.label.startswith('I authorize external inference for this historical')).check()
    next(x for x in at.button if x.label=='Run C2 backtest').click().run()
    assert not at.exception
    body=next(body for path,body in sent if path=='/simulation/c2/run')
    assert body['consent_to_paid_calls'] and body['approve_historical_rules'] and body['max_model_calls']==48
    assert body['trailing_stop_enabled'] is True and body['trailing_atr_multiple']==2.0
    assert body['take_profit_percent']==8.0 and body['review_after_gap'] is True
    assert body['stop_loss_mode']=='ATR' and body['initial_stop_atr_multiple']==2.0
    assert body['risk_percent']==1.0 and body['breakout_risk_percent']==0.5
    assert body['mode']=='ROUTER' and body['slippage_bps']==10.0
    assert at.session_state['simulation_result']['initial_stop_loss']['mode']=='ATR'
    assert at.text_input(key='portfolio_job_C2').value==at.session_state['simulation_result']['run_id']

    assert status_reads  # fragment performs a read-only poll immediately
    before=len(status_reads)
    next(x for x in at.button if x.label=='Refresh AI progress').click().run()
    assert not at.exception and len(status_reads)>before
    assert sum(path=='/simulation/c2/run' for path,_ in sent)==1
    assert not any(x.label=='Initial stop loss (% below signal close)' for x in at.number_input)


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
    at.selectbox(key='aegis_workspace').select('AI Agent Experiments').run()
    next(x for x in at.checkbox if x.label.startswith('I authorize this run to use the selected')).check()
    next(x for x in at.button if x.label=='Run AI experiment').click().run()
    assert not at.exception
    assert any('No frozen reviewed playbook exists' in x.value for x in at.error)
    assert any('Leave memory off.' in x.value for x in at.info)
    assert not any('Check model ID, API credits' in x.value for x in at.error)
