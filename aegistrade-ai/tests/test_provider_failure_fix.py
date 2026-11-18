"""No live generation: exact citation evidence and precise paused-provider failures."""
import copy,json
from pathlib import Path
from unittest.mock import Mock
from aegistrade.knowledge import PolicyRetriever
from aegistrade.research_diagnostics import inference_diagnostic,diagnose_legacy_output
from aegistrade.agentic import run_agentic_case
from aegistrade.llm_research import RouterClient
from tests.test_agentic import SNAPSHOT,LocalTools,fake_team


def test_exact_citation_cannot_be_lost_to_semantic_ranking():
    r=PolicyRetriever()
    ranked=r.search('company evidence sufficiency risk',top_k=5,required_ids=['POL-43','POL-10'],as_of='2023-12-01')
    assert [d['id'] for d in ranked[:2]]==['POL-43','POL-10']
    assert all(d['corpus_sha256']==r.corpus_sha256 for d in ranked)
    assert r.search('POL-43 company evidence',top_k=1)[0]['id']=='POL-43'


def test_exact_lookup_keeps_external_date_filter():
    r=PolicyRetriever()
    found=r.search('REF-ALIAS-01',top_k=5,required_ids=['REF-ALIAS-01'],as_of='2024-01-01')
    assert 'REF-ALIAS-01' not in {d['id'] for d in found}


def test_critic_rejection_does_not_make_unproductive_revision_call(monkeypatch):
    def fake(self,messages,**kw):
        answer=fake_team(self,messages,**kw)
        if 'Role: critic research' in messages[0]['content'] and answer.get('content'):
            answer['content']=json.dumps({'accept':False,'reason':'Synthetic critic rejection requiring review.'})
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert out['llm_calls']==6 and not out['guard_pass']
    assert out['failure']['code']=='CRITIC_REJECTED' and out['critic_accept'] is False
    assert not any(e.get('event')=='replan' and e.get('agent')=='supervisor' for e in out['trajectory'])


def test_runtime_pins_strategy_ids_for_independent_critic_search(monkeypatch):
    class InspectTools(LocalTools):
        seen=[]
        def __init__(self,snapshot):super().__init__(snapshot);self.required_policy_ids=()
        async def call(self,name,args):
            if name=='search_policy' and self.required_policy_ids:
                self.seen.append(self.required_policy_ids)
            return await super().call(name,args)
    monkeypatch.setattr(RouterClient,'chat',fake_team)
    out=run_agentic_case(SNAPSHOT,tools_factory=InspectTools)
    assert out['guard_pass']
    assert InspectTools.seen==[('POL-72',),('POL-06',)]


def test_c1_route_policy_is_pinned_before_initial_search(monkeypatch):
    class InspectTools(LocalTools):
        seen=[]
        def __init__(self,snapshot):super().__init__(snapshot);self.required_policy_ids=()
        async def call(self,name,args):
            if name=='search_policy':self.seen.append(self.required_policy_ids)
            return await super().call(name,args)
    monkeypatch.setattr(RouterClient,'chat',fake_team)
    out=run_agentic_case(SNAPSHOT,'C1',tools_factory=InspectTools)
    assert out['guard_pass'] and InspectTools.seen==[('POL-72',)]


def test_company_citation_retry_guidance_does_not_relax_guard(monkeypatch):
    sent_invalid=False;correction_seen=False
    def fake(self,messages,**kwargs):
        nonlocal sent_invalid,correction_seen
        answer=fake_team(self,messages,**kwargs)
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if role=='single' and answer.get('content') and not sent_invalid:
            value=json.loads(answer['content'])
            value['company']['citations']=['WEBSCAN-NOT-ELIGIBLE']
            answer['content']=json.dumps(value);sent_invalid=True
        elif role=='single' and answer.get('content'):
            correction_seen=any('company.citations may use only these exact' in str(m.get('content','')) for m in messages)
        return answer
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,'C1',tools_factory=LocalTools)
    assert correction_seen and out['guard_pass']


def test_openrouter_final_turn_requests_json_object(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-only')
    captured={}
    response=Mock()
    response.raise_for_status.return_value=None
    response.json.return_value={'model':'test','choices':[{'message':{'content':'{"accept":true}'}}],
                                'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2,'cost':0}}
    def post(*args,**kwargs):captured.update(kwargs['json']);return response
    monkeypatch.setattr('aegistrade.llm_research.requests.post',post)
    client=RouterClient(model='test',max_calls=1,max_output_tokens_total=200)
    client.chat([{'role':'user','content':'Return JSON'}],max_tokens=100,tool_choice='none')
    assert captured['response_format']=={'type':'json_object'}


def test_timeout_and_format_errors_do_not_claim_credit_failure():
    for code in ['CODEX_TIMEOUT','CODEX_OUTPUT_INVALID']:
        usage=[{'error':'TimeoutExpired' if code=='CODEX_TIMEOUT' else 'ValueError','error_code':code,'latency_s':120.03}]
        result=inference_diagnostic(usage,'strategy')
        assert result['code']==code and result['category']=='PROVIDER'
        assert result['elapsed_seconds']==120.03
    assert inference_diagnostic([{'error':'HTTPError','http_status':402}])['code']=='HTTP_402'


def test_saved_generic_provider_error_is_reconstructed_without_mutation():
    out={'failure':{'code':'INFERENCE_FAILED','category':'PROVIDER','agent':'strategy','message':'Generic'},
        'usage':[{'error':'TimeoutExpired','error_code':'CODEX_TIMEOUT','latency_s':120.03}]}
    before=copy.deepcopy(out);result=diagnose_legacy_output(out)
    assert result['code']=='CODEX_TIMEOUT' and result['source']=='saved_transport_usage'
    assert out==before


def test_paused_portfolio_decision_retains_specific_code(completed_c2):
    from tests.test_c2_portfolio import history,settings,prepare
    from aegistrade.c2_portfolio import create_run,execute_run
    frame=history(65);rid=create_run(frame,settings(frame))
    def fail(*a,**kw):return {'guard_pass':False,'llm_calls':1,'model_errors':['Generic failure'],
        'failure':{'code':'INFERENCE_FAILED','category':'PROVIDER'},
        'usage':[{'error':'TimeoutExpired','error_code':'CODEX_TIMEOUT','latency_s':120.03}]}
    result=execute_run(rid,frame,researcher=fail,preparer=prepare)
    assert result['status']=='PAUSED_PROVIDER'
    decision=result['decisions'][0]
    assert decision['failure_category']=='PROVIDER' and decision['failure']['code']=='CODEX_TIMEOUT'
    assert decision['errors'][0].startswith('CODEX_TIMEOUT:')
    assert not result['ledgers']['C2']
