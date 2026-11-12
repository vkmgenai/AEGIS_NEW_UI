"""Field-specific correction and audit preservation; all model replies mocked."""
import copy,json
from pathlib import Path
from aegistrade.agentic import run_agentic_case
from aegistrade.llm_research import RouterClient
from aegistrade.research_diagnostics import diagnose_legacy_output,field_limits
from tests.test_agentic import SNAPSHOT,LocalTools,fake_team


def test_overlong_summary_is_corrected_with_exact_feedback(monkeypatch):
    observed=[];sent_long=False
    def fake(self,messages,**kw):
        nonlocal sent_long
        observed.append(messages[-1].get('content',''))
        if 'Role: market research' in messages[0]['content']:
            assert '"company.summary":{"minLength":1,"maxLength":600}' in messages[0]['content']
        answer=fake_team(self,messages,**kw)
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if role=='market' and answer.get('content') and not sent_long:
            sent_long=True;data=json.loads(answer['content']);data['company']['summary']='x'*701
            answer['content']=json.dumps(data)
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert out['guard_pass'] and out['llm_calls']==7 and not out['model_errors']
    assert any('company.summary must contain at most 600 characters (received 701)' in x for x in observed)
    assert any(e.get('code')=='OUTPUT_SCHEMA_INVALID' for e in out['trajectory'])


def test_persistent_length_error_is_schema_failure_not_provider_failure(monkeypatch):
    def fake(self,messages,**kw):
        answer=fake_team(self,messages,**kw)
        if answer.get('content'):
            value=json.loads(answer['content']);value['company']['summary']='x'*701
            answer['content']=json.dumps(value)
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert out['llm_calls']==3 and not out['guard_pass']
    assert out['failure']['category']=='SCHEMA'
    assert 'company.summary' in out['model_errors'][0] and '701' in out['model_errors'][0]
    assert 'provider' not in out['model_errors'][0].lower()


def test_insufficient_market_assessment_stops_before_other_specialists(monkeypatch):
    monkeypatch.setenv('AEGIS_DATED_WEB_SEARCH','false')
    def fake(self,messages,**kw):
        answer=fake_team(self,messages,**kw)
        if answer.get('content'):
            value=json.loads(answer['content']);value['company']['status']='INSUFFICIENT_EVIDENCE'
            answer['content']=json.dumps(value)
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not out['guard_pass'] and out['llm_calls']==2
    assert set(out['handoffs'])=={'market'}
    assert out['company_assessment']['status']=='INSUFFICIENT_EVIDENCE'
    assert out['failure']['code']=='COMPANY_ASSESSMENT_BLOCKED'


def test_review_required_can_still_support_holding_exit(monkeypatch):
    snapshot={**SNAPSHOT,'research_purpose':'HOLDING_REVIEW','holding_context':{'quantity':2,'entry_price':98.,
        'stop_price':94.,'strategy':'EMA_TREND','holding_sessions':5,'review_trigger':'Scheduled review'}}
    def fake(self,messages,**kw):
        answer=fake_team(self,messages,**kw)
        if answer.get('content'):
            value=json.loads(answer['content'])
            if 'company' in value:value['company']['status']='REVIEW_REQUIRED'
            if 'portfolio_action' in value or 'strategy' in value:value['portfolio_action']='EXIT'
            answer['content']=json.dumps(value)
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(snapshot,tools_factory=LocalTools)
    assert out['guard_pass'] and out['portfolio_action']=='EXIT' and out['llm_calls']==6


def legacy_output():
    from tests.company_fixtures import pack_for,assessment
    company=assessment(pack_for(SNAPSHOT));company['summary']='x'*701
    return {'guard_pass':False,'model_errors':['BLOCK: ValidationError; invalid evidence, exhausted budget or provider failure'],
        'trajectory':[{'event':'llm_response','agent':'market','message':{'content':json.dumps({
            'regime':'TREND','explanation':'Recorded synthetic market observation.','company':company})}}]}


def test_legacy_diagnosis_does_not_rewrite_original_record():
    output=legacy_output();before=copy.deepcopy(output)
    failure=diagnose_legacy_output(output)
    assert failure['code']=='OUTPUT_SCHEMA_INVALID' and '701' in failure['message']
    assert output==before and failure['source']=='saved_response_revalidation'


def test_portfolio_shows_diagnosis_without_modifying_saved_audit():
    from tests.test_c2_portfolio import history,settings
    from aegistrade.c2_portfolio import create_run,load,save,state_path,result_for
    f=history(65);rid=create_run(f,settings(f));state=load(rid);cid='a'*32
    record=state_path(rid).parent/'research'/f'{cid}.json';save(record,legacy_output());original=record.read_bytes()
    state['decisions']=[{'id':cid,'date':'2024-01-01','symbol':'DEMO','action':'BLOCKED','llm_calls':3,
        'errors':['BLOCK: ValidationError; invalid evidence, exhausted budget or provider failure']}]
    before=copy.deepcopy(state)
    view=result_for(state);decision=view['decisions'][0]
    assert decision['failure_category']=='SCHEMA' and 'company.summary' in decision['errors'][0]
    assert decision['recorded_errors']==state['decisions'][0]['errors']
    assert state==before and record.read_bytes()==original


def test_identical_repeated_observation_uses_reference_and_retains_full_trace(monkeypatch):
    from tests.test_agentic import call
    class LargeTools(LocalTools):
        async def call(self,name,args):
            result=await super().call(name,args)
            if name=='market_snapshot':result['diagnostic_padding']='x'*11500
            return result
    seen_reference=[];repeated=False
    def fake(self,messages,**kw):
        nonlocal repeated
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        observations=[m for m in messages if m['role']=='tool']
        if role=='market' and observations and not repeated:
            repeated=True;self.calls+=1
            request=call('market_snapshot');request['id']='repeat-market'
            return {'tool_calls':[request]}
        seen_reference.extend(m['content'] for m in observations if 'identical_to_tool_call_id' in m['content'])
        return fake_team(self,messages,**kw)
    monkeypatch.setattr(RouterClient,'chat',fake)
    result=run_agentic_case(SNAPSHOT,tools_factory=LargeTools)
    assert result['guard_pass'] and result['llm_calls']==7 and seen_reference
    market_reads=[t for t in result['tool_trace'] if t['tool']=='market_snapshot']
    assert len(market_reads)==2
    assert all(len(t['observation']['diagnostic_padding'])==11500 for t in market_reads)
