"""Breakout support must be substantive, quoted, current and independently read."""
from copy import deepcopy
from datetime import datetime,timedelta
import json
import pytest
from aegistrade.breakout_evidence import (validate_breakout_evidence,validate_breakout_critic,
    validate_entry_price_comparability)
from aegistrade.company_research import validate_company_assessment
from aegistrade.llm_research import CompanyAssessment,BreakoutEvidence,CriticJudgement,RouterClient
from aegistrade.research_gate import validate_completed_c2
from tests.company_fixtures import pack_for,assessment,BREAKOUT_QUOTE,BreakoutArchive
from tests.test_signal_evidence import BREAKOUT,TREND,RSI


def evidence(pack,quote=BREAKOUT_QUOTE,kind='EARNINGS_IMPROVEMENT'):
    return BreakoutEvidence(document_id=pack['documents'][0]['id'],kind=kind,quote=quote,
        relevance='Synthetic reported improvement supplies current corroborating issuer context, not a price forecast.')


def test_readable_filing_and_nonempty_prose_are_no_longer_enough():
    pack=pack_for(BREAKOUT);a=CompanyAssessment(**assessment(pack));a.breakout_support='A readable dated company filing exists.'
    with pytest.raises(ValueError,match='structured'):validate_company_assessment(a,pack,snapshot=BREAKOUT)
    a.breakout_evidence=evidence(pack)
    assert validate_company_assessment(a,pack,snapshot=BREAKOUT)


def test_changed_financial_value_in_quote_is_rejected():
    pack=pack_for(BREAKOUT)
    with pytest.raises(ValueError,match='verbatim'):
        validate_breakout_evidence(evidence(pack,quote=BREAKOUT_QUOTE.replace('120.00','129.00')),pack)


@pytest.mark.parametrize('days',[-31,1])
def test_stale_or_future_source_cannot_corroborate_breakout(days):
    pack=pack_for(BREAKOUT);pack['documents'][0]['available_at']=(datetime.fromisoformat(pack['decision_at'])+timedelta(days=days)).isoformat()
    with pytest.raises(ValueError,match='30 days'):validate_breakout_evidence(evidence(pack),pack)


@pytest.mark.parametrize('quote,kind',[
    ('The selected provider will review the field and has indicated production gains up to 60% over ten years.','OPERATING_IMPROVEMENT'),
    ('A technical provider has been selected for a project valued at INR 120.00 crore after bid evaluation.','COMPLETED_COMMERCIAL_EVENT'),
    ('The company completed bid evaluation for a project worth INR 120.00 crore and selected a provider.','COMPLETED_COMMERCIAL_EVENT'),
    ('The auditors reviewed financial statements with total revenue of INR 120.00 crore and income of INR 140.00 crore.','EARNINGS_IMPROVEMENT')])
def test_forecasts_selection_and_auditor_context_are_not_reported_improvement(quote,kind):
    pack=pack_for(BREAKOUT);pack['documents'][0]['excerpt']=quote
    with pytest.raises(ValueError):validate_breakout_evidence(evidence(pack,quote=quote,kind=kind),pack)


def test_completed_order_with_visible_benefit_metric_can_qualify():
    quote='The company has been awarded a supply order worth INR 120.00 crore from a new industrial customer.'
    pack=pack_for(BREAKOUT);pack['documents'][0]['excerpt']=quote
    assert validate_breakout_evidence(evidence(pack,quote=quote,kind='COMPLETED_COMMERCIAL_EVENT'),pack)


def test_reported_improvement_in_may_is_not_confused_with_a_forecast():
    quote='Revenue increased by 20% to INR 120.00 crore in May compared with the preceding year.'
    pack=pack_for(BREAKOUT);pack['documents'][0]['excerpt']=quote
    assert validate_breakout_evidence(evidence(pack,quote=quote),pack)


@pytest.mark.parametrize('snapshot',[BREAKOUT,TREND,RSI])
def test_known_recent_demerger_quarantines_unadjusted_entries_without_looking_ahead(snapshot):
    pack=pack_for(snapshot)
    pack['documents'].append({'id':'CMP-ACTION','kind':'announcement','title':'General update on demerger of a business',
        'extraction_status':'readable','available_at':pack['decision_at'],'excerpt':'A structural action is disclosed; no distributed-share accounting is implemented.'})
    with pytest.raises(ValueError,match='quarantined'):validate_entry_price_comparability(pack,snapshot)
    # It is not classified as adverse news or forced liquidation of an existing holding.
    validate_entry_price_comparability(pack,{**snapshot,'research_purpose':'HOLDING_REVIEW'})
    pack['documents'][-1]['available_at']=(datetime.fromisoformat(pack['decision_at'])+timedelta(days=1)).isoformat()
    validate_entry_price_comparability(pack,snapshot)  # A future disclosure cannot veto a past entry.


def test_critic_acceptance_without_own_source_quote_is_insufficient(completed_c2):
    out=completed_c2(BREAKOUT)
    assert validate_completed_c2(out)['validated_c2']
    out['handoffs']['critic']['payload'].pop('breakout_evidence')
    with pytest.raises(ValueError,match='independently'):validate_completed_c2(out)


