"""Strategy-specific coverage policy and causal adverse-news exits. No live calls."""
from copy import deepcopy
from datetime import date
import json
import pytest
from aegistrade.company_research import (validate_company_assessment,read_company_research,
    prepare_company_research,pack_path,_persist_pack,potential_adverse,adverse_news_watch)
from aegistrade.company_excerpts import materiality_fields,announcement_excerpt
from aegistrade.dated_web import search_and_enrich
from aegistrade.llm_research import CompanyAssessment,RouterClient
from aegistrade.research_gate import validate_completed_c2
from tests.company_fixtures import pack_for,assessment,FakeArchive

TREND={'symbol':'TCS','date':'2024-04-08','regime':'TREND','approved_candidate':'EMA_TREND',
       'Close':110.,'EMA20':105.,'EMA50':100.,'ATR14':2.,'RSI14':55.,'ADX14':30.}
RSI={**TREND,'regime':'RANGE','approved_candidate':'RSI_REVERSION','RSI14':25.,'Close':95.}
BREAKOUT={**TREND,'regime':'BREAKOUT','approved_candidate':'BREAKOUT'}


class OfflineWeb:
    def search(self,q):raise OSError('Contract-test offline search')


def missing_pack(snapshot=TREND):
    pack_path(snapshot['symbol'],snapshot['date']).unlink(missing_ok=True)
    return search_and_enrich(snapshot,backend=OfflineWeb())['company_evidence']


def coverage(pack):
    return CompanyAssessment(status='LIMITED',adverse_risk='COVERAGE_LIMITED',
        summary='Technical signal qualifies; financial/news coverage is missing after bounded attempted research, with no identified concrete adverse event.',
        citations=[pack['web_scan']['citation_id']],event_risks=[],
        limitations=['Historical company coverage is incomplete; this is not a finding of safety or clean fundamentals.'])


@pytest.mark.parametrize('snapshot',[TREND,RSI])
def test_strong_technical_signal_can_pass_coverage_gap_after_attempted_research(snapshot):
    pack=missing_pack(snapshot)
    assert not pack['adverse_scan']['ready'] and pack['web_scan']['attempted_queries']==2
    assert validate_company_assessment(coverage(pack),pack,snapshot=snapshot,portfolio_action='ENTER')


def test_missing_coverage_never_becomes_a_clean_company_finding():
    pack=missing_pack();a=coverage(pack);a.adverse_risk='NO_MATERIAL_ADVERSE_FOUND'
    with pytest.raises(ValueError):validate_company_assessment(a,pack,snapshot=TREND)
    a=coverage(pack);a.event_risks=['Concrete unresolved regulatory exposure needs impact assessment.']
    with pytest.raises(ValueError):validate_company_assessment(a,pack,snapshot=TREND)
    for snapshot in [{**TREND,'ADX14':10.},BREAKOUT]:
        with pytest.raises(ValueError):validate_company_assessment(coverage(pack),pack,snapshot=snapshot)
    unattempted=deepcopy(pack);unattempted['web_scan']['attempted_queries']=0
    with pytest.raises(ValueError):validate_company_assessment(coverage(unattempted),unattempted,snapshot=TREND)


def test_coverage_gate_requires_independent_current_sources(completed_c2):
    out=completed_c2(TREND);pack=missing_pack();company=coverage(pack).model_dump()
    out['company_research']=pack;out['company_assessment']=company;out['handoffs']['market']['payload']['company']=company
    for t in out['tool_trace']:
        if t['tool']=='company_evidence':t['observation']=pack
    result=validate_completed_c2(out)
    assert result['company_assessment']['adverse_risk']=='COVERAGE_LIMITED'
    assert result['company_sources'][0]['id']==pack['web_scan']['citation_id']
    out['tool_trace']=[t for t in out['tool_trace'] if t.get('agent')!='critic']
    with pytest.raises(ValueError):validate_completed_c2(out)


def test_breakout_requires_readable_dated_corroboration_and_support():
    pack=pack_for(BREAKOUT);a=CompanyAssessment(**assessment(pack))
    with pytest.raises(ValueError,match='Breakout'):validate_company_assessment(a,pack,snapshot=BREAKOUT)
    a.breakout_support='The cited synthetic issuer results provide test-only corroborating company context.'
    assert validate_company_assessment(a,pack,snapshot=BREAKOUT)
    empty=missing_pack(BREAKOUT)
    with pytest.raises(ValueError):validate_company_assessment(coverage(empty),empty,snapshot=BREAKOUT)


