"""C1 evidence-first SMC contracts; all sources and model responses are synthetic."""
from copy import deepcopy
import json
import pandas as pd
import pytest
from aegistrade.smc import prepare_smc,screening_candidates
from aegistrade.c2_portfolio import C1PortfolioSettings,C2PortfolioSettings,create_run,execute_run,load,save,state_path,frame_for
from aegistrade.c1_gate import validate_completed_c1
from tests.test_c2_portfolio import history,prepare


def smc_history():
    f=history(73)
    f[['Open','High','Low','Close']]=[100.,102.,99.,101.]
    f.loc[59,['Open','High','Low','Close']]=[101.,102.,99.,100.]
    f.loc[60,['Open','High','Low','Close']]=[101.,102.,97.,100.]
    f.loc[61,['Open','High','Low','Close']]=[100.,102.,99.,101.5]
    f.loc[62,['Open','High','Low','Close']]=[101.,105.,100.,104.]
    f.loc[63,['Open','High','Low','Close']]=[103.5,104.,102.,103.]
    f.loc[64,['Open','High','Low','Close']]=[100.,104.,99.,103.]
    f.loc[65,['Open','High','Low','Close']]=[103.,105.,102.,104.]
    f.loc[66,['Open','High','Low','Close']]=[105.,110.,103.,108.]
    return f


def cfg(f,**kw):
    return C1PortfolioSettings(start_date=f.Date.iloc[60].date(),end_date=f.Date.iloc[-1].date(),
         consent_to_paid_calls=True,approve_historical_rules=True,review_after_gap=False,
         max_model_calls=kw.pop('max_model_calls',160),holding_review_sessions=kw.pop('holding_review_sessions',60),**kw)


def single_result(completed_c2,snapshot):
    out=completed_c2(snapshot);company=out['company_assessment']
    action='SCREEN' if snapshot['research_purpose']=='COMPANY_SCREEN' else 'HOLD'
    payload={'strategy':snapshot['approved_candidate'],'portfolio_action':action,
             'citations':out['citations'],'explanation':'Synthetic single-agent company screen; code checks the signal afterwards.','company':company}
    out.update(config='C1',portfolio_action=action,critic_accept=False,independent_critic=False,
        handoffs={'single':{'agent':'single','payload':payload,'evidence_tools':['market_snapshot','company_evidence','search_policy','check_strategy']}},llm_calls=2)
    out['tool_trace']=[{**t,'agent':'single'} for t in out['tool_trace'] if t.get('agent')!='critic']
    return out


def researcher(completed_c2,seen=None):
    def run(snapshot,config,**kw):
        assert config=='C1'
        if seen is not None:seen.append(deepcopy(snapshot))
        if snapshot['research_purpose']=='COMPANY_SCREEN':
            assert snapshot['regime']=='UNCERTAIN' and snapshot['approved_candidate']=='NONE'
            assert not snapshot.get('smc_context') and not snapshot.get('PullbackRecent')
        return single_result(completed_c2,snapshot)
    return run


def test_smc_pattern_is_later_retest_and_prefix_causal():
    f=smc_history();out=prepare_smc(f)
    assert list(out.index[out.SMCSignal])==[64]
    c=out.loc[64,'SMCContext']
    assert c['sweep_date']==str(f.Date.iloc[60].date())
    assert c['structure_date']==str(f.Date.iloc[62].date())
    assert c['zone_low']==97 and c['zone_high']==101
    for end in [61,63,65,69]:
        pd.testing.assert_frame_equal(out.iloc[:end].reset_index(drop=True),prepare_smc(f.iloc[:end]).reset_index(drop=True))
    f.loc[63,'Close']=96 # invalidate before retest
    assert not prepare_smc(f).loc[64,'SMCSignal']


def test_evidence_first_screen_does_not_select_using_smc():
    f=smc_history();c=cfg(f);prepared=frame_for(f,c,{})
    daily=prepared[prepared.Date==f.Date.iloc[64]]
    a=screening_candidates(daily,set(),4)
    changed=daily.copy();changed['SMCSignal']=False;changed['SMCContext']=None;changed['Regime']='UNCERTAIN'
    assert a==screening_candidates(changed,set(),4)
    assert a[0]['selected'] and a[0]['strategy']=='NONE'


