"""Defence in depth for EDUCATIONAL synthetic data, not a complete security boundary.

Only deterministic policy code can authorize orders. Untrusted passages are never
executed as instructions. These checks are intentionally inspectable for red-team tests.
"""
from __future__ import annotations
import re
from hmac import compare_digest

INJECTION_RULES = [
    r'ignore (?:all |the )?(?:previous|prior|system) instructions',
    r'override (?:the )?(?:risk|approval|safety|policy)',
    r'you (?:are|must act as) (?:now )?(?:system|developer|admin)',
    r'approve (?:all |this )?(?:trades|orders) automatically',
    r'disable (?:the )?(?:risk|human approval|audit|logging|guardrails)',
    r'send (?:the )?(?:api key|token|secret|password)',
    r'(?:system|developer)\s*:\s*',
    r'execute (?:python|shell|code|command)',
    r'(?:bypass|skip) (?:the )?(?:human|review|approval)',
]

class GuardResult(dict):
    pass

def scan_untrusted_text(text: str) -> GuardResult:
    text = str(text)
    matched=[p for p in INJECTION_RULES if re.search(p,text,re.IGNORECASE)]
    return GuardResult(ok=not matched, reasons=['Possible instruction injection'] if matched else [],
                       matches=matched, truncated=len(text)>6000)

def sanitize_untrusted(text: str, max_chars=3000) -> str:
    s=re.sub(r'(?i)(sk-or-[a-zA-Z0-9_-]{8,})','[REDACTED_API_KEY]',str(text))
    s=re.sub(r'(?i)(bearer\s+[a-zA-Z0-9_.-]{8,})','Bearer [REDACTED]',s)
    return s[:max_chars]

def check_reviewer_token(supplied:str, configured:str) -> bool:
    if not supplied or not configured or len(configured)<12:
        return False
    return compare_digest(str(supplied).encode(),str(configured).encode())

def verify_output_grounding(text:str, citations:list[str], required_prefix='POL-') -> dict:
    # Static check for required passage IDs; substantive support needs a calibrated judge.
    missing=[c for c in citations if c.startswith(required_prefix) and c not in text]
    return {'ok':not missing,'missing_ids':missing}
