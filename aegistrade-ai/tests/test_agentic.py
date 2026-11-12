import json
from tests.company_fixtures import pack_for,assessment
from contextlib import asynccontextmanager
import pytest
from fastmcp import Client
from aegistrade.agentic import run_agentic_case
from aegistrade.agent_tools import market_observation, strategy_observation, CaseEvidence
from aegistrade.llm_research import RouterClient, run_research_case
from aegistrade.research_service import ResearchSettings, required_call_budget
from aegistrade.mcp_runtime import ResearchTools

SNAPSHOT={'symbol':'DEMO','date':'2024-01-01','regime':'TREND','approved_candidate':'EMA_TREND',
          'Close':100.,'RSI14':55.,'ADX14':25.,'EMA20':99.,'EMA50':95.,'ATR14':2.,'future_price':200}


def call(name,args=None):
    return {'id':name,'type':'function','function':{'name':name,'arguments':json.dumps(args or {})}}

class LocalTools:
    mode='test-double'
    def __init__(self,snapshot):
        self.evidence=CaseEvidence.from_snapshot(snapshot);self.pack=pack_for(snapshot)
    async def __aenter__(self):return self
    async def __aexit__(self,*a):pass
    async def call(self,name,args):
        if name=='company_evidence':return self.pack
        if name=='market_snapshot':return market_observation(self.evidence)
        if name=='check_strategy':return strategy_observation(self.evidence)
        return {'ok':True,'corpus_sha256':__import__('aegistrade.corpus',fromlist=['corpus_info']).corpus_info()['sha256'],'results':[{'id':'POL-06','text':'A human must approve the exact order.'}]}


def fake_team(self,messages,**kw):
    self.calls+=1
    role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
    if not any(m['role']=='tool' for m in messages):
        names={'market':['market_snapshot','company_evidence'],'strategy':['search_policy','check_strategy'],
               'critic':['search_policy','check_strategy','company_evidence'],'single':['market_snapshot','company_evidence','search_policy','check_strategy']}[role]
        return {'tool_calls':[call(n,{'query':'human approval'} if n=='search_policy' else {}) for n in names]}
    payload={'market':{'regime':'TREND','explanation':'ADX and averages support trend.'},
             'strategy':{'strategy':'EMA_TREND','citations':['POL-06'],'explanation':'Trend route; exact approval required.'},
             'critic':{'accept':True,'reason':'Policy and route agree.'},
             'single':{'strategy':'EMA_TREND','citations':['POL-06'],'explanation':'Trend route; exact approval required.'}}[role]
    if role in {'market','single'}:
        pack=json.loads(next(m['content'] for m in messages if m['role']=='tool' and 'pack_sha256' in m.get('content','')))
        payload['company']=assessment(pack)
    return {'content':json.dumps(payload)}


def test_team_three_specialists_and_single_share_budget(monkeypatch):
    observed=[]
    def fake(self,messages,**kwargs):
        observed.append(json.dumps(messages))
        return fake_team(self,messages,**kwargs)
    monkeypatch.setattr(RouterClient,'chat',fake)
    team=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    single=run_agentic_case(SNAPSHOT,'C1',tools_factory=LocalTools)
    assert team['guard_pass'] and single['guard_pass']
    assert team['llm_calls']==6 and single['llm_calls']==2
    assert set(team['handoffs'])=={'market','strategy','critic'}
    assert team['budget']==single['budget'] and team['available_tools']==single['available_tools']
    assert 'future_price' not in ''.join(observed) and 'approved_candidate' not in ''.join(observed)
    assert any(x['event']=='pre_tool' for x in team['trajectory'])
    assert required_call_budget(ResearchSettings(configuration='C2',cases=3))==24


def test_no_evidence_and_fabricated_citation_blocked(monkeypatch):
    def fake(self,*a,**kw):
        self.calls+=1
        return {'content':json.dumps({'regime':'TREND','explanation':'Unsupported'})}
    monkeypatch.setattr(RouterClient,'chat',fake)
    result=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not result['guard_pass'] and result['model_errors']
    assert any(x['event']=='replan' for x in result['trajectory'])


def test_unknown_write_tool_denied_and_bounded(monkeypatch):
    def fake(self,*a,**kw):
        self.calls+=1
        return {'tool_calls':[call('submit_live_order')]}
    monkeypatch.setattr(RouterClient,'chat',fake)
    result=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not result['guard_pass'] and result['llm_calls']==3
    assert all(not x['observation']['ok'] for x in result['tool_trace'])


def test_provider_exception_and_tool_secrets_scrubbed(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','PRIVATE_TEST_KEY')
    def fail(*a,**kw):raise RuntimeError('PRIVATE_TEST_KEY')
    monkeypatch.setattr(RouterClient,'chat',fail)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not out['guard_pass'] and 'PRIVATE_TEST_KEY' not in json.dumps(out)


def test_real_inprocess_mcp_evidence():
    import asyncio
    from mcp_servers.market_server import mcp as market
    from mcp_servers.strategy_server import mcp as strategy
    from mcp_servers.knowledge_server import mcp as knowledge
    async def run():
        async with ResearchTools(SNAPSHOT,clients={n:Client(s) for n,s in [('market',market),('strategy',strategy),('knowledge',knowledge)]}) as tools:
            assert (await tools.call('market_snapshot',{}))['ok']
            assert (await tools.call('check_strategy',{}))['data']['approved_strategy']=='EMA_TREND'
            assert (await tools.call('search_policy',{'query':'human approval'}))['results']
    asyncio.run(run())


def test_specialist_corrects_contradiction_within_shared_budget(monkeypatch):
    wrong_sent=False
    def fake(self,messages,**kwargs):
        nonlocal wrong_sent
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if role=='market' and any(m['role']=='tool' for m in messages) and not wrong_sent:
            wrong_sent=True;self.calls+=1
            return {'content':json.dumps({'regime':'RANGE','explanation':'Deliberately contradictory development response'})}
        return fake_team(self,messages,**kwargs)
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert out['guard_pass'] and out['llm_calls']==7
    assert any(e['event']=='replan' for e in out['trajectory'])


def test_fabricated_citation_rejected_after_real_tool_evidence(monkeypatch):
    def fake(self,messages,**kwargs):
        message=fake_team(self,messages,**kwargs)
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if role=='strategy' and message.get('content'):
            value=json.loads(message['content']);value['citations']=['POL-NOT-RETRIEVED'];message['content']=json.dumps(value)
        return message
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not out['guard_pass'] and out['model_errors']
    assert 'strategy' not in out['handoffs']


def test_three_specialists_can_make_typed_holding_exit(monkeypatch):
    snap={**SNAPSHOT,'research_purpose':'HOLDING_REVIEW','holding_context':{'quantity':2,'entry_price':98.,
          'stop_price':94.,'strategy':'EMA_TREND','holding_sessions':5,'review_trigger':'Scheduled review'}}
    def fake(self,messages,**kw):
        out=fake_team(self,messages,**kw)
        role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if role=='strategy' and out.get('content'):
            payload=json.loads(out['content']);payload['portfolio_action']='EXIT';out['content']=json.dumps(payload)
        return out
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(snap,tools_factory=LocalTools)
    assert out['guard_pass'] and out['portfolio_action']=='EXIT' and out['llm_calls']==6
    from aegistrade.research_gate import validate_completed_c2
    out['snapshot']=snap
    assert validate_completed_c2(out,purpose='HOLDING_REVIEW')['portfolio_action']=='EXIT'