@pytest.mark.parametrize('budget',[160,8])
def test_c1_end_to_end_company_before_smc_profit_exit_and_resume(completed_c2,budget):
    f=smc_history();seen=[];c=cfg(f,max_model_calls=budget)
    rid=create_run(f,c);r=execute_run(rid,f,researcher=researcher(completed_c2,seen),preparer=prepare)
    if budget==8:
        assert r['status']=='PAUSED_BUDGET'
        state=load(rid);state['call_limit']=160;save(state_path(rid),state)
        r=execute_run(rid,f,researcher=researcher(completed_c2,seen),preparer=prepare)
    assert r['status'].startswith('COMPLETED'),r
    ledger=r['ledgers']['C1'];buys=[x for x in ledger if x['event']=='BUY'];sells=[x for x in ledger if x['event']=='SELL_TAKE_PROFIT']
    assert len(buys)==1 and len(sells)==1
    assert buys[0]['strategy']=='SMC' and buys[0]['signal_date']==str(f.Date.iloc[64].date())
    assert buys[0]['date']==str(f.Date.iloc[65].date())
    assert buys[0]['entry_setup']=='SMC_EVIDENCE_FIRST'
    assert sells[0]['realized_pnl']/(buys[0]['price']*buys[0]['quantity']+buys[0]['fee'])==pytest.approx(.04)
    assert any(d['action']=='NO_SMC_SIGNAL' for d in r['decisions'])
    assert next(d for d in r['decisions'] if d['action']=='ENTER')['evidence_passed']
    assert r['independent_critic'] is False and r['research_order']=='EVIDENCE_BEFORE_SIGNAL'
    assert len({(s['date'],s['research_purpose']) for s in seen})==len(seen)
    assert abs(r['accounting']['equity_identity_error'])<1e-7
    assert r['comparison_valid_for_full_period'] and 'SMC_REFERENCE' in r['ledgers']


def test_missing_evidence_never_buys_despite_smc(completed_c2,monkeypatch):
    monkeypatch.setenv('AEGIS_DATED_WEB_SEARCH','false')
    f=smc_history();rid=create_run(f,cfg(f))
    r=execute_run(rid,f,researcher=lambda *a,**kw:pytest.fail('No generation for known unreadable evidence'),
         preparer=lambda *a:{'status':'INSUFFICIENT_EVIDENCE','reasons':['Synthetic missing company evidence']})
    assert not r['ledgers']['C1'] and r['model_usage']['attempted_calls']==0


def test_c1_gate_requires_single_agent_observed_dated_evidence(completed_c2):
    f=smc_history();c=cfg(f);p=frame_for(f,c,{})
    from aegistrade.c2_portfolio import case_snapshot
    b=next(p.itertuples());snap=case_snapshot(b);snap.update(regime='UNCERTAIN',approved_candidate='NONE',research_purpose='COMPANY_SCREEN',PullbackRecent=False);snap.pop('smc_context',None)
    out=single_result(completed_c2,snap)
    assert validate_completed_c1(out)['portfolio_action']=='SCREEN'
    for mutate in ['wrong_config','no_observation','wrong_action','unread_policy']:
        bad=deepcopy(out)
        if mutate=='wrong_config':bad['config']='C2'
        if mutate=='no_observation':bad['tool_trace']=[t for t in bad['tool_trace'] if t['tool']!='company_evidence']
        if mutate=='wrong_action':bad['handoffs']['single']['payload']['portfolio_action']='ENTER'
        if mutate=='unread_policy':bad['tool_trace']=[t for t in bad['tool_trace'] if t['tool']!='search_policy']
        with pytest.raises(ValueError):validate_completed_c1(bad)
    from aegistrade.research_gate import validate_completed_c2
    with pytest.raises(ValueError):validate_completed_c2(out)


def test_smc_holds_at_end_and_protective_stop_still_applies(completed_c2):
    f=smc_history();f.loc[67:,'Low']=100.;c=cfg(f,take_profit_percent=100);rid=create_run(f,c)
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert len(r['open_holdings'])==1 and not any(x['event'].startswith('SELL') for x in r['ledgers']['C1'])
    f.loc[66,['Open','Low']]=[95.,93.];rid=create_run(f,c)
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    stop=next(x for x in r['ledgers']['C1'] if x['event']=='SELL_STOP')
    assert stop['price']==pytest.approx(95*.999)


