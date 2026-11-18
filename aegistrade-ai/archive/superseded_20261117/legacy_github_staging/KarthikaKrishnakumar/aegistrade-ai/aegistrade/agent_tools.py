"""Shared typed contracts for local MCP and agent research tools. No gold labels."""
from __future__ import annotations
import math
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class HoldingContext(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    quantity:int=Field(gt=0)
    entry_price:float=Field(gt=0)
    # Zero is the simulator sentinel when the user explicitly disables stops.
    # Such a position must remain eligible for scheduled holding research.
    stop_price:float=Field(ge=0)
    strategy:Literal['EMA_TREND','EMA_PULLBACK','RSI_REVERSION','BREAKOUT','SMC']
    holding_sessions:int=Field(ge=0)
    review_trigger:str=Field(max_length=120)

class ReentryContext(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    stop_date:str
    stop_level:float=Field(gt=0)
    original_entry_date:str

class SMCContext(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    sweep_date:str
    structure_date:str
    sweep_level:float=Field(gt=0)
    structure_level:float=Field(gt=0)
    zone_low:float=Field(gt=0)
    zone_high:float=Field(gt=0)

class CaseEvidence(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    symbol:str=Field(pattern=r'^[A-Z0-9][A-Z0-9_&-]{1,29}$')
    date:str
    regime:Literal['SMC','TREND','PULLBACK','RANGE','BREAKOUT','BREAKOUT_BOUNCE','HIGH_VOL','UNCERTAIN','WARMUP']
    Close:float=Field(gt=0)
    RSI14:float=Field(ge=0,le=100)
    ADX14:float=Field(ge=0,le=100)
    EMA20:float=Field(gt=0)
    EMA50:float=Field(gt=0)
    ATR14:float=Field(ge=0)
    PriorHigh:float|None=Field(default=None,gt=0)
    PullbackRecent:bool=False
    breakout_reentry:ReentryContext|None=None
    smc_context:SMCContext|None=None
    research_purpose:Literal['ENTRY','HOLDING_REVIEW','COMPANY_SCREEN']='ENTRY'
    holding_context:HoldingContext|None=None

    selection_score:float|None=Field(default=None,ge=0,le=100)
    selection_rank:int|None=Field(default=None,ge=1)
    average_turnover_20_inr:float|None=Field(default=None,ge=0)

    @model_validator(mode='after')
    def check_date(self):
        from datetime import date
        date.fromisoformat(self.date)
        if self.research_purpose=='HOLDING_REVIEW' and self.holding_context is None:
            raise ValueError('Holding review needs current position context')
        if self.regime=='PULLBACK' and not (self.PullbackRecent and self.PriorHigh and self.ADX14>=22 and self.Close>self.PriorHigh and self.Close>self.EMA20>self.EMA50):
            raise ValueError('Pullback requires prior pullback and completed-close rebound confirmation')
        if self.regime=='BREAKOUT_BOUNCE':
            if not self.breakout_reentry or not self.PriorHigh:raise ValueError('Breakout bounce needs its portfolio stop context')
            if not (date.fromisoformat(self.breakout_reentry.stop_date)<date.fromisoformat(self.date) and self.Close>self.breakout_reentry.stop_level and self.Close>self.EMA20 and self.Close>self.PriorHigh and self.ADX14>=18):
                raise ValueError('Breakout bounce is not confirmed after the prior stop')
        if self.research_purpose=='COMPANY_SCREEN' and (self.regime!='UNCERTAIN' or self.smc_context or self.breakout_reentry or self.PullbackRecent):
            raise ValueError('Company screening must precede strategy evidence')
        if self.regime=='SMC' and self.research_purpose=='ENTRY':
            c=self.smc_context
            if not c or not (date.fromisoformat(c.sweep_date)<date.fromisoformat(c.structure_date)<date.fromisoformat(self.date) and c.zone_low<c.zone_high<self.Close):
                raise ValueError('SMC requires an earlier sweep, later structure break and subsequent confirmed zone retest')
        return self

    @classmethod
    def from_snapshot(cls,snapshot):
        return cls.model_validate({k:snapshot[k] for k in cls.model_fields if k in snapshot})

class EmptyArgs(BaseModel):
    model_config=ConfigDict(extra='forbid')

class SearchArgs(EmptyArgs):
    query:str=Field(min_length=3,max_length=250)

class ToolResult(BaseModel):
    ok:bool
    data:dict|list|None=None
    error_code:str|None=None


def approved_route(regime):
    return {'SMC':'SMC','TREND':'EMA_TREND','PULLBACK':'EMA_PULLBACK','RANGE':'RSI_REVERSION','BREAKOUT':'BREAKOUT','BREAKOUT_BOUNCE':'BREAKOUT'}.get(regime,'NONE')


def market_observation(evidence:CaseEvidence):
    return {'ok':True,'data':evidence.model_dump(),'source':'historical research case; not a live quote'}


def strategy_observation(evidence:CaseEvidence):
    return {'ok':True,'data':{'approved_strategy':approved_route(evidence.regime),
        'permitted_portfolio_actions':['SCREEN'] if evidence.research_purpose=='COMPANY_SCREEN' else ['HOLD','EXIT'] if evidence.research_purpose=='HOLDING_REVIEW' else ['ENTER'],
        'constraint':'Code-defined research route; entry signal and risk checks remain separate.'}}
