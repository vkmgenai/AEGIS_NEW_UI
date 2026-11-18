"""C0/C1/C2 experiment harness, deliberate deterministic non-LLM baselines.

Do not treat placeholder single-/multi-agent traces as measured LLM success; the
separate review report must contain the real OpenRouter configurations/results.
"""
from __future__ import annotations
from dataclasses import asdict
import json,time,statistics
import pandas as pd
from .engine import backtest, TradePolicy

CONFIGS={
    'C0_FIXED':{'mode':'EMA_TREND','description':'No dynamic routing; fixed EMA strategy'},
    'C1_SINGLE':{'mode':'ROUTER','description':'Rule based router; SINGLE-AGENT PROMPT comparator is a separate LLM experiment'},
    'C2_TEAM':{'mode':'ROUTER','description':'Rule based router; true multi-agent contribution requires workflow evaluations'},
    'RSI_FIXED':{'mode':'RSI_REVERSION','description':'Fixed RSI reference'},
    'BREAKOUT_FIXED':{'mode':'BREAKOUT','description':'Fixed breakout reference'},
}
def strategy_comparison(frame:pd.DataFrame,policy:TradePolicy|None=None) -> list[dict]:
    result=[]
    for key,config in CONFIGS.items():
        t=time.perf_counter()
        equity,events,metric=backtest(frame,config['mode'],policy)
        result.append({'config':key,'mode':config['mode'],'label':config['description'],
                       'elapsed_seconds':round(time.perf_counter()-t,3),**metric})
    return result
