"""Budget, safety and reproducibility tests for the new UI backtests and AI research API."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from aegistrade.simulation_service import SimulationSettings,execute_simulation
from aegistrade.research_service import ResearchSettings,required_call_budget,execute_research
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators

@pytest.fixture(scope='module')
def prepared():
    return prepare_indicators(synthetic_market(n_days=230))


def test_simulation_configurable_capital_and_period(prepared,tmp_path):
    args=SimulationSettings(initial_capital=200000,start_date='2022-04-01',end_date='2022-10-31',mode='ALL')
    report=execute_simulation(prepared,args,save_dir=tmp_path)
    assert report['settings']['initial_capital']==200000
    assert len(report['metrics'])==5
    assert all(m['initial_capital']==200000 for m in report['metrics'])
    assert len(report['curves']['ROUTER'])==report['sessions']
    assert len(list(tmp_path.glob('*.json')))==1
    assert 'ROUTER is code-based' in report['disclaimer']
    assert all(len(x)==32 for x in [report['run_id']])


def test_capital_and_dates_rejected(prepared):
    with pytest.raises(ValidationError):SimulationSettings(initial_capital=-1)
    with pytest.raises(ValidationError):SimulationSettings(start_date='2024-02-01',end_date='2023-01-01')
    with pytest.raises(ValueError):execute_simulation(prepared,SimulationSettings(start_date='2022-01-03',end_date='2022-01-06'))


def test_no_llm_c0_works_offline(prepared,monkeypatch,tmp_path):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.delenv('AEGIS_ENABLE_LLM_EXPERIMENTS',raising=False)
    result=execute_research(prepared,ResearchSettings(configuration='C0',cases=2),model='unused',save_dir=tmp_path)
    assert result['summary'][0]['model_calls']==0
    assert len(result['outputs'])==2
    assert (tmp_path/(result['run_id']+'.json')).exists()


def test_paid_mode_requires_key_and_consent(prepared,monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    with pytest.raises(ValueError,match='explicit'):
        execute_research(prepared,ResearchSettings(configuration='C2',consent_to_paid_calls=False),model='unused')
    with pytest.raises(ValueError,match='key'):
        execute_research(prepared,ResearchSettings(configuration='C2',consent_to_paid_calls=True),model='unused')
    assert required_call_budget(ResearchSettings(configuration='ALL',cases=3))==48
    with pytest.raises(ValidationError):ResearchSettings(cases=4)


def test_c2_three_specialists_with_mock_no_network(prepared,monkeypatch):
    import aegistrade.research_service as research
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_FAKE_DO_NOT_USE')
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    from tests.company_fixtures import FakeArchive
    monkeypatch.setattr("aegistrade.company_research.NSEArchive",FakeArchive)
    seen=[]
    def fake(snapshot,config,model,max_calls,max_output_tokens):
        seen.append((snapshot['symbol'],config))
        n={'C0':0,'C1':1,'C2':3}[config]
        return {'config':config,'guard_pass':True,'model_errors':[],'llm_calls':n,
                'latency_s':0.11,'usage':[{'total_tokens':8} for _ in range(n)]}
    monkeypatch.setattr(research,'run_research_case',fake)
    result=execute_research(prepared,ResearchSettings(configuration='ALL',cases=2,consent_to_paid_calls=True),model='demo')
    assert len(result['outputs'])==6
    assert sum(r['model_calls'] for r in result['summary'])==8
    assert len(seen)==6


def test_api_backtest_and_c0_and_paid_guard(monkeypatch,tmp_path):
    import app.api as api
    monkeypatch.setattr(api,'DATA',tmp_path)
    monkeypatch.setattr(api,'_frame',None)
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.delenv('AEGIS_ENABLE_LLM_EXPERIMENTS',raising=False)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','a_private_demo_token')
    client=TestClient(api.app)
    response=client.post('/simulation/run',json={'initial_capital':200000,'mode':'ALL',
               'start_date':'2022-06-01','end_date':'2023-01-31'})
    assert response.status_code==200,response.text
    data=response.json()
    assert len(data['metrics'])==5 and data['settings']['initial_capital']==200000
    assert client.get('/simulation/result/'+data['run_id']).status_code==200
    assert client.get('/simulation/recent').json()['runs']
    assert client.post('/simulation/run',json={'start_date':'2022-03-01','end_date':'2022-01-01'}).status_code==422
    assert client.post('/research/experiments/run',json={'configuration':'C0','cases':1}).status_code==200
    assert client.post('/research/experiments/run',json={'configuration':'C1','cases':1,
                       'consent_to_paid_calls':True}).status_code==403
    assert client.post('/research/experiments/run',json={'configuration':'C1','cases':1,
                       'consent_to_paid_calls':True},headers={'X-Reviewer-Token':'a_private_demo_token'}).status_code==403
    assert client.get('/research/experiments/recent').json()['runs']
    assert client.get('/simulation/result/../secrets').status_code in {404,422}
