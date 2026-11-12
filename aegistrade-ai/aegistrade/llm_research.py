"""Optional OpenRouter agent experiment harness, never authorizes execution.

C0 = deterministic route without model.
C1 = single tool-using agent with all available read tools.
C2 = supervisor and three bounded specialists; shared eight-call ceiling.
All configurations use same *available* evidence and same model, with total call
and output-token caps recorded; comparisons must account for actual token cost.

Use --cases <= 5 initially to avoid unexpected bills. Models can hallucinate.
"""
from __future__ import annotations
import os,time,json,re
from dataclasses import dataclass,field
from typing import Literal
from pydantic import BaseModel,ValidationError,Field,ConfigDict
import requests
from .budget import RunBudget
from .knowledge import PolicyRetriever

REGIMES={'TREND','RANGE','BREAKOUT','HIGH_VOL','UNCERTAIN','WARMUP'}
STRATS={'EMA_TREND','RSI_REVERSION','BREAKOUT','NONE'}

class CompanyAssessment(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    status:Literal['SUFFICIENT','LIMITED','INSUFFICIENT_EVIDENCE','REVIEW_REQUIRED']
    adverse_risk:Literal['NO_MATERIAL_ADVERSE_FOUND','COVERAGE_LIMITED','ADVERSE_EVENT_FOUND','MATERIAL_ADVERSE','UNKNOWN']='UNKNOWN'
    breakout_support:str|None=Field(default=None,min_length=1,max_length=350)
    summary:str=Field(min_length=1,max_length=600)
    citations:list[str]=Field(max_length=6)
    event_risks:list[str]=Field(max_length=4)
    limitations:list[str]=Field(min_length=1,max_length=4)

class MarketJudgement(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    regime:Literal['TREND','RANGE','BREAKOUT','HIGH_VOL','UNCERTAIN','WARMUP']
    explanation:str=Field(max_length=800)
    company:CompanyAssessment

class StrategyJudgement(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    strategy:Literal['EMA_TREND','RSI_REVERSION','BREAKOUT','NONE']
    citations:list[str]=Field(min_length=1,max_length=16)
    explanation:str=Field(max_length=800)
    portfolio_action:Literal['ENTER','HOLD','EXIT']='ENTER'

class CriticJudgement(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    accept:bool
    reason:str=Field(max_length=800)

class SingleJudgement(StrategyJudgement):
    company:CompanyAssessment

SIX_SLOT='Role: {role}\nContext: {context}\nTask: {task}\nConstraints: {constraints}\nFormat: {format}\nExamples: {examples}'

def strip_json(text:str):
    text=text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    if not text.startswith('{'):
        m=re.search(r'\{.*\}',text,re.DOTALL)
        if m:text=m.group(0)
    return json.loads(text)

@dataclass
class RouterClient:
    model:str='openai/gpt-4.1-mini'
    max_calls:int=3
    max_output_tokens_total:int=600
    calls:int=0
    output_budget_used:int=0
    usage:list=field(default_factory=list)
    def complete(self,prompt:str,max_tokens:int=200):
        message = self.chat([{'role':'system','content':'You are a cautious research assistant. Return requested JSON using only supplied evidence. Never execute orders.'}, {'role':'user','content':prompt}], max_tokens=max_tokens)
        return str(message.get('content') or '')

    def chat(self, messages:list, max_tokens:int=400, tools:list|None=None, tool_choice:str='auto'):
        key=os.getenv('OPENROUTER_API_KEY')
        if not key:raise RuntimeError('OPENROUTER_API_KEY missing')
        if self.calls >= self.max_calls or self.output_budget_used+max_tokens>self.max_output_tokens_total:
            raise RuntimeError('Model call or output-token cap reached')
        self.calls+=1
        self.output_budget_used+=max_tokens
        started=time.perf_counter()
        payload={'model':self.model,'messages':messages,'temperature':0,'max_tokens':max_tokens,
                 'usage':{'include':True}}
        if tools:
            payload.update(tools=tools,tool_choice=tool_choice,
                           provider={'require_parameters':True})
        try:
            response=requests.post('https://openrouter.ai/api/v1/chat/completions',
                headers={'Authorization':f'Bearer {key}','Content-Type':'application/json',
                         'X-Title':'AegisTrade AI Research'},json=payload,timeout=40)
            response.raise_for_status()
            body=response.json()
            if body.get('error'):raise ValueError('Provider returned an error')
            message=body['choices'][0]['message']
            if not isinstance(message,dict):raise ValueError('Invalid provider message')
            self.usage.append({'model':body.get('model',self.model),**(body.get('usage') or {}),
                               'latency_s':round(time.perf_counter()-started,3)})
            return message
        except Exception as exc:
            status=getattr(getattr(exc,'response',None),'status_code',None)
            self.usage.append({'model':self.model,'error':type(exc).__name__,'http_status':status,
                               'latency_s':round(time.perf_counter()-started,3)})
            raise RuntimeError(f'Model request failed ({type(exc).__name__}, HTTP {status}); check provider access/credits') from None

def run_research_case(snapshot:dict, config:str, model=None,
                      max_calls=8, max_output_tokens=4800, lessons:list|None=None,*,backend=None) -> dict:
    """C0 is deterministic; C1/C2 share the tool-using research implementation."""
    if config in {'C1','C2'}:
        from .agentic import run_agentic_case
        return run_agentic_case(snapshot,config,model=model,max_calls=max_calls,
                                max_output_tokens=max_output_tokens,lessons=lessons,backend=backend)
    if config!='C0':raise ValueError('Expected C0, C1 or C2')
    started=time.perf_counter()
    docs=PolicyRetriever(mode=os.getenv('AEGIS_RETRIEVAL_MODE','offline')).search('approved strategy regime risk no trade human approval',top_k=5)
    from .company_research import read_company_research
    company=(read_company_research(snapshot['symbol'],snapshot['date']) if snapshot.get('date') else
             {'ok':True,'status':'INSUFFICIENT_EVIDENCE','documents':[],
              'reasons':['No historical decision date supplied to the deterministic reference.']})
    return {'config':'C0','expected_strategy':snapshot['approved_candidate'],'expected_regime':snapshot['regime'],
            'selected_strategy':snapshot['approved_candidate'],'market_regime':snapshot['regime'],
            'model':'not_used','citations':[d['id'] for d in docs],'guard_pass':True,
            'llm_calls':0,'usage':[],'model_errors':[],'latency_s':round(time.perf_counter()-started,3),
            'company_research':company,
            'note':'Deterministic route reference; policy agreement is true by construction. Company coverage is reported separately, without semantic assessment or order eligibility.'}
