"""Read-only indicator and strategy MCP server."""
from functools import lru_cache
import pandas as pd
import os
from fastmcp import FastMCP
from aegistrade.market import load_configured_market
from aegistrade.strategies import prepare_indicators, entry_signal

mcp=FastMCP("AegisTrade Strategy Engine (READ ONLY)")

def _data():
    return prepare_indicators(load_configured_market())

@mcp.tool
def evaluate_regime(symbol: str, signal_date: str) -> dict:
    """READ: Compute the code-defined regime and whether the approved routed strategy signals entry."""
    f=_data()
    try:
        when=pd.Timestamp(signal_date)
    except (ValueError, TypeError):
        return {"ok":False,"error":"INVALID_DATE"}
    x=f[(f.Symbol==symbol)&(f.Date==when)]
    if x.empty:return {"ok":False,"error":"BAR_NOT_FOUND"}
    r=x.iloc[0]
    return {"ok":True,"symbol":symbol,"date":signal_date,"regime":str(r.Regime),
            "strategy":str(r.RoutedStrategy),"entry_signal":entry_signal(r,str(r.RoutedStrategy)),
            "indicators":{k:(float(getattr(r,k)) if pd.notna(getattr(r,k)) else None)
                          for k in ("EMA20","EMA50","RSI14","ATR14","ADX14")}}

from aegistrade.agent_tools import CaseEvidence, strategy_observation

@mcp.tool
def check_case_strategy(evidence: CaseEvidence) -> dict:
    """READ/COMPUTE: Validate and inspect the selected case; no future labels or writes."""
    return strategy_observation(evidence)

if __name__=="__main__":
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