def adverse_output(snapshot,completed_c2):
    out=completed_c2(snapshot);path=pack_path(snapshot['symbol'],snapshot['date']);raw=json.loads(path.read_text())
    doc={**raw['documents'][0],'id':'CMP-ADVERSE-TEST','kind':'announcement','title':'Disclosed penalty — contract test only',
         'source_url':'https://nsearchives.nseindia.com/corporate/TEST_PENALTY.pdf',
         'text':'CONTRACT TEST ONLY. Issuer reports a paid penalty of INR 10,000. Impact on financial operations: Nil, according to the issuer. No actual company fact. '*4}
    import hashlib
    doc['content_sha256']=hashlib.sha256(doc['text'].encode()).hexdigest();raw['documents'].append(doc);_persist_pack(path,raw)
    pack=read_company_research(snapshot['symbol'],snapshot['date'])
    company=CompanyAssessment(status='REVIEW_REQUIRED',adverse_risk='ADVERSE_EVENT_FOUND',
        summary='Contract-test cited small penalty; issuer reports Nil operating impact.',citations=[doc['id']],
        event_risks=['Disclosed penalty, despite small amount and issuer-reported Nil impact.'],limitations=['Synthetic contract evidence.']).model_dump()
    out.update(company_research=pack,company_assessment=company)
    out['handoffs']['market']['payload']['company']=company
    for t in out['tool_trace']:
        if t['tool']=='company_evidence':t['observation']=pack
    return out


def test_supported_adverse_news_blocks_entry_and_requires_exit_for_holdings(completed_c2):
    out=adverse_output(TREND,completed_c2)
    with pytest.raises(ValueError):validate_completed_c2(out)
    holding={**TREND,'research_purpose':'HOLDING_REVIEW','holding_context':{'quantity':2,'entry_price':100.,
        'stop_price':90.,'strategy':'EMA_TREND','holding_sessions':2,'review_trigger':'New dated adverse source'}}
    out=adverse_output(holding,completed_c2);out['portfolio_action']='HOLD';out['handoffs']['strategy']['payload']['portfolio_action']='HOLD'
    with pytest.raises(ValueError,match='EXIT'):validate_completed_c2(out,purpose='HOLDING_REVIEW')
    out['portfolio_action']='EXIT';out['handoffs']['strategy']['payload']['portfolio_action']='EXIT'
    assert validate_completed_c2(out,purpose='HOLDING_REVIEW')['portfolio_action']=='EXIT'


def test_address_fragments_are_not_amounts_and_substantive_context_survives():
    source=('General Manager\nBSE Limited\nFloor 25, Phiroze Jeejeebhoy Towers,\nMumbai 400001\nScrip Code: 532555\n'+
        'Sub.: Outcome of Board meeting\nThe board approved an interim dividend of INR 3.25 per share.\n')
    fields=materiality_fields(source)
    assert '3.25' in fields['amount_context'] and 'Towers' not in fields['amount_context']
    assert 'interim dividend' in fields['disclosure_context']
    assert materiality_fields('Phiroze Jeejeebhoy Towers, Mumbai 400001')['amount_context'] is None
    assert 'Sub.' in announcement_excerpt(source) and 'Towers' not in announcement_excerpt(source)


def test_routine_window_closure_is_not_an_adverse_candidate():
    assert not potential_adverse('Trading Window closure pursuant to Prohibition of Insider Trading Regulations',recent=True)
    assert potential_adverse('Trading window notice and fraud investigation',recent=True)
    assert potential_adverse('Closure of manufacturing plant following fire',recent=True)


def test_dated_watch_keeps_after_close_news_for_next_session_and_caches():
    class Archive:
        calls=0
        def announcements(self,*a):
            self.calls+=1
            return [{'symbol':'TCS','an_dt':'08-Apr-2024 16:00:00','desc':'Fraud investigation',
                'attchmntFile':'https://nsearchives.nseindia.com/corporate/WATCH_TEST.pdf'},
                {'symbol':'TCS','an_dt':'09-Apr-2024 10:00:00','desc':'Trading Window closure',
                'attchmntFile':'https://nsearchives.nseindia.com/corporate/ROUTINE.pdf'}]
    archive=Archive()
    same_day=adverse_news_watch('TCS','2024-04-08','2024-04-05',provider=archive)
    assert not same_day['candidates']
    next_day=adverse_news_watch('TCS','2024-04-09','2024-04-08',provider=archive)
    assert len(next_day['candidates'])==1 and next_day['candidates'][0]['available_at'].startswith('2024-04-08T16:00')
    assert adverse_news_watch('TCS','2024-04-09','2024-04-08',provider=archive)==next_day and archive.calls==2


def test_daily_news_triggers_c2_before_scheduled_review_and_sells_next_open(completed_c2):
    from tests.test_c2_portfolio import history,settings,prepare
    from aegistrade.c2_portfolio import create_run,execute_run
    f=history(66);event_day=f.Date.iloc[62].date().isoformat();sell_day=f.Date.iloc[63].date().isoformat()
    f.loc[63:,'Regime']='UNCERTAIN';f.loc[63:,'RoutedStrategy']='NONE'
    seen=[]
    def research(snapshot,*a,**kw):
        seen.append(snapshot)
        if snapshot['research_purpose']=='ENTRY':
            out=completed_c2(snapshot);out['portfolio_action']='ENTER';out['handoffs']['strategy']['payload']['portfolio_action']='ENTER';return out
        out=adverse_output(snapshot,completed_c2);out['portfolio_action']='EXIT';out['handoffs']['strategy']['payload']['portfolio_action']='EXIT';return out
    def watch(symbol,day,previous):return {'status':'CHECKED','candidates':[{'title':'Disclosed penalty'}] if day==event_day else []}
    rid=create_run(f,settings(f,review=60));out=execute_run(rid,f,researcher=research,preparer=prepare,news_monitor=watch)
    sale=next(x for x in out['ledgers']['C2'] if x['event']=='SELL_C2')
    assert sale['date']==sell_day and sale['research_id']
    review=next(x for x in seen if x['research_purpose']=='HOLDING_REVIEW')
    assert review['date']==event_day and 'New dated' in review['holding_context']['review_trigger']
    assert out['accounting']['forced_end_liquidation'] is False


