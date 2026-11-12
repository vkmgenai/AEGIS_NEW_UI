"""Transport contracts: mocked CLI subprocesses, no subscription usage."""
import json,os,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from aegistrade import llm_backend as b


def fake_cli(monkeypatch,envelope,*,native=None,code=0,stderr=''):
    monkeypatch.setattr(b,'codex_binary',lambda:'/test/codex')
    monkeypatch.setattr(b,'backend_info',lambda **kw:{'ready':True,'cli_version':'test-cli'})
    seen={}
    def execute(command,prompt,*,env,cwd,timeout):
        seen.update(command=command,prompt=json.loads(prompt),env=env,cwd=cwd)
        Path(cwd,'answer.json').write_text(json.dumps(envelope))
        events=[{'type':'turn.completed','usage':{'input_tokens':80,'output_tokens':20}}]
        if native:events.insert(0,{'type':'item.completed','item':{'type':native}})
        return code,'\n'.join(json.dumps(e) for e in events),stderr
    monkeypatch.setattr(b,'_execute',execute)
    return seen


def test_configuration_selects_one_transport_without_fallback(monkeypatch):
    monkeypatch.setenv('AEGIS_LLM_BACKEND','codex_cli')
    monkeypatch.setenv('OPENROUTER_MODEL','router-only-model')
    assert isinstance(b.create_client(),b.CodexClient)
    assert b.model_name()=='codex-default'
    monkeypatch.setenv('AEGIS_LLM_BACKEND','openrouter')
    from aegistrade.llm_research import RouterClient
    assert isinstance(b.create_client(),RouterClient)
    assert b.model_name()=='router-only-model'
    monkeypatch.setenv('AEGIS_LLM_BACKEND','claude_cli')
    with pytest.raises(ValueError):b.create_client()


