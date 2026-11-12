"""RESTRICTED WRITE MCP: simulated orders only, requiring a human-issued approval token.

The graph must provision the token. An LLM should NEVER receive this server/tool directly.
"""
import os
from pathlib import Path
from fastmcp import FastMCP
from aegistrade.safety import AuditBroker, OrderProposal, RiskInputs, RiskParameters

mcp=FastMCP("AegisTrade Mock Broker (RESTRICTED WRITE)")

@mcp.tool
def order_status(request_id: str) -> dict:
    """READ: Reconcile accepted simulated order status after timeout."""
    return AuditBroker(Path(os.getenv('AEGIS_DATA_DIR','data'))/'simulated_orders.sqlite').reconcile(request_id)

@mcp.tool
def submit_simulated_order(order: OrderProposal, approval_token: str, quote_price: float,
                           quote_observed_utc: str, risk_inputs: RiskInputs) -> dict:
    """WRITE: Requires exact-payload approval + fresh quote + passing risk checks."""
    return AuditBroker(Path(os.getenv('AEGIS_DATA_DIR','data'))/'simulated_orders.sqlite').submit(order,approval_token,quote_price,quote_observed_utc,
                                                           risk_inputs,RiskParameters())

if __name__=="__main__":
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