def test_c1_settings_cannot_disable_target_or_switch_flow():
    f=smc_history()
    with pytest.raises(ValueError):cfg(f,take_profit_percent=0)
    with pytest.raises(ValueError):cfg(f,mode='ROUTER')
    with pytest.raises(ValueError):C2PortfolioSettings.model_validate(cfg(f).model_dump())


def test_c1_single_agent_real_orchestration_uses_tools_before_screen(monkeypatch):
    from tests.test_agentic import LocalTools,call
    from tests.company_fixtures import assessment
    from aegistrade.llm_research import RouterClient
    from aegistrade.agentic import run_agentic_case
    snap={'symbol':'DEMO','date':'2024-04-01','regime':'UNCERTAIN','approved_candidate':'NONE',
          'research_purpose':'COMPANY_SCREEN','Close':103.,'RSI14':50.,'ADX14':25.,'EMA20':99.,'EMA50':95.,'ATR14':2.}
    def fake(self,messages,**kw):
        self.calls+=1
        if not any(m['role']=='tool' for m in messages):
            return {'tool_calls':[call(n,{'query':'SMC company screening policy'} if n=='search_policy' else {}) for n in ['market_snapshot','company_evidence','search_policy','check_strategy']]}
        pack=json.loads(next(m['content'] for m in messages if m['role']=='tool' and 'pack_sha256' in m.get('content','')))
        return {'content':json.dumps({'strategy':'NONE','portfolio_action':'SCREEN','citations':['POL-06'],
             'explanation':'Synthetic company evidence checked first; no SMC entry was assessed.','company':assessment(pack)})}
    monkeypatch.setattr(RouterClient,'chat',fake)
    out=run_agentic_case(snap,'C1',tools_factory=LocalTools);out['snapshot']=snap
    assert out['guard_pass'],out
    assert out['llm_calls']==2 and set(out['handoffs'])=={'single'}
    assert validate_completed_c1(out)['portfolio_action']=='SCREEN'


def test_c1_adverse_holding_research_exits_next_open(completed_c2):
    f=smc_history();f.loc[67:,'Low']=100.
    c=cfg(f,take_profit_percent=100,holding_review_sessions=1)
    def adverse(snapshot,config,**kw):
        out=single_result(completed_c2,snapshot)
        if snapshot['research_purpose']=='HOLDING_REVIEW':
            out['company_assessment'].update(status='REVIEW_REQUIRED',adverse_risk='ADVERSE_EVENT_FOUND',event_risks=['Synthetic adverse disclosure; contract test only.'])
            out['handoffs']['single']['payload']['portfolio_action']='EXIT';out['portfolio_action']='EXIT'
        return out
    rid=create_run(f,c);r=execute_run(rid,f,researcher=adverse,preparer=prepare)
    sold=next(x for x in r['ledgers']['C1'] if x['event']=='SELL_C1')
    decision=next(d for d in r['decisions'] if d['action']=='EXIT')
    assert sold['date']>decision['date'] and sold['research_id']==decision['id']
    assert not r['independent_critic']


def test_reviewed_newsletter_is_observed_before_smc(completed_c2,tmp_path):
    from aegistrade.company_research import prepare_company_research,import_archived_news
    from tests.company_fixtures import FakeArchive
    f=smc_history();day=str(f.Date.iloc[64].date())
    prepare_company_research('DEMO',day,provider=FakeArchive())
    excerpt={'symbol':'DEMO','kind':'newsletter','title':'Synthetic reviewed company newsletter','publisher':'Test publisher',
       'published_at':str(f.Date.iloc[63].date()),'source_url':'https://publisher.example/archived-contract-only',
       'text':'Synthetic dated licensed excerpt for a contract test, not real company news. '*4,'original_publication_verified':True}
    path=tmp_path/'newsletter.jsonl';path.write_text(json.dumps(excerpt))
    import_archived_news('DEMO',day,path,'Contract reviewer')
    observed=[]
    def run(snapshot,config,**kw):
        out=single_result(completed_c2,snapshot)
        if snapshot['date']==day:
            assert snapshot['research_purpose']=='COMPANY_SCREEN' and not snapshot.get('smc_context')
            observed.extend(d['id'] for d in out['company_research']['documents'] if d['kind']=='newsletter')
        return out
    rid=create_run(f,cfg(f));r=execute_run(rid,f,researcher=run,preparer=prepare)
    assert observed and any(x['event']=='BUY' for x in r['ledgers']['C1'])


