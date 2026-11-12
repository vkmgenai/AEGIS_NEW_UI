"""List tools from 5 read-only MCP servers using stdio adapters.

Never expose the action/write server to model tools. Run with the full env.
"""
import asyncio,sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
ROOT=Path(__file__).resolve().parents[1]
SERVERS=['market','strategy','risk','knowledge','records']
async def main():
    connections={name:{'command':sys.executable,'args':['-m',f'mcp_servers.{name}_server'],
         'transport':'stdio'} for name in SERVERS}
    client=MultiServerMCPClient(connections)
    tools=await client.get_tools()
    for t in tools:
        print(t.name,':',t.description.splitlines()[0][:90])
    assert len(tools)>=8,'Expected at least 8 registered tools'
    print('Verified MCP discovery. No write server is connected to the LLM.')
if __name__=='__main__':asyncio.run(main())
