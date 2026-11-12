"""Code-owned strategy-specific evidence policy; no generation or sizing here."""
ADVERSE_FINDINGS={'MATERIAL_ADVERSE','ADVERSE_EVENT_FOUND'}


def coverage_signal(snapshot):
    from .agent_tools import CaseEvidence
    try:e=CaseEvidence.from_snapshot(snapshot)
    except (ValueError,KeyError,TypeError):return False
    if e.research_purpose=='HOLDING_REVIEW':return e.holding_context.strategy in {'EMA_TREND','RSI_REVERSION'}
    if e.ATR14<=0:return False
    return ((e.regime=='TREND' and e.ADX14>=22 and e.Close>e.EMA20>e.EMA50) or
            (e.regime=='RANGE' and e.RSI14<42 and e.Close>.88*e.EMA50))


def coverage_reviewed(pack):
    web=pack.get('web_scan',{})
    return bool(pack.get('pack_sha256') and
        (pack.get('adverse_scan',{}).get('ready') or
         (web.get('attempted_queries')==2 and web.get('decision_at')==pack.get('decision_at'))))


def require_adverse_exit(assessment,snapshot,action):
    if (snapshot.get('research_purpose')=='HOLDING_REVIEW' and
        assessment.adverse_risk in ADVERSE_FINDINGS and action!='EXIT'):
        raise ValueError('Cited adverse news requires EXIT, not HOLD')
