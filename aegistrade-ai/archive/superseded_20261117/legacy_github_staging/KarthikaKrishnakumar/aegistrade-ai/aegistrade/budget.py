"""Budget and tool-call counters. Set small defaults until OpenRouter allowance is known."""
from __future__ import annotations
from dataclasses import dataclass,field

@dataclass
class RunBudget:
    max_tool_calls:int=20
    max_llm_calls:int=2
    max_estimated_tokens:int=2500
    tool_calls:int=0
    llm_calls:int=0
    estimated_tokens:int=0
    log:list=field(default_factory=list)
    def before_tool(self,name:str,permission:str='read'):
        if self.tool_calls >= self.max_tool_calls: raise RuntimeError('Tool-call budget reached')
        if permission=='write' and name not in {'submit_simulated_order','record_approved_lesson'}:
            raise PermissionError('Unauthorized write tool')
        self.tool_calls += 1
        self.log.append({'event':'pre-tool','name':name,'permission':permission})
    def after_tool(self,name:str,status:str):
        self.log.append({'event':'post-tool','name':name,'status':status})
    def before_llm(self,estimate:int=0):
        if self.llm_calls >= self.max_llm_calls or self.estimated_tokens+estimate>self.max_estimated_tokens:
            raise RuntimeError('LLM budget reached')
        self.llm_calls += 1; self.estimated_tokens += estimate
