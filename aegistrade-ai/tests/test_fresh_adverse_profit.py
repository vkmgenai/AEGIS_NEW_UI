"""New execution/research contracts. Synthetic prices and mocked generation only."""
from datetime import date
from types import SimpleNamespace
import copy
import pytest
import pandas as pd
from aegistrade.engine import TradePolicy,backtest
from aegistrade.execution_policy import protective_exit,take_profit_reference
from aegistrade.c2_portfolio import create_run,execute_run,load,save,state_path
from aegistrade.company_research import prepare_company_research,validate_company_assessment,company_pack_researchable
from aegistrade.llm_research import CompanyAssessment
from aegistrade.research_gate import validate_completed_c2
from tests.test_c2_portfolio import history,settings,runner,prepare
from tests.test_trailing_stop import rising_then_gap
from tests.company_fixtures import FakeArchive,assessment


def friday_history():
    f=history(70);f['Date']=pd.bdate_range('2024-01-08',periods=70)
    f.loc[:63,'Regime']='UNCERTAIN';f.loc[:63,'RoutedStrategy']='NONE'
    assert f.Date.iloc[64].date()==date(2024,4,5)
    return f


def test_friday_researched_on_monday_fills_tuesday(completed_c2):
    f=friday_history();cfg=settings(f,review=60).model_copy(update={'review_after_gap':True})
    seen=[];rid=create_run(f,cfg);r=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    buy=r['ledgers']['C2'][0]
    assert r['status']=='COMPLETED' and buy['date']=='2024-04-09'
    assert buy['signal_date']=='2024-04-08' and buy['original_signal_date']=='2024-04-05'
    assert [x['date'] for x in seen]==['2024-04-08']
    assert sum(d['action']=='DEFERRED_REVIEW' for d in r['decisions'])==1
    curve,events,_=backtest(f.iloc[60:],p=TradePolicy(review_after_gap=True))
    assert events.iloc[0].Date.date()==date(2024,4,9)


def test_reversed_monday_signal_cancels_friday_without_generation(completed_c2):
    f=friday_history();f.loc[65:,'Regime']='UNCERTAIN';f.loc[65:,'RoutedStrategy']='NONE'
    rid=create_run(f,settings(f).model_copy(update={'review_after_gap':True}))
    r=execute_run(rid,f,researcher=lambda *a,**kw:pytest.fail('Stale Friday entry'),preparer=prepare)
    assert not r['ledgers']['C2']
    assert any(d['action']=='ENTRY_CANCELLED' and d['date']=='2024-04-08' for d in r['decisions'])


