"""Read/compute risk MCP server. No trading write permission."""
import os
from fastmcp import FastMCP
from aegistrade.safety import OrderProposal, RiskInputs, RiskParameters, validate_risk

mcp=FastMCP("AegisTrade Risk Validation (COMPUTE ONLY)")

@mcp.tool
def validate_simulated_buy(order: OrderProposal, inputs: RiskInputs) -> dict:
    """READ/COMPUTE: Validate a typed proposed BUY against deterministic risk policy."""
    return validate_risk(order,inputs,RiskParameters())

@mcp.tool
def policy_summary() -> dict:
    """READ: Retrieve the demo risk parameters."""
    return RiskParameters().model_dump()

if __name__=="__main__":
    port=os.getenv('AEGIS_MCP_PORT')
    mcp.run(transport='http',host='0.0.0.0',port=int(port)) if port else mcp.run(transport='stdio')