def test_empty_daily_watch_uses_no_extra_generation(completed_c2):
    from tests.test_c2_portfolio import history,settings,prepare,runner
    from aegistrade.c2_portfolio import create_run,execute_run
    f=history(66);seen=[];rid=create_run(f,settings(f,review=60))
    out=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare,
        news_monitor=lambda *a:{'status':'CHECKED','candidates':[]})
    assert len(seen)==1 and out['model_usage']['attempted_calls']==6 and out['news_checks']


def test_three_specialists_can_complete_coverage_limited_entry(monkeypatch):
    from tests.test_dated_web import Tools
    from tests.test_agentic import call
    from aegistrade.agentic import run_agentic_case
    class OfflineTools(Tools):
        def __init__(self,snapshot):super().__init__(snapshot);self.backend=OfflineWeb()
    def model(self,messages,**kwargs):
        self.calls+=1;role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if not any(m['role']=='tool' for m in messages):
            names={'market':['market_snapshot','company_evidence'],'strategy':['check_strategy','search_policy'],
                'critic':['company_evidence','check_strategy','search_policy']}[role]
            return {'tool_calls':[call(t,{'query':'evidence policy'} if t=='search_policy' else {}) for t in names]}
        if role=='market':value={'regime':'TREND','explanation':'Code-qualified signal with disclosed coverage risk.',
            'company':coverage(read_company_research('TCS',TREND['date'])).model_dump()}
        elif role=='strategy':value={'strategy':'EMA_TREND','portfolio_action':'ENTER','citations':['POL-06'],
            'explanation':'Follow the qualified technical signal under the explicit incomplete-coverage policy.'}
        else:value={'accept':True,'reason':'Observed attempted coverage, no cited adverse event, qualified technical signal and correct policy.'}
        return {'content':json.dumps(value)}
    monkeypatch.setattr(RouterClient,'chat',model)
    out=run_agentic_case(TREND,tools_factory=OfflineTools);out['snapshot']=TREND
    assert out['guard_pass'],out['model_errors']
    assert out['llm_calls']==6 and set(out['handoffs'])=={'market','strategy','critic'}
    assert validate_completed_c2(out)['company_assessment']['adverse_risk']=='COVERAGE_LIMITED'


def test_specialists_correct_a_hold_on_cited_adverse_news(monkeypatch,completed_c2):
    from tests.test_dated_web import Tools
    from tests.test_agentic import call
    from aegistrade.agentic import run_agentic_case
    holding={**TREND,'research_purpose':'HOLDING_REVIEW','holding_context':{'quantity':2,'entry_price':100.,
        'stop_price':90.,'strategy':'EMA_TREND','holding_sessions':2,'review_trigger':'New adverse issuer news'}}
    prepared=adverse_output(holding,completed_c2);strategy_answers=0
    def model(self,messages,**kwargs):
        nonlocal strategy_answers
        self.calls+=1;role=messages[0]['content'].split('Role: ')[1].split(' research')[0]
        if not any(m['role']=='tool' for m in messages):
            names={'market':['market_snapshot','company_evidence'],'strategy':['check_strategy','search_policy'],
                'critic':['company_evidence','check_strategy','search_policy']}[role]
            return {'tool_calls':[call(t,{'query':'adverse news exit policy'} if t=='search_policy' else {}) for t in names]}
        if role=='market':value={'regime':'TREND','explanation':'New cited adverse disclosure.', 'company':prepared['company_assessment']}
        elif role=='strategy':
            strategy_answers+=1
            if strategy_answers==2:assert 'Cited adverse news requires EXIT' in messages[-1]['content']
            value={'strategy':'EMA_TREND','portfolio_action':'HOLD' if strategy_answers==1 else 'EXIT','citations':['POL-06'],
                'explanation':'Exit on a supported adverse event under the selected policy.'}
        else:value={'accept':True,'reason':'Readable dated cited adverse event, correct EXIT, no future data.'}
        return {'content':json.dumps(value)}
    monkeypatch.setattr(RouterClient,'chat',model)
    out=run_agentic_case(holding,tools_factory=Tools);out['snapshot']=holding
    assert out['guard_pass'],out['model_errors']
    assert out['portfolio_action']=='EXIT' and out['llm_calls']==7
    assert any(e.get('code')=='ADVERSE_EXIT_REQUIRED' for e in out['trajectory'])
    assert validate_completed_c2(out,purpose='HOLDING_REVIEW')['portfolio_action']=='EXIT'
