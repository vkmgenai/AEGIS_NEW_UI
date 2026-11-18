"""Read-only typed market-data MCP server; synthetic dataset by default."""
from functools import lru_cache
import pandas as pd
import os
from fastmcp import FastMCP
from aegistrade.market import load_configured_market

mcp = FastMCP("AegisTrade Market Data (READ ONLY)")

def _data():
    return load_configured_market()

@mcp.tool
def list_symbols() -> list[str]:
    """READ: Return available research market symbols."""
    return sorted(_data().Symbol.unique().tolist())

@mcp.tool
def get_daily_bar(symbol: str, signal_date: str) -> dict:
    """READ: Return an OHLCV bar on a YYYY-MM-DD date or structured not-found error."""
    f=_data()
    try:
        when=pd.Timestamp(signal_date)
    except (ValueError, TypeError):
        return {"ok":False,"error":"INVALID_DATE","symbol":symbol,"signal_date":signal_date}
    x=f.loc[(f.Symbol==symbol)&(f.Date==when)]
    if x.empty:
        return {"ok":False,"error":"BAR_NOT_FOUND","symbol":symbol,"signal_date":signal_date}
    return {"ok":True,"bar":{k:(float(x.iloc[0][k]) if k in {"Open","High","Low","Close","Volume"} else str(x.iloc[0][k]))
                              for k in ["Date","Symbol","Open","High","Low","Close","Volume"]}}

from aegistrade.agent_tools import CaseEvidence, market_observation

@mcp.tool
def assess_case(evidence: CaseEvidence) -> dict:
    """READ/COMPUTE: Validate and inspect the selected case; no future labels or writes."""
    return market_observation(evidence)

@mcp.tool
def company_evidence(symbol:str,signal_date:str) -> dict:
    """READ: Historical cached filings/issuer news known by 15:30 IST; never download or use future news."""
    from aegistrade.company_research import read_company_research
    try:return read_company_research(symbol,signal_date)
    except (ValueError,KeyError,TypeError,OSError):
        return {'ok':False,'error_code':'INVALID_COMPANY_EVIDENCE','message':'Prepare and verify company evidence for this exact symbol/date.'}

@mcp.tool
def search_dated_web(evidence:CaseEvidence) -> dict:
    """READ: Bounded financial/adverse public search, fetched-source date checks and cached dated evidence. No broker/LLM calls."""
    from aegistrade.dated_web import search_and_enrich
    return search_and_enrich(evidence.model_dump())


if __name__=="__main__":
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
