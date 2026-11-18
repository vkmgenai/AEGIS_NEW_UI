"""Persistent MCP sessions for one research case, local stdio or Docker HTTP.

Credentials are deliberately excluded from child-server environments.
"""
from __future__ import annotations
from contextlib import AsyncExitStack
from pathlib import Path
import os,sys,json
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from .agent_tools import CaseEvidence, EmptyArgs, SearchArgs

class ResearchTools:
    def __init__(self,snapshot,*,clients=None):
        self.evidence=CaseEvidence.from_snapshot(snapshot)
        self.clients=clients or {}
        self.stack=AsyncExitStack()
        self.required_policy_ids=()
        self.mode='inprocess-mcp' if clients else 'mcp'

    async def __aenter__(self):
        try:
            for name in ('market','strategy','knowledge'):
                if name not in self.clients:
                    url=os.getenv(f'AEGIS_{name.upper()}_MCP_URL')
                    if url:
                        target=url
                    else:
                        root=str(Path(__file__).resolve().parents[1])
                        env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','SYSTEMROOT') if k in os.environ}
                        for setting in ('AEGIS_POLICY_CORPUS_PATH','AEGIS_QDRANT_URL','AEGIS_DATA_DIR','AEGIS_DATA_SOURCE','AEGIS_NSE_DATASET_DIR','AEGIS_CHROMA_PATH','AEGIS_MODEL_CACHE','HF_HUB_OFFLINE','AEGIS_DATED_WEB_SEARCH'):
                            if os.getenv(setting):env[setting]=os.environ[setting]
                        env.update(PYTHONPATH=root,AEGIS_RETRIEVAL_MODE=os.getenv('AEGIS_RETRIEVAL_MODE','offline'))
                        target=StdioTransport(command=sys.executable,args=['-m',f'mcp_servers.{name}_server'],
                                              env=env,cwd=root,keep_alive=False)
                    self.clients[name]=Client(target,timeout=90 if name=='knowledge' else 55 if name=='market' else 25)
                await self.stack.enter_async_context(self.clients[name])
        except BaseException:
            await self.stack.aclose()
            raise
        return self

    async def __aexit__(self,*args):
        return await self.stack.__aexit__(*args)

    async def call(self,name,args):
        if name=='market_snapshot':
            EmptyArgs.model_validate(args)
            server,remote,payload='market','assess_case',{'evidence':self.evidence.model_dump()}
        elif name=='check_strategy':
            EmptyArgs.model_validate(args)
            server,remote,payload='strategy','check_case_strategy',{'evidence':self.evidence.model_dump()}
        elif name=='company_evidence':
            EmptyArgs.model_validate(args)
            server,remote,payload='market','company_evidence',{'symbol':self.evidence.symbol,'signal_date':self.evidence.date}
        elif name=='search_dated_web':
            EmptyArgs.model_validate(args)
            server,remote,payload='market','search_dated_web',{'evidence':self.evidence.model_dump()}
        elif name=='search_policy':
            parsed=SearchArgs.model_validate(args)
            server,remote,payload='knowledge','search_policy',{'query':parsed.query,'top_k':5,'as_of':self.evidence.date}
            if self.required_policy_ids:payload['passage_ids']=list(self.required_policy_ids)
        else:raise PermissionError('Tool outside read-only allowlist')
        response=await self.clients[server].call_tool(remote,payload)
        if response.is_error:raise ValueError('MCP tool returned an error')
        data=response.data
        if data is None:
            data=json.loads(''.join(getattr(c,'text','') for c in response.content))
        if hasattr(data,'model_dump'):data=data.model_dump()
        return data
