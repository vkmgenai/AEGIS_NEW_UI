"""Export actual MCP schemas without connecting any tool to an LLM."""
import asyncio,json
from pathlib import Path
from fastmcp import Client

async def main():
    from mcp_servers import market_server,strategy_server,risk_server,knowledge_server,records_server,action_server
    inventory=[]
    for module in [market_server,strategy_server,risk_server,knowledge_server,records_server,action_server]:
        async with Client(module.mcp) as client:
            for t in await client.list_tools():
                inventory.append({'server':module.__name__,'name':t.name,
                    'permission':'write' if t.name=='submit_simulated_order' else 'read/compute',
                    'exposed_to_llm':t.name in {'assess_case','company_evidence','check_case_strategy','search_policy'},
                    'description':t.description,'input_schema':t.inputSchema,
                    'output_schema':t.outputSchema})
    path=Path('docs/MCP_TOOL_INVENTORY.json');path.write_text(json.dumps(inventory,indent=2))
    print(f'Exported {len(inventory)} tool schemas to {path}')
if __name__=='__main__':asyncio.run(main())
