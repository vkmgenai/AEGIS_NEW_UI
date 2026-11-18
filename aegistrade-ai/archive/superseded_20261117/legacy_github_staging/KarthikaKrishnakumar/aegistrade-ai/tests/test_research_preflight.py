import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.client_errors import APIError
from aegistrade.research_service import memory_preflight,load_reviewed_memory,ResearchPreflightError


def test_memory_readiness_does_not_create_or_freeze_storage(tmp_path):
    assert not memory_preflight()['available']
    assert not (tmp_path/'reviewed_lessons.sqlite').exists()
    with pytest.raises(ResearchPreflightError,match='No frozen playbook'):load_reviewed_memory()
    assert not (tmp_path/'reviewed_lessons.sqlite').exists()


def test_empty_frozen_playbook_is_not_presented_as_reviewed_memory(tmp_path):
    from aegistrade.lessons import ReviewedPlaybook
    book=ReviewedPlaybook(tmp_path/'reviewed_lessons.sqlite');book.freeze('Test reviewer');book.conn.close()
    assert not memory_preflight()['available']
    with pytest.raises(ResearchPreflightError):load_reviewed_memory()


def test_only_frozen_accepted_lessons_enable_memory(tmp_path):
    from aegistrade.lessons import ReviewedPlaybook
    book=ReviewedPlaybook(tmp_path/'reviewed_lessons.sqlite')
    lid=book.propose('grounding','Check retrieved strategy evidence before citing it.','For strategy decisions')
    book.review(lid,'ACCEPT','Relevant operational lesson')
    assert not memory_preflight()['available']
    book.freeze('Independent test reviewer');book.conn.close()
    assert memory_preflight()['available']
    lessons,manifest=load_reviewed_memory();assert manifest['count']==1 and lessons


def test_memory_preflight_blocks_before_archive_or_model_work(monkeypatch):
    import app.api as api
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','preflight-test-reviewer')
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY');monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr('aegistrade.company_research.prepare_company_research',lambda *a,**kw:pytest.fail('No archive work before memory validation'))
    monkeypatch.setattr('aegistrade.research_service.run_research_case',lambda *a,**kw:pytest.fail('No paid calls'))
    client=TestClient(api.app)
    assert not client.get('/research/experiments/preflight').json()['memory']['available']
    response=client.post('/research/experiments/run',json={'configuration':'C2','use_memory':True,'consent_to_paid_calls':True},headers={'X-Reviewer-Token':'preflight-test-reviewer'})
    assert response.status_code==422
    detail=response.json()['detail'];assert detail['code']=='MEMORY_NOT_READY' and detail['paid_model_calls_started'] is False
    assert 'memory off' in detail['action']


def test_http_error_keeps_actionable_message_without_echoing_private_input(monkeypatch):
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','PRIVATE_TEST_TOKEN')
    response=SimpleNamespace(status_code=422,text='unused',json=lambda:{'detail':{'code':'MEMORY_NOT_READY','message':'No frozen playbook exists. PRIVATE_TEST_TOKEN','action':'Leave memory off.'}})
    error=APIError.from_response(response)
    assert 'No frozen playbook' in error.detail and error.action=='Leave memory off.'
    assert 'PRIVATE_TEST_TOKEN' not in str(error)
    response.json=lambda:{'detail':[{'loc':['body','cases'],'msg':'Must be at most 3','input':'DO_NOT_ECHO'}]}
    assert APIError.from_response(response).detail=='body.cases: Must be at most 3'
