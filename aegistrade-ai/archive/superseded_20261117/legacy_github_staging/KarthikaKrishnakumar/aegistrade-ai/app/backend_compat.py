"""UI/API contract compatibility, independent of routine patch releases."""
import re

UI_API_CONTRACT=1


def compatible_backend(health):
    contract=health.get('ui_api_contract')
    if contract is not None:return type(contract) is int and contract==UI_API_CONTRACT
    # Older 0.16 backends have the same contract but predate its explicit field.
    version=health.get('version','')
    if not isinstance(version,str) or not re.fullmatch(r'0\.16\.\d+',version):return False
    return (isinstance(health.get('inference'),dict) and health.get('c2_required_before_order') is True
            and health.get('company_research_required') is True)