def test_cli_returns_json_without_secrets_or_repo_access(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','do-not-pass')
    monkeypatch.setenv('OPENAI_API_KEY','do-not-pass-either')
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','private-reviewer')
    seen=fake_cli(monkeypatch,{'kind':'final','content':'{"accept":true}','tool_calls':[]})
    c=b.CodexClient(max_calls=1)
    assert json.loads(c.complete('Return a typed decision'))=={'accept':True}
    assert not any(k in seen['env'] for k in ('OPENAI_API_KEY','OPENROUTER_API_KEY','AEGIS_REVIEWER_TOKEN'))
    assert seen['cwd']!=Path.cwd() and not seen['cwd'].exists()
    cmd=seen['command']
    for flag in ['--ephemeral','--ignore-rules','--ignore-user-config','--strict-config','--output-schema']:assert flag in cmd
    for control in ['features.shell_tool=false','features.apps=false','web_search="disabled"','mcp_servers={}']:assert control in cmd
    assert c.usage[0]['total_tokens']==100 and c.usage[0]['cost'] is None
    assert c.usage[0]['provider_request_count'] is None
    assert not c.usage[0]['hard_provider_token_cap']
    with pytest.raises(RuntimeError,match='budget'):c.complete('Another invocation')
    assert c.calls==1


def test_virtual_tools_are_returned_to_application_not_executed(monkeypatch):
    seen=fake_cli(monkeypatch,{'kind':'tool_calls','content':None,'tool_calls':[{'name':'company_evidence','arguments':'{}'}]})
    c=b.CodexClient();tools=[{'type':'function','function':{'name':'company_evidence','parameters':{'type':'object'}}}]
    answer=c.chat([{'role':'user','content':'Assess dated company evidence'}],tools=tools)
    assert answer['tool_calls'][0]['function']=={'name':'company_evidence','arguments':'{}'}
    assert seen['prompt']['allowed_virtual_tools']==tools


@pytest.mark.parametrize('envelope,native',[
    ({'kind':'tool_calls','content':None,'tool_calls':[{'name':'shell','arguments':'{}'}]},None),
    ({'kind':'final','content':'{"accept":true}','tool_calls':[]},'command_execution'),
    ({'kind':'final','content':'{"accept":true}','tool_calls':[]},'mcp_tool_call'),
    ({'kind':'final','content':'not JSON','tool_calls':[]},None)])
def test_unexpected_tools_and_invalid_output_fail_closed(monkeypatch,envelope,native):
    fake_cli(monkeypatch,envelope,native=native)
    c=b.CodexClient()
    with pytest.raises(RuntimeError,match='CODEX_'):c.complete('Return JSON')
    assert c.calls==1 and c.usage[0]['error']


def test_quota_failure_counts_attempt_and_never_retries(monkeypatch):
    seen=fake_cli(monkeypatch,{},code=1,stderr='Usage limit reached')
    c=b.CodexClient()
    with pytest.raises(RuntimeError,match='CODEX_QUOTA'):c.complete('Return JSON')
    assert c.calls==1 and len(c.usage)==1


def test_timeout_counts_attempt(monkeypatch):
    fake_cli(monkeypatch,{})
    def timeout(*a,**kw):raise subprocess.TimeoutExpired('codex',120)
    monkeypatch.setattr(b,'_execute',timeout)
    c=b.CodexClient()
    with pytest.raises(RuntimeError,match='CODEX_TIMEOUT'):c.complete('Return JSON')
    assert c.calls==1 and c.usage[0]['error_code']=='CODEX_TIMEOUT'


def test_cli_requires_chatgpt_auth_before_starting(monkeypatch):
    monkeypatch.setattr(b,'backend_info',lambda **kw:{'ready':False,'reason':'Run codex login'})
    c=b.CodexClient()
    with pytest.raises(RuntimeError,match='login'):c.complete('Return JSON')
    assert c.calls==0 and c.usage[0]['invocation_started'] is False


def test_portfolio_rejects_backend_change_before_any_generation(monkeypatch):
    from tests.test_c2_portfolio import history,settings
    from aegistrade.c2_portfolio import create_run,execute_run
    f=history(65);rid=create_run(f,settings(f))
    monkeypatch.setenv('AEGIS_LLM_BACKEND','codex_cli')
    with pytest.raises(ValueError,match='Inference backend'):execute_run(rid,f)


def test_api_codex_readiness_does_not_require_openrouter_key(monkeypatch):
    from fastapi.testclient import TestClient
    import app.api as api
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr(api,'backend_info',lambda:{'ready':True,'backend':'codex_cli','budget_unit':'cli_invocations'})
    health=TestClient(api.app).get('/health').json()
    assert health['llm_experiments_enabled'] and not health['openrouter_opt_in']
    assert health['inference']['backend']=='codex_cli'


def test_timeout_terminates_the_actual_child_process(monkeypatch,tmp_path):
    import sys
    real_popen=subprocess.Popen;children=[]
    def capture(*a,**kw):
        proc=real_popen(*a,**kw);children.append(proc);return proc
    monkeypatch.setattr(b.subprocess,'Popen',capture)
    with pytest.raises(subprocess.TimeoutExpired):
        b._execute([sys.executable,'-c','import time; time.sleep(20)'],'',env=os.environ.copy(),cwd=tmp_path,timeout=.1)
    assert len(children)==1 and children[0].poll() is not None


def test_codex_selected_c2_keeps_three_specialists_and_scoped_tools(monkeypatch):
    from tests.test_agentic import SNAPSHOT,LocalTools,fake_team
    from aegistrade.agentic import run_agentic_case
    from aegistrade.llm_research import RouterClient
    monkeypatch.setenv('AEGIS_LLM_BACKEND','codex_cli')
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.setattr(b.CodexClient,'chat',fake_team)
    monkeypatch.setattr(RouterClient,'chat',lambda *a,**kw:pytest.fail('No OpenRouter fallback allowed'))
    result=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert result['guard_pass'] and result['llm_calls']==6
    assert set(result['handoffs'])=={'market','strategy','critic'}
    assert result['inference']['backend']=='codex_cli'
    assert result['inference']['budget_unit']=='cli_invocations'


def test_typed_specialist_output_avoids_nested_json_string(monkeypatch):
    from jsonschema import Draft202012Validator
    payload={'accept':True,'reason':'Observed source and route agree.','breakout_evidence':None}
    seen=fake_cli(monkeypatch,{'kind':'final','content':payload,'tool_calls':[]})
    original=b._execute;captured={}
    def execute(*args,**kwargs):
        schema=json.loads(Path(kwargs['cwd'],'schema.json').read_text());captured.update(schema)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate({'kind':'final','content':payload,'tool_calls':[]})
        return original(*args,**kwargs)
    monkeypatch.setattr(b,'_execute',execute)
    client=b.CodexClient()
    result=client.chat([{'role':'system','content':'Role: critic research specialist\nTask: verify.'}],tool_choice='none')
    assert json.loads(result['content'])==payload
    assert captured['properties']['content']['anyOf'][0]['type']=='object'
    assert client.usage[0]['response_format']=='typed-specialist-object' and client.calls==1


def test_market_output_schema_definitions_and_required_fields():
    from jsonschema import Draft202012Validator
    payload=b.specialist_schema([{'role':'system','content':'Role: market research specialist\nTask: inspect.'}])
    schema=b.envelope_schema(['company_evidence'],'auto',payload)
    Draft202012Validator.check_schema(schema)
    assert 'CompanyAssessment' in schema['$defs']
    assert 'adverse_risk' in schema['$defs']['CompanyAssessment']['required']
    Draft202012Validator(schema).validate({'kind':'tool_calls','content':None,'tool_calls':[{'name':'company_evidence','arguments':'{}'}]})


def test_malformed_inner_json_records_stage_without_raw_private_output(monkeypatch):
    fake_cli(monkeypatch,{'kind':'final','content':'{"reason":"PRIVATE_MALFORMED','tool_calls':[]})
    client=b.CodexClient()
    with pytest.raises(RuntimeError,match='CODEX_OUTPUT_INVALID'):client.complete('Return JSON')
    usage=client.usage[0]
    assert usage['validation_stage']=='specialist_content' and usage['json_error']['column']>0
    assert 'PRIVATE_MALFORMED' not in json.dumps(usage)
    from aegistrade.research_diagnostics import inference_diagnostic
    diag=inference_diagnostic(client.usage,'critic')
    assert diag['invalid_reason']=='Malformed JSON at specialist_content'
    assert client.calls==1


def test_fenced_json_is_unwrapped_without_retry_or_content_repair(monkeypatch):
    fake_cli(monkeypatch,{'kind':'final','content':'```json\n{"accept":false,"reason":"Unresolved exposure"}\n```','tool_calls':[]})
    client=b.CodexClient();payload=json.loads(client.complete('Return JSON'))
    assert payload=={'accept':False,'reason':'Unresolved exposure'} and client.calls==1
