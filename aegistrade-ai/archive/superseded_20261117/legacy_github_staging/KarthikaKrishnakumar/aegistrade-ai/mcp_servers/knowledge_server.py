"""Read-only typed MCP knowledge index. Uses offline mode unless neural is configured."""
from __future__ import annotations
import os,re
from functools import lru_cache
from fastmcp import FastMCP
from aegistrade.knowledge import get_retriever

mcp=FastMCP('AegisTrade Knowledge KB (READ ONLY)')

def index():return get_retriever()

@mcp.tool
def search_policy(query:str,top_k:int=5,as_of:str|None=None,passage_ids:list[str]|None=None) -> dict:
    """READ: Retrieve cited policy passages; each has source, date and passage id."""
    if not 3 <= len(query) <= 1500 or not 1 <= top_k <= 12:
        return {'ok':False,'error_code':'INVALID_QUERY','message':'Query must be 3-1500 chars, top_k 1-12'}
    if as_of:
        from datetime import date
        try:date.fromisoformat(as_of)
        except ValueError:return {'ok':False,'error_code':'INVALID_ASOF','message':'as_of must be YYYY-MM-DD'}
    if passage_ids and (len(passage_ids)>16 or any(not isinstance(p,str) or len(p)>64 for p in passage_ids)):
        return {'ok':False,'error_code':'INVALID_PASSAGE_IDS','message':'Use at most sixteen passage IDs'}
    requested=set(passage_ids or [])|set(re.findall(r'\b(?:POL-\d{2,}|REF-[A-Z0-9-]+)\b',query))
    if len(requested)>20:return {'ok':False,'error_code':'TOO_MANY_PASSAGE_IDS','message':'At most twenty exact IDs per query'}
    return {'ok':True,'results':index().search(query,max(top_k,len(requested)),as_of=as_of,required_ids=passage_ids),
            'as_of':as_of,'corpus_sha256':index().corpus_sha256,'retrieval_mode':index().mode}

@mcp.tool
def get_policy(passage_id:str) -> dict:
    """READ: Return one exact cited passage ID."""
    d=next((x for x in index().docs if x['id']==passage_id),None)
    return {'ok':True,'passage':d} if d else {'ok':False,'error_code':'NOT_FOUND','passage_id':passage_id}

if __name__=='__main__':
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