def test_technical_smc_is_explicit_zero_generation_mode():
    from aegistrade.simulation_service import SimulationSettings,execute_simulation
    f=smc_history()
    settings=SimulationSettings(mode='SMC',start_date=f.Date.iloc[20].date(),end_date=f.Date.iloc[-1].date(),
        take_profit_percent=4,trailing_stop_enabled=False,review_after_gap=False)
    r=execute_simulation(f,settings)
    assert [m['mode'] for m in r['metrics']]==['SMC']
    assert any(x['event']=='BUY' for x in r['ledgers']['SMC'])
    assert any(x['event']=='SELL_TAKE_PROFIT' for x in r['ledgers']['SMC'])
    assert 'model_usage' not in r


@pytest.mark.parametrize('tamper',['smc_context','stop'])
def test_c1_queued_buy_revalidates_smc_and_stop_before_fill(completed_c2,tamper):
    f=smc_history();rid=create_run(f,cfg(f));fill_date=str(f.Date.iloc[65].date())
    def pause_before_fill():
        state=load(rid)
        return state['day_index']<len(state['dates']) and state['dates'][state['day_index']]==fill_date and state['phase']=='OPEN'
    first=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare,should_cancel=pause_before_fill)
    assert first['status']=='PAUSED_USER' and any(o['side']=='BUY' for o in first['pending_orders'])
    state=load(rid);order=next(o for o in state['queued'] if o['side']=='BUY')
    if tamper=='smc_context':order['smc_context']['zone_high']+=.1
    else:order['stop']+=.1
    save(state_path(rid),state)
    r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert not any(x['event']=='BUY' for x in r['ledgers']['C1'])
    assert any(d['action']=='FILL_BLOCKED' for d in r['decisions'])


def test_signal_diagnostics_follow_evidence_and_preserve_old_fingerprint(completed_c2):
    import hashlib
    from aegistrade.c2_portfolio import fingerprint
    f=smc_history();p=frame_for(f,cfg(f),{})
    old=p.drop(columns=['SMCStage'])
    assert fingerprint(p)==hashlib.sha256(old.to_json(orient='split',date_format='iso',double_precision=15).encode()).hexdigest()
    rid=create_run(f,cfg(f));r=execute_run(rid,f,researcher=researcher(completed_c2),preparer=prepare)
    assert r['research_summary']['signals_found']==1
    assert r['research_summary']['buy_fills']==1
    assert any(d['smc_stage']=='ENTRY_CONFIRMED' and d['action']=='ENTER' for d in r['signal_checks'])
    assert any(d['smc_stage']=='WAITING_SWEEP' for d in r['signal_checks'])
    assert all('Dated company screening passed.' in d['explanation'] for d in r['signal_checks'])


def test_research_activity_sidecar_updates_without_changing_allowance(completed_c2,monkeypatch):
    import aegistrade.c2_portfolio as portfolio
    f=smc_history();rid=create_run(f,cfg(f));observed=[]
    def mock(snapshot,config,progress=None,**kw):
        assert progress is not None
        progress({'event':'llm_request','agent':'single','turn':1,'ignored':'Do not persist evidence text'})
        current=json.loads((state_path(rid).parent/'activity.json').read_text())
        assert current['stage']=='LLM_REQUEST' and current['symbol']==snapshot['symbol']
        assert 'ignored' not in current
        observed.append(current)
        return single_result(completed_c2,snapshot)
    monkeypatch.setattr(portfolio,'run_agentic_case',mock)
    r=execute_run(rid,f,preparer=prepare)
    assert observed and r['activity']['stage']==r['status']
    assert r['model_usage']['call_limit']==160
