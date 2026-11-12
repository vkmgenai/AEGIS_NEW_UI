"""Deterministic checks on visible dated corroboration, not a price prediction."""
from datetime import datetime,timedelta
import re

MAX_SOURCE_AGE_DAYS=30
STRUCTURAL_ACTION=re.compile(r'\bdemerg\w*|\b(?:stock|share)\s+split|\bsplit\s+of\s+shares|\bsub[ -]?division|\bbonus\s+(?:issue|shares)|\brights\s+issue|\bcapital\s+reduction',re.I)
FORECAST=re.compile(r'\b(?:will|would|could|expected|expects|forecast\w*|target\w*|propos\w*|intend\w*|planned|plans|indicated|potential|anticipated|estimated)\b|\bup\s+to\b|\bmay\s+(?:be|increase|rise|grow|improve|result|lead|achieve|generate|deliver|benefit)\b',re.I)
IMPROVEMENT=re.compile(r'\b(?:grew|grown|rose|risen|increased|improved|higher|growth)\b|\brecord[ -](?:high|revenue|profit|production|output|sales)\b',re.I)
BENEFIT_METRIC=re.compile(r'(?:₹|\bINR\b|\bUSD\b|\bRs\.?)\s*\d|\d[\d,.]*\s*(?:%|crore|million|billion|MW\b|GW\b|tonnes?\b|barrels?\b)',re.I)


def normalized(text):return ' '.join(str(text).split())


def source_is_recent(doc,pack):
    try:
        cutoff=datetime.fromisoformat(pack['decision_at']);available=datetime.fromisoformat(doc['available_at'])
        return cutoff-timedelta(days=MAX_SOURCE_AGE_DAYS)<=available<=cutoff
    except (KeyError,ValueError,TypeError):return False


def structural_action_sources(pack):
    """Known recent non-financial disclosures, not a complete action calendar."""
    candidates=[*pack.get('structural_action_documents',[]),*pack.get('documents',[])]
    return sorted({d['id'] for d in candidates if d.get('extraction_status')=='readable'
        and d.get('kind') not in {'financial_results','annual_report'} and source_is_recent(d,pack)
        and STRUCTURAL_ACTION.search(d.get('title',''))})


def validate_entry_price_comparability(pack,snapshot):
    if snapshot.get('research_purpose','ENTRY')=='ENTRY' and structural_action_sources(pack):
        raise ValueError('Recent structural corporate action is unresolved on unadjusted prices; entry is quarantined')


def visible_windows(doc):
    fields=doc.get('materiality',{})
    return [doc.get('excerpt',''),fields.get('disclosure_context',''),
            *[w.get('text','') for w in fields.get('source_windows',[])]]


def validate_breakout_evidence(evidence,pack,*,citations=None):
    if evidence is None:raise ValueError('Breakout requires structured source-linked corroboration')
    docs={d['id']:d for d in pack.get('documents',[]) if d.get('extraction_status')=='readable'}
    doc=docs.get(evidence.document_id)
    if not doc or (citations is not None and evidence.document_id not in citations):
        raise ValueError('Breakout corroboration must cite an observed readable company document')
    if not source_is_recent(doc,pack):raise ValueError('Breakout corroboration must be available within the last 30 days and before the cutoff')
    quote=normalized(evidence.quote)
    if not any(quote in normalized(text) for text in visible_windows(doc)):
        raise ValueError('Breakout quote is not verbatim visible source evidence')
    if STRUCTURAL_ACTION.search(doc.get('title','')+' '+quote):
        raise ValueError('Structural corporate actions cannot corroborate a breakout on this raw-price simulator')
    if FORECAST.search(quote):raise ValueError('Plans, forecasts or prospective benefits cannot be the sole breakout corroboration')
    if re.search(r'\b(?:no|not|without)\b.{0,50}\b(?:growth|increase|improv\w*|completed|awarded)\b',quote,re.I):
        raise ValueError('Breakout source does not report the claimed improvement or completed commercial event')
    if not BENEFIT_METRIC.search(quote):raise ValueError('Breakout corroboration requires an explicit reported benefit metric')
    if evidence.kind=='EARNINGS_IMPROVEMENT':
        supported=IMPROVEMENT.search(quote) and re.search(r'\brevenue|\bprofit|\bearnings|\bEBITDA',quote,re.I)
    elif evidence.kind=='OPERATING_IMPROVEMENT':
        supported=IMPROVEMENT.search(quote) and re.search(r'\bproduction|\boutput|\bcapacity|\bvolume|\bsales',quote,re.I)
    else:
        contract=re.search(r'\b(?:signed|executed|awarded|secured)\b.{0,65}\b(?:contract|order|agreement)\b|\b(?:contract|order|agreement)\b.{0,65}\b(?:signed|executed|awarded|secured)\b',quote,re.I)
        completed=re.search(r'\b(?:completed|commissioned)\s+(?:(?:the|a|an|its|new|commercial|manufacturing|production|of|construction)\s+){0,5}(?:plant|facility|project|acquisition)\b',quote,re.I)
        supported=contract or completed
    if not supported:raise ValueError('Breakout source does not report the claimed improvement or completed commercial event')
    return True


def validate_breakout_critic(company,critic,pack,snapshot):
    if snapshot.get('regime')!='BREAKOUT' or snapshot.get('research_purpose','ENTRY')!='ENTRY':return
    if not critic.accept:return
    if critic.breakout_evidence is None:raise ValueError('Breakout critic must independently quote and corroborate the supporting source')
    validate_breakout_evidence(critic.breakout_evidence,pack)
    if company.breakout_evidence is None or critic.breakout_evidence.document_id!=company.breakout_evidence.document_id:
        raise ValueError('Market and critic must corroborate the same breakout source')