def test_full_title_structural_metadata_survives_display_title_truncation():
    from pathlib import Path
    from aegistrade.company_research import pack_path,_persist_pack,read_company_research
    pack_for(BREAKOUT);path=pack_path(BREAKOUT['symbol'],BREAKOUT['date']);raw=json.loads(path.read_text())
    doc={**raw['documents'][0],'id':'CMP-LONG-ACTION','kind':'announcement',
        'source_url':'https://nsearchives.nseindia.com/corporate/LONG_ACTION.pdf',
        'title':('Company disclosure metadata ' * 12)+'Demerger of a business',
        'available_at':raw['decision_at']}
    raw['documents'].append(doc);_persist_pack(path,raw)
    pack=read_company_research(BREAKOUT['symbol'],BREAKOUT['date'])
    displayed=next(d for d in pack['documents'] if d['id']==doc['id'])
    assert 'Demerger' not in displayed['title']
    assert any(d['id']==doc['id'] for d in pack['structural_action_documents'])
    with pytest.raises(ValueError,match='quarantined'):validate_entry_price_comparability(pack,BREAKOUT)


def test_critic_must_verify_same_source_not_an_unrelated_readable_filing():
    pack=pack_for(BREAKOUT);a=CompanyAssessment(**assessment(pack));a.breakout_evidence=evidence(pack)
    other={**pack['documents'][0],'id':'CMP-OTHER'};pack['documents'].append(other)
    cited=evidence(pack).model_copy(update={'document_id':other['id']})
    critic=CriticJudgement(accept=True,reason='Synthetic source review.',breakout_evidence=cited)
    with pytest.raises(ValueError,match='same breakout source'):validate_breakout_critic(a,critic,pack,BREAKOUT)


@pytest.mark.parametrize('later_return',[-.5,.5])
def test_qualifying_evidence_does_not_depend_on_future_profit_or_loss(later_return):
    snapshot={**BREAKOUT,'future_return':later_return};pack=pack_for(snapshot)
    a=CompanyAssessment(**assessment(pack));a.breakout_support='Synthetic reported growth.';a.breakout_evidence=evidence(pack)
    assert validate_company_assessment(a,pack,snapshot=snapshot)


def test_portfolio_cannot_buy_even_if_a_researcher_claims_pass_without_quoted_support(completed_c2):
    from tests.test_c2_portfolio import history,settings
    from aegistrade.c2_portfolio import create_run,execute_run
    from aegistrade.company_research import prepare_company_research
    f=history(66);f['Regime']='BREAKOUT';f['RoutedStrategy']='BREAKOUT';f['Prior20High']=f.Close-1
    def prepare(symbol,day):return prepare_company_research(symbol,day,provider=BreakoutArchive())
    def invalid(snapshot,*a,**kw):
        out=completed_c2(snapshot);out['company_assessment']['breakout_evidence']=None
        out['handoffs']['market']['payload']['company']=out['company_assessment']
        return out  # Deliberate false guard_pass; independent code must reject it.
    rid=create_run(f,settings(f));out=execute_run(rid,f,researcher=invalid,preparer=prepare)
    assert not any(x['event']=='BUY' for x in out['ledgers']['C2'])
    assert any(d.get('failure',{}).get('code')=='BREAKOUT_SOURCE_QUOTE_REQUIRED' for d in out['decisions'])


def test_independent_critic_repairs_a_bare_acceptance_within_existing_budget(monkeypatch):
    from tests.test_agentic import LocalTools,call
    from aegistrade.agentic import run_agentic_case
    from aegistrade.company_research import read_company_research
    critic_answers=0
    def model(self,messages,**kwargs):
        nonlocal critic_answers
        self.calls+=1;role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if not any(m['role']=='tool' for m in messages):
            names={'market':['market_snapshot','company_evidence'],'strategy':['check_strategy','search_policy'],
                'critic':['company_evidence','check_strategy','search_policy']}[role]
            return {'tool_calls':[call(t,{'query':'breakout corroboration policy'} if t=='search_policy' else {}) for t in names]}
        pack=read_company_research(BREAKOUT['symbol'],BREAKOUT['date'])
        if role=='market':
            company=assessment(pack);company.update(breakout_support='Synthetic reported growth.',breakout_evidence=evidence(pack).model_dump())
            value={'regime':'BREAKOUT','explanation':'Synthetic breakout route with quoted support.','company':company}
        elif role=='strategy':value={'strategy':'BREAKOUT','portfolio_action':'ENTER','citations':['POL-06'],'explanation':'Synthetic permitted route.'}
        else:
            critic_answers+=1;value={'accept':True,'reason':'Synthetic independent evidence review.'}
            if critic_answers==2:
                assert 'independently quote' in messages[-1]['content'];value['breakout_evidence']=evidence(pack).model_dump()
        return {'content':json.dumps(value)}
    monkeypatch.setattr(RouterClient,'chat',model)
    out=run_agentic_case(BREAKOUT,tools_factory=LocalTools);out['snapshot']=BREAKOUT
    assert out['guard_pass'],out['model_errors']
    assert out['llm_calls']==7 and any(e.get('code')=='BREAKOUT_CRITIC_EVIDENCE_REQUIRED' for e in out['trajectory'])
    assert validate_completed_c2(out)['validated_c2']
