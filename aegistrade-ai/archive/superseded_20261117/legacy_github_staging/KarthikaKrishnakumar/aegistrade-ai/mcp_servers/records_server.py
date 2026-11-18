"""Read-only status and approved lesson MCP server. No token or write tool exposure."""
from __future__ import annotations
import os
from fastmcp import FastMCP
from aegistrade.lessons import ReviewedPlaybook
from aegistrade.safety import AuditBroker

mcp=FastMCP('AegisTrade Records (READ ONLY)')

@mcp.tool
def approved_lessons(topic:str) -> dict:
    """READ: Approved and reviewed lessons for one topic; never pending or rejected."""
    db=os.getenv('AEGIS_DATA_DIR','data')+'/reviewed_lessons.sqlite'
    return {'ok':True,'lessons':ReviewedPlaybook(db).accepted(topic)}

@mcp.tool
def simulated_order_status(request_id:str) -> dict:
    """READ: Reconcile one simulated broker order by exact id."""
    db=os.getenv('AEGIS_DATA_DIR','data')+'/simulated_orders.sqlite'
    return {'ok':True,**AuditBroker(db).reconcile(request_id)}

if __name__=='__main__':
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
