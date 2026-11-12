"""Shared typed contracts for local MCP and agent research tools. No gold labels."""
from __future__ import annotations
import math
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class HoldingContext(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    quantity:int=Field(gt=0)
    entry_price:float=Field(gt=0)
    stop_price:float=Field(gt=0)
    strategy:Literal['EMA_TREND','RSI_REVERSION','BREAKOUT']
    holding_sessions:int=Field(ge=0)
    review_trigger:str=Field(max_length=120)

class CaseEvidence(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    symbol:str=Field(pattern=r'^[A-Z0-9][A-Z0-9_&-]{1,29}$')
    date:str
    regime:Literal['TREND','RANGE','BREAKOUT','HIGH_VOL','UNCERTAIN','WARMUP']
    Close:float=Field(gt=0)
    RSI14:float=Field(ge=0,le=100)
    ADX14:float=Field(ge=0,le=100)
    EMA20:float=Field(gt=0)
    EMA50:float=Field(gt=0)
    ATR14:float=Field(ge=0)
    research_purpose:Literal['ENTRY','HOLDING_REVIEW']='ENTRY'
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
    return {'TREND':'EMA_TREND','RANGE':'RSI_REVERSION','BREAKOUT':'BREAKOUT'}.get(regime,'NONE')


def market_observation(evidence:CaseEvidence):
    return {'ok':True,'data':evidence.model_dump(),'source':'historical research case; not a live quote'}


def strategy_observation(evidence:CaseEvidence):
    return {'ok':True,'data':{'approved_strategy':approved_route(evidence.regime),
        'permitted_portfolio_actions':['HOLD','EXIT'] if evidence.research_purpose=='HOLDING_REVIEW' else ['ENTER'],
        'constraint':'Code-defined research route; entry signal and risk checks remain separate.'}}