def test_monday_holiday_review_uses_next_actual_session(completed_c2):
    f=friday_history().drop(index=65)
    rid=create_run(f,settings(f,review=60).model_copy(update={'review_after_gap':True}));seen=[]
    r=execute_run(rid,f,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    assert seen[0]['date']=='2024-04-09' and r['ledgers']['C2'][0]['date']=='2024-04-10'


def test_budget_pause_preserves_friday_origin_and_does_not_repeat_deferral(completed_c2):
    f=friday_history();rid=create_run(f,settings(f,review=60).model_copy(update={'review_after_gap':True}))
    s=load(rid);s['call_limit']=0;save(state_path(rid),s)
    first=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert first['status']=='PAUSED_BUDGET' and first['progress']['current_date']=='2024-04-08'
    s=load(rid);s['call_limit']=8;save(state_path(rid),s)
    final=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert sum(d['action']=='DEFERRED_REVIEW' for d in final['decisions'])==1
    assert final['ledgers']['C2'][0]['original_signal_date']=='2024-04-05'
    assert final['model_usage']['attempted_calls']==6


def test_profit_target_is_net_of_fees_and_slippage():
    p=TradePolicy(fee_bps=10,slippage_bps=10,take_profit_percent=8)
    pos={'quantity':10,'entry_price':100.,'entry_fee':1.,'stop':90.,'initial_stop':90.}
    target=take_profit_reference(pos,p)
    event,ref=protective_exit(pos,SimpleNamespace(Open=100,Low=99,High=target,Close=105),p)
    proceeds=10*ref*.999*.999
    assert event=='SELL_TAKE_PROFIT' and proceeds/1001-1==pytest.approx(.08)
    event,ref=protective_exit(pos,SimpleNamespace(Open=120,Low=80,High=125),p)
    assert event=='SELL_TAKE_PROFIT' and ref==120  # Open precedes later low.
    event,ref=protective_exit(pos,SimpleNamespace(Open=100,Low=85,High=125),p)
    assert event=='SELL_STOP' and ref==90  # Ambiguous intraday order: conservative.


@pytest.mark.parametrize('mode',['profit','stop','opening_gap'])
def test_c2_profit_and_stop_precedence_with_accounting(completed_c2,mode):
    f=rising_then_gap().iloc[:62 if mode!='opening_gap' else 63].copy()
    if mode=='stop':f.loc[61,'Low']=100.
    if mode=='opening_gap':
        f.loc[61,['High','Close']]=[116.,115.]
        f.loc[62,['Open','Low','High','Close']]=[125.,100.,126.,123.]
    rid=create_run(f,settings(f,review=60,trailing=True).model_copy(update={'take_profit_percent':8.}))
    r=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    sold=next(x for x in r['ledgers']['C2'] if x['event'].startswith('SELL'))
    assert sold['event']==('SELL_STOP' if mode=='stop' else 'SELL_TAKE_PROFIT')
    if mode=='opening_gap':assert sold['price']==pytest.approx(125*.999)
    if mode=='profit':
        b=r['ledgers']['C2'][0];cost=b['price']*b['quantity']+b['fee']
        assert sold['realized_pnl']/cost==pytest.approx(.08)
    assert abs(r['accounting']['equity_identity_error'])<1e-7
    assert r['accounting']['forced_end_liquidation'] is False


class EmptyArchive(FakeArchive):
    def announcements(self,*a):return []


def limited(pack,adverse='NO_MATERIAL_ADVERSE_FOUND'):
    return CompanyAssessment(status='LIMITED',adverse_risk=adverse,summary='Financial details unavailable; no material adverse found within the completed bounded issuer scan.',
        citations=[pack['adverse_scan']['citation_id']],event_risks=[],limitations=['Missing financial details and independent press; not proof of safety.'])


def test_limited_financials_can_pass_with_complete_cited_adverse_scan():
    pack=prepare_company_research('DEMO','2024-04-08',provider=EmptyArchive())
    assert pack['status']=='INSUFFICIENT_EVIDENCE' and pack['adverse_scan']['ready']
    assert company_pack_researchable(pack)
    assert validate_company_assessment(limited(pack),pack)
    for risk in ['MATERIAL_ADVERSE','UNKNOWN']:
        with pytest.raises(ValueError):validate_company_assessment(limited(pack,risk),pack)
    wrong=limited(pack);wrong.citations=['SCAN-fabricated']
    with pytest.raises(ValueError):validate_company_assessment(wrong,pack)
    partial=copy.deepcopy(pack);partial['adverse_scan']['ready']=False
    assert not company_pack_researchable(partial)
    with pytest.raises(ValueError):validate_company_assessment(limited(pack),partial)


def test_limited_c2_gate_records_scan_source_and_requires_independent_critic(completed_c2):
    snapshot={'symbol':'DEMO','date':'2024-04-08','regime':'TREND','approved_candidate':'EMA_TREND',
        'Close':110.,'EMA20':100.,'EMA50':95.,'RSI14':55.,'ADX14':30.,'ATR14':2.}
    out=completed_c2(snapshot)
    pack=prepare_company_research('DEMO',snapshot['date'],provider=EmptyArchive(),refresh=True)
    company=limited(pack).model_dump();out['company_research']=pack;out['company_assessment']=company
    out['handoffs']['market']['payload']['company']=company
    for t in out['tool_trace']:
        if t['tool']=='company_evidence':t['observation']=pack
    verified=validate_completed_c2(out)
    assert verified['company_assessment']['status']=='LIMITED'
    assert verified['company_sources'][0]['id']==pack['adverse_scan']['citation_id']
    out['tool_trace']=[t for t in out['tool_trace'] if t.get('agent')!='critic']
    with pytest.raises(ValueError):validate_completed_c2(out)


class RiskArchive(FakeArchive):
    def announcements(self,symbol,start,end):
        rows=super().announcements(symbol,start,end)
        if end==date(2024,4,8):
            row=rows[0].copy();row.update(desc='Fraud investigation and regulatory action',attchmntFile='https://nsearchives.nseindia.com/corporate/RISK.pdf');rows.append(row)
        return rows


def test_material_adverse_is_retrieved_and_cannot_pass_an_entry():
    pack=prepare_company_research('DEMO','2024-04-08',provider=RiskArchive())
    assert pack['adverse_scan']['ready'] and pack['adverse_scan']['candidate_count']>0
    risk=next(d for d in pack['documents'] if 'Fraud' in d['title'])
    a=CompanyAssessment(**{**assessment(pack),'status':'REVIEW_REQUIRED','adverse_risk':'MATERIAL_ADVERSE',
        'citations':[risk['id']],'event_risks':['Cited fraud investigation.']})
    with pytest.raises(ValueError):validate_company_assessment(a,pack)
    assert validate_company_assessment(a,pack,allow_review_required=True)


class WeekendArchive(FakeArchive):
    def announcements(self,symbol,start,end):
        rows=super().announcements(symbol,start,end)
        if start<=date(2024,4,7)<=end:
            rows.append({'symbol':symbol,'an_dt':'07-Apr-2024 12:00:00','desc':'Fraud investigation',
                'attchmntText':'Weekend material adverse disclosure',
                'attchmntFile':'https://nsearchives.nseindia.com/corporate/WEEKEND.pdf'})
        return rows


def test_weekend_adverse_evidence_is_visible_on_monday_not_friday():
    friday=prepare_company_research('DEMO','2024-04-05',provider=WeekendArchive())
    monday=prepare_company_research('DEMO','2024-04-08',provider=WeekendArchive())
    assert not any('Fraud' in d['title'] for d in friday['documents'])
    assert any('Fraud' in d['title'] for d in monday['documents'])
    assert all(d['available_at']<=monday['decision_at'] for d in monday['documents'])


class CrowdedRiskArchive(FakeArchive):
    def announcements(self,symbol,start,end):
        rows=super().announcements(symbol,start,end)
        if end==date(2024,4,8):
            for i in range(9):
                row=rows[0].copy();row.update(desc='Fraud investigation',attchmntFile=f'https://nsearchives.nseindia.com/corporate/RISK{i}.pdf');rows.append(row)
        return rows


def test_risk_attachment_bound_does_not_become_a_false_clean_scan():
    pack=prepare_company_research('DEMO','2024-04-08',provider=CrowdedRiskArchive())
    assert pack['adverse_scan']['candidate_count']==9 and not pack['adverse_scan']['ready']
    with pytest.raises(ValueError):validate_company_assessment(limited(pack),pack)


class NewsArchive(FakeArchive):
    def announcements(self,*args):
        rows=super().announcements(*args)
        for row in rows:row['desc']='Issuer news release'
        return rows


@pytest.mark.parametrize('config',['C1','C2'])
def test_actual_agent_graph_accepts_limited_adverse_review(monkeypatch,config):
    import json
    from tests.test_agentic import SNAPSHOT,LocalTools,fake_team
    from aegistrade.llm_research import RouterClient
    from aegistrade.agentic import run_agentic_case
    pack=prepare_company_research('DEMO',SNAPSHOT['date'],provider=NewsArchive())
    def reply(self,messages,**kwargs):
        answer=fake_team(self,messages,**kwargs)
        if answer.get('content'):
            value=json.loads(answer['content'])
            if 'company' in value:value['company']=limited(pack).model_dump()
            answer['content']=json.dumps(value)
        return answer
    monkeypatch.setattr(RouterClient,'chat',reply)
    out=run_agentic_case(SNAPSHOT,config,tools_factory=LocalTools)
    assert out['guard_pass'],out['model_errors']
    assert out['company_assessment']['status']=='LIMITED'
    assert out['llm_calls']==(6 if config=='C2' else 2)


def test_friday_candidate_is_blocked_by_weekend_adverse_disclosure(monkeypatch):
    import json
    from tests.test_agentic import LocalTools,fake_team
    from aegistrade.llm_research import RouterClient
    from aegistrade.agentic import run_agentic_case
    f=friday_history()
    def prepare_weekend(symbol,day):return prepare_company_research(symbol,day,provider=WeekendArchive())
    def reply(self,messages,**kwargs):
        answer=fake_team(self,messages,**kwargs)
        if answer.get('content'):
            value=json.loads(answer['content'])
            if 'company' in value:
                value['company'].update(status='REVIEW_REQUIRED',adverse_risk='MATERIAL_ADVERSE',event_risks=['Cited weekend fraud investigation.'])
            answer['content']=json.dumps(value)
        return answer
    monkeypatch.setattr(RouterClient,'chat',reply)
    def research(snapshot,*args,**kwargs):return run_agentic_case(snapshot,tools_factory=LocalTools)
    rid=create_run(f,settings(f).model_copy(update={'review_after_gap':True}))
    r=execute_run(rid,f,researcher=research,preparer=prepare_weekend)
    assert not r['ledgers']['C2']
    first=next(d for d in r['decisions'] if d['action']=='BLOCKED')
    assert first['date']=='2024-04-08' and first['llm_calls']==2


def test_partial_monday_review_resume_does_not_cancel_already_accepted_entry(completed_c2):
    f=friday_history();other=f.copy();other['Symbol']='OTHER';f=pd.concat([f,other],ignore_index=True)
    rid=create_run(f,settings(f,review=60,budget=8).model_copy(update={'review_after_gap':True}))
    first=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert first['status']=='PAUSED_BUDGET' and len(first['pending_orders'])==1
    accepted=first['pending_orders'][0]['symbol']
    s=load(rid);s['call_limit']=80;save(state_path(rid),s)
    final=execute_run(rid,f,researcher=runner(completed_c2),preparer=prepare)
    assert not any(d['action']=='ENTRY_CANCELLED' and d['symbol']==accepted for d in final['decisions'])
    buys=[d for d in final['ledgers']['C2'] if d['event']=='BUY']
    assert len(buys)==2 and all(d['date']=='2024-04-09' for d in buys)


def test_missing_friday_bar_cannot_carry_thursday_buy_into_monday_open(completed_c2):
    f=friday_history();f.loc[63,'Regime']='TREND';f.loc[63,'RoutedStrategy']='EMA_TREND'
    other=f.copy();other['Symbol']='OTHER';other['Volume']=1
    frame=pd.concat([f.drop(index=64),other],ignore_index=True)
    rid=create_run(frame,settings(frame,review=60).model_copy(update={'review_after_gap':True}));seen=[]
    r=execute_run(rid,frame,researcher=runner(completed_c2,seen=seen),preparer=prepare)
    buy=next(d for d in r['ledgers']['C2'] if d['event']=='BUY')
    assert buy['date']=='2024-04-09' and buy['signal_date']=='2024-04-08'
    assert buy['original_signal_date']=='2024-04-04'
    assert [d['date'] for d in seen]==['2024-04-04','2024-04-08']
