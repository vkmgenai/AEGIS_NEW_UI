"""Checkpointed C2-in-the-loop historical portfolio. No broker and no forced end sale.

Each new entry needs fresh, dated completed C2. Protective/strategy exits are
pre-approved code rules; scheduled holding reviews can produce cited HOLD/EXIT.
"""
from __future__ import annotations
from .company_research import company_pack_researchable
from datetime import date,datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,math,os,threading,uuid
import pandas as pd
from pydantic import Field,model_validator
from typing import Literal
from prometheus_client import Counter
from .simulation_service import SimulationSettings,normalize,execute_simulation,policy_from_settings
from .selection import prepare_selection_features,rank_candidates
from .strategies import chosen_strategy,exit_signal
from .engine import TradePolicy,allowable_shares,performance
from .company_research import prepare_company_research,digest
from .agentic import run_agentic_case,CONFIG
from .llm_backend import identity,model_name
from .research_gate import validate_completed_c2
from .corpus import corpus_info
from .research_diagnostics import saved_failure,inference_diagnostic
from .execution_policy import protective_exit,take_profit_reference,defer_entry_review,initial_stop_price,initial_stop_settings,policy_for_strategy,position_policy_record,strategy_policy_records
from .trailing_stop import advance_trailing_stop,stop_exit_reason
from . import portfolio_memory
from .dated_web import eligible as web_eligible
from .breakout_reentry import register_breakout_stop,reentry_candidates,reentry_context

VERSION='portfolio-v7-c1-smc-evidence-first'
model_calls_total=Counter('aegis_c2_portfolio_model_calls_total','Known inference units in C2 historical portfolios; backend determines unit')
uncertain_calls_total=Counter('aegis_c2_portfolio_uncertain_calls_total','Conservative call reservations after interrupted responses')
completed_total=Counter('aegis_c2_portfolios_completed_total','Completed C2 historical windows, including coverage gaps')

class C2PortfolioSettings(SimulationSettings):
    research_flow:Literal['C2']='C2'
    portfolio_playbook_id:str|None=Field(default=None,pattern=r'^[0-9a-f]{32}$')
    memory_allow_development_replay:bool=False
    mode:str='ROUTER'
    consent_to_paid_calls:bool=False
    approve_historical_rules:bool=False
    max_model_calls:int=Field(default=48,ge=8,le=2400)
    holding_review_sessions:int=Field(default=5,ge=1,le=60)

    @model_validator(mode='after')
    def c2_rules(self):
        if self.mode!=('SMC' if self.research_flow=='C1' else 'ROUTER') or not self.automatic_stock_selection:raise ValueError('Portfolio must use its flow-specific automatic strategy')
        if not self.consent_to_paid_calls or not self.approve_historical_rules:raise ValueError('Paid consent and upfront historical entry/exit-rule approval are required')
        if not self.start_date or not self.end_date:raise ValueError('Choose an explicit simulation period')
        return self


class C1PortfolioSettings(C2PortfolioSettings):
    research_flow:Literal['C1']='C1'
    mode:str='SMC'
    take_profit_percent:float=Field(default=4.,gt=0,le=100,allow_inf_nan=False)
    trailing_stop_enabled:bool=False
    breakout_reentry_enabled:bool=False
    screening_candidates_per_session:int=Field(default=3,ge=1,le=10)

    @model_validator(mode='after')
    def c1_rules(self):
        if self.portfolio_playbook_id:raise ValueError('C1 SMC does not consume C2 portfolio lessons')
        if self.breakout_reentry_enabled:raise ValueError('Breakout re-entry is not used in C1 SMC')
        return self


def settings_for_state(state):
    return (C1PortfolioSettings if state['settings'].get('research_flow')=='C1' else C2PortfolioSettings).model_validate(state['settings'])


def now():return datetime.now(timezone.utc).isoformat()
def root():return Path(os.getenv('AEGIS_DATA_DIR','data'))/'c2_portfolio_runs'
def valid_id(value):
    if len(value)!=32 or any(x not in '0123456789abcdef' for x in value):raise ValueError('Invalid C2 portfolio ID')
    return value

def state_path(run_id):return root()/valid_id(run_id)/'state.json'
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temp.write_text(json.dumps(normalize(value),allow_nan=False));temp.replace(path)
    finally:temp.unlink(missing_ok=True)

def load(run_id):return json.loads(state_path(run_id).read_text())
def frame_for(frame,settings,provenance):
    if provenance.get('requested_start') and settings.start_date<date.fromisoformat(provenance['requested_start']):raise ValueError('C2 evaluation cannot include frozen-universe warm-up')
    if provenance.get('requested_end') and settings.end_date>date.fromisoformat(provenance['requested_end']):raise ValueError('End exceeds downloaded evaluation window')
    if settings.research_flow=='C1':
        from .smc import prepare_smc
        frame=prepare_smc(frame)
    f=prepare_selection_features(frame)
    f=f[(f.Date.dt.date>=settings.start_date)&(f.Date.dt.date<=settings.end_date)].copy()
    if f.Date.nunique()<2:raise ValueError('C2 replay needs at least two market sessions')
    if not f.Ready.any():raise ValueError('No ready historical indicators')
    return f.sort_values(['Date','Symbol']).reset_index(drop=True)

def fingerprint(f):return hashlib.sha256(f.drop(columns=['SMCStage'],errors='ignore').to_json(orient='split',date_format='iso',double_precision=15).encode()).hexdigest()

def create_run(frame,settings,*,source='synthetic',provenance=None,model=None):
    memory=portfolio_memory.bind(settings.portfolio_playbook_id,settings.start_date,settings.memory_allow_development_replay)
    provenance=provenance or {};f=frame_for(frame,settings,provenance);run_id=uuid.uuid4().hex
    state={'run_id':run_id,'version':VERSION,'created_utc':now(),'updated_utc':now(),'status':'QUEUED',
        'research_flow':settings.research_flow,'memory_manifest':memory,'settings':settings.model_dump(mode='json'),'model':model_name(model),'inference':identity(model=model),
        'prompt_version':CONFIG['version'],'corpus_sha256':corpus_info()['sha256'],'input_sha256':fingerprint(f),
        'data_source':source,'data_provenance':provenance,'dates':[str(d.date()) for d in sorted(f.Date.unique())],
        'day_index':0,'phase':'OPEN','cash':settings.initial_capital,'previous_equity':settings.initial_capital,
        'deferred_entries':[],'positions':{},'last_marks':{},'queued':[],'curves':[],'ledger':[],'selection_audit':[],'stop_updates':[],
        'decisions':[],'processed_close_keys':[],'model_calls':0,'budget_charged':0,'uncertain_model_calls':0,
        'call_limit':settings.max_model_calls,'inflight':None,'usage':[],'last_error':None,
        'research_attempts':{},'breakout_reentry_watches':{},
        'consents':[{'at':now(),'call_limit':settings.max_model_calls,'historical_rules':True}],
        'execution_policy':'Automatic historical fills under upfront approved rules; no live writes or per-fill human pause.'}
    # The reference uses identical data, capital, costs and risk; it has no C2 filters/reviews.
    policy=policy_from_settings(settings)
    state['strategy_policies']=strategy_policy_records(policy)
    if settings.research_flow=='C1':state['strategy_policies']={'SMC':position_policy_record(policy)}
    from .engine import backtest,buy_and_hold
    eq,events,metrics=backtest(f,mode=settings.mode,p=policy,automatic_selection=True,screening_limit=settings.screening_candidates_per_session if settings.research_flow=='C1' else 3)
    bench,bm=buy_and_hold(f,policy)
    state['reference']={'metrics':normalize(metrics),'curve':[{'date':str(r.Date.date()),'equity':r.Equity} for r in eq.itertuples()]}
    state['reference']['ledger']=[{'date':str(r.Date.date()),'symbol':r.Symbol,'event':r.Event,'quantity':r.Quantity,
        'price':r.Price,'fee':r.Fee,'strategy':r.Strategy,'realized_pnl':normalize(r.PnL)} for r in events.itertuples()]
    state['benchmark']={'name':'EQUAL_WEIGHT_BUY_AND_HOLD','metrics':normalize(bm),
                        'curve':[{'date':str(r.Date.date()),'equity':r.Equity} for r in bench.itertuples()]}
    save(state_path(run_id),state);return run_id


def case_snapshot(bar,*,purpose='ENTRY',position=None,index=0,rank=None):
    s={'symbol':str(bar.Symbol),'date':str(bar.Date.date()),'regime':str(bar.Regime),
       'approved_candidate':str(bar.RoutedStrategy),'research_purpose':purpose,
       **{k:float(getattr(bar,k)) for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14')}}
    s.update(PullbackRecent=bool(getattr(bar,'PullbackRecent',False)),PriorHigh=float(getattr(bar,'PriorHigh',bar.High)))
    if getattr(bar,'SMCContext',None):s['smc_context']=bar.SMCContext
    if position:s['holding_context']={'quantity':position['quantity'],'entry_price':position['entry_price'],
        'stop_price':position['stop'],'strategy':position['strategy'],'holding_sessions':index-position['entry_index'],
        'review_trigger':'Scheduled holding review; close-updated stop applies next session' if position.get('trailing_last_close') else 'Scheduled holding review'}
    if rank:s.update(selection_score=rank['score'],selection_rank=rank['rank'],average_turnover_20_inr=rank['average_turnover_20_inr'])
    return s

def validate_memory_state(state,settings):
    expected=portfolio_memory.bind(settings.portfolio_playbook_id,settings.start_date,settings.memory_allow_development_replay)
    if expected!=state.get('memory_manifest'):raise ValueError('Portfolio lesson settings differ from the pinned memory manifest')
    validate_memory_state(state,settings)


def validate_memory_state(state,settings):
    expected=portfolio_memory.bind(settings.portfolio_playbook_id,settings.start_date,settings.memory_allow_development_replay)
    if expected!=state.get('memory_manifest'):raise ValueError('Portfolio lesson settings differ from the pinned memory manifest')
    portfolio_memory.validate_binding(state.get('memory_manifest'),settings.start_date)


class PauseBudget(Exception):pass
class Cancelled(Exception):pass
class PauseProvider(Exception):pass


def execute_run(run_id,frame,*,researcher=None,preparer=None,validator=None,should_cancel=None,news_monitor=None):
    """Resume exact day/phase. Dependency injection is for explicit contract tests only."""
    state=load(run_id);settings=settings_for_state(state)
    if state['status'].startswith('COMPLETED'):return result_for(state)
    validate_memory_state(state,settings)
    f=frame_for(frame,settings,state['data_provenance'])
    if state['version']!=VERSION or state['prompt_version']!=CONFIG['version'] or state['corpus_sha256']!=corpus_info()['sha256'] or fingerprint(f)!=state['input_sha256']:
        raise ValueError('Data, prompts, policy corpus or simulator version changed; create a new run')
    frozen=state.get('inference',{'backend':'openrouter','model':state['model'],'budget_unit':'model_requests','adapter_version':'openrouter-v1'})
    if identity()!=frozen:raise ValueError('Inference backend/model/adapter changed; restore the original configuration or start a new run')
    flow=settings.research_flow
    from .c1_gate import validate_completed_c1,validate_smc_order
    researcher=researcher or run_agentic_case;preparer=preparer or prepare_company_research;validator=validator or (validate_completed_c1 if flow=='C1' else validate_completed_c2)
    if news_monitor is None and state['data_source']=='nsepython' and preparer is prepare_company_research:
        from .company_research import adverse_news_watch
        news_monitor=adverse_news_watch
    p=policy_from_settings(settings)
    path=state_path(run_id);folder=path.parent;groups={str(d.date()):g for d,g in f.groupby('Date',sort=True)}
    def checkpoint():state['updated_utc']=now();save(path,state)
    def activity(stage,snapshot=None,**details):
        # Separate bounded sidecar: a tool event never rewrites the financial checkpoint.
        value={'run_id':run_id,'stage':stage,'updated_utc':now(),
               'date':(snapshot or {}).get('date',state['dates'][min(state['day_index'],len(state['dates'])-1)])}
        if snapshot:value['symbol']=snapshot.get('symbol')
        value.update({k:v for k,v in details.items() if k in {'agent','tool','turn'}})
        save(folder/'activity.json',value)

    def cancelled():
        if (should_cancel and should_cancel()) or (folder/'cancel').exists():raise Cancelled()
    # Reserve before calls. A crash with no durable result leaves the full reservation charged.
    if state['inflight']:
        task=state['inflight'];output=folder/'research'/f"{task['id']}.json"
        if output.exists():
            out=json.loads(output.read_text());actual=min(8,max(0,int(out.get('llm_calls',8))))
            state['budget_charged']-=8-actual;state['model_calls']+=actual;state['usage'].extend(out.get('usage',[]))
            model_calls_total.inc(actual)
        else:
            state['uncertain_model_calls']+=8;uncertain_calls_total.inc(8)
        state['inflight']=None;checkpoint()
    state['status']='RUNNING';state['last_error']=None;checkpoint();activity('STARTING_RUN')

    def research(snapshot,key):
        cancelled()
        activity('PREPARING_DATED_EVIDENCE',snapshot)
        if corpus_info()['sha256']!=state['corpus_sha256']:raise ValueError('Policy corpus changed during historical run')
        attempt=state['research_attempts'].get(key,0)
        cid=digest([state['run_id'],key,attempt])[:32];outfile=folder/'research'/f'{cid}.json'
        def provider_pause(out):
            failure=inference_diagnostic(out.get('usage',[]),(out.get('failure') or {}).get('agent')) or out.get('failure')
            state['decisions'].append({'id':cid,'key':key,'date':snapshot['date'],'symbol':snapshot['symbol'],
                'purpose':snapshot['research_purpose'],'action':'PROVIDER_FAILURE',
                'failure':failure,'failure_category':'PROVIDER',
                'errors':[failure['code']+': '+failure['message']] if failure else out.get('model_errors',[]),'llm_calls':out.get('llm_calls',0)})
            state['research_attempts'][key]=attempt+1;checkpoint()
            raise PauseProvider()
        if outfile.exists():
            cached=json.loads(outfile.read_text())
            if cached.get('portfolio_memory',{}).get('manifest')!=state.get('memory_manifest'):raise ValueError('Cached research memory differs from the pinned portfolio version')
            if cached.get('retryable_provider_failure'):provider_pause(cached)
            return cached,cid
        try:
            pack=(preparer(snapshot['symbol'],snapshot['date'],progress=lambda _:(cancelled(),activity('READING_COMPANY_ARCHIVE',snapshot))) if preparer is prepare_company_research
                  else preparer(snapshot['symbol'],snapshot['date']))
        except Cancelled:raise
        except Exception as exc:
            if web_eligible(snapshot):
                from .company_research import read_company_research
                pack=read_company_research(snapshot['symbol'],snapshot['date'])
            else:return {'guard_pass':False,'model_errors':['Company archive unavailable: '+type(exc).__name__],'llm_calls':0,'snapshot':snapshot},None
        if not company_pack_researchable(pack) and not web_eligible(snapshot):return {'guard_pass':False,'model_errors':pack.get('reasons',['Insufficient company evidence']),'llm_calls':0,'snapshot':snapshot},None
        selected_lessons=portfolio_memory.retrieve(state.get('memory_manifest'),snapshot,pack)
        if state['budget_charged']+8>state['call_limit']:raise PauseBudget()
        state['budget_charged']+=8;state['inflight']={'id':cid,'key':key,'reserved':8};checkpoint()
        cancelled()
        # run_agentic_case always returns usage/errors; unexpected failures retain the reservation.
        memory_args={'lessons':selected_lessons} if state.get('memory_manifest') else {}
        if researcher is run_agentic_case:
            memory_args['progress']=lambda event:activity(event['event'].upper(),snapshot,**{k:v for k,v in event.items() if k!='event'})
        activity('LLM_RESEARCH',snapshot)
        out=researcher(snapshot,flow,model=state['model'],max_calls=8,max_output_tokens=4800,backend=frozen['backend'],**memory_args)
        out['portfolio_memory']={'manifest':state.get('memory_manifest'),'lesson_ids':[x['id'] for x in selected_lessons]}
        out['snapshot']=snapshot
        out['retryable_provider_failure']=any(u.get('error') for u in out.get('usage',[]))
        save(outfile,out)
        actual=int(out.get('llm_calls',8))
        if not 0<=actual<=8:raise ValueError('Invalid researcher call accounting')
        state['budget_charged']-=8-actual;state['model_calls']+=actual;state['usage'].extend(out.get('usage',[]));state['inflight']=None;checkpoint()
        model_calls_total.inc(actual)
        if corpus_info()['sha256']!=state['corpus_sha256']:raise ValueError('Policy corpus changed during research')
        if out['retryable_provider_failure']:provider_pause(out)
        return out,cid

    def decide(snapshot,key):
        out,cid=research(snapshot,key);validated=None;validation_failure=None
        activity('VALIDATING_RESEARCH',snapshot)
        if out.get('guard_pass'):
            try:validated=validator(out,purpose=snapshot['research_purpose'])
            except (ValueError,KeyError,TypeError) as exc:
                from .research_diagnostics import validation_diagnostic
                validation_failure=validation_diagnostic(exc,'code_guard')
        rec={'id':cid,'key':key,'date':snapshot['date'],'symbol':snapshot['symbol'],'purpose':snapshot['research_purpose'],'entry_setup':snapshot['regime'],'breakout_reentry':snapshot.get('breakout_reentry'),
             'action':validated['portfolio_action'] if validated else 'BLOCKED','guard_pass':bool(validated),
             'dated_web_search':out.get('dated_web_search'),'portfolio_memory':out.get('portfolio_memory'),'explanation':out.get('explanation',''),'company_assessment':out.get('company_assessment'),
             'citations':out.get('citations',[]),'errors':out.get('model_errors',[]),'llm_calls':out.get('llm_calls',0)}
        if out.get('failure'):
            rec['failure']=out['failure'];rec['failure_category']=out['failure']['category']
        elif validation_failure:
            rec['failure']=validation_failure;rec['failure_category']=validation_failure['category']
            rec['errors']=[*rec['errors'],validation_failure['code']+': '+validation_failure['message']]
        elif not cid and not validated:rec['failure_category']='EVIDENCE'
        if not validated and not rec['errors']:rec['errors']=['Completed C2 validation failed']
        return rec

    def sell(sym,bar,when,reason,reference,research_id=None):
        pos=state['positions'].pop(sym);price=reference*(1-p.slippage_bps/10000)
        if reason in {'SELL_STOP','SELL_TRAILING_STOP'}:
            register_breakout_stop(state.setdefault('breakout_reentry_watches',{}),{**pos,'symbol':sym},when,state['day_index'],p.breakout_reentry_enabled)
        fee=price*pos['quantity']*p.fee_bps/10000;net=price*pos['quantity']-fee
        state['cash']+=net
        state['ledger'].append({'date':when,'symbol':sym,'event':reason,'quantity':pos['quantity'],'price':price,'fee':fee,
            'strategy':pos['strategy'],'realized_pnl':net-pos['quantity']*pos['entry_price']-pos['entry_fee'],
            'initial_stop':pos.get('initial_stop',pos['stop']),'stop_price':pos['stop'],'take_profit_reference':take_profit_reference(pos,p),
            'entry_research_id':pos['entry_research_id'],'research_id':research_id,'entry_date':pos['entry_date']})

    try:
        for index in range(state['day_index'],len(state['dates'])):
            cancelled();when=state['dates'][index];daily=groups[when];snap={str(r.Symbol):r for r in daily.itertuples()}
            if corpus_info()['sha256']!=state['corpus_sha256']:raise ValueError('Policy corpus changed during historical run')
            def equity(opening=False):return state['cash']+sum(pos['quantity']*(float(getattr(snap[s],'Open' if opening else 'Close')) if s in snap else state['last_marks'][s]['price']) for s,pos in state['positions'].items())
            if state['phase']=='OPEN':
                activity('PROCESSING_OPEN')
                pending=[]
                for order in sorted(state['queued'],key=lambda o:0 if o['side']=='SELL' else 1):
                    sym=order['symbol']
                    if sym not in snap:pending.append(order);continue
                    bar=snap[sym]
                    if order['side']=='BUY' and settings.review_after_gap and defer_entry_review(order['signal_date'],when):
                        origin=order.get('original_signal_date',order['signal_date'])
                        state['deferred_entries'].append({'symbol':sym,'date':origin})
                        state['decisions'].append({'date':when,'symbol':sym,'purpose':'ENTRY','action':'DEFERRED_REVIEW',
                            'original_signal_date':origin,'llm_calls':0,'explanation':'Missing-bar delay crossed a non-trading gap; refresh at this close before any later entry.'})
                        continue
                    if order['side']=='SELL':
                        if sym in state['positions']:
                            pos=state['positions'][sym]
                            # An opening gap through an existing stop remains a protective stop.
                            stop_gap=float(bar.Open)<=pos['stop']
                            profit_gap=take_profit_reference(pos,p) is not None and float(bar.Open)>=take_profit_reference(pos,p)
                            if order['reason'] in {'SELL_C2','SELL_C1'} and not (stop_gap or profit_gap):
                                try:
                                    out=json.loads((folder/'research'/f"{order['research_id']}.json").read_text())
                                    if validator(out,purpose='HOLDING_REVIEW')['portfolio_action']!='EXIT':raise ValueError('Exit changed')
                                except (ValueError,KeyError,TypeError,OSError):
                                    state['decisions'].append({'date':when,'symbol':sym,'action':'FILL_BLOCKED','errors':['C2 exit research changed before fill']});continue
                            reason=stop_exit_reason(pos) if stop_gap else ('SELL_TAKE_PROFIT' if take_profit_reference(pos,p) is not None and float(bar.Open)>=take_profit_reference(pos,p) else order['reason'])
                            sell(sym,bar,when,reason,float(bar.Open),order.get('research_id'))
                    elif sym not in state['positions'] and len(state['positions'])<p.max_positions:
                        buy=float(bar.Open)*(1+p.slippage_bps/10000);eq=equity(True)
                        # Durable research is revalidated before a simulated fill; a changed pack blocks it.
                        try:
                            out=json.loads((folder/'research'/f"{order['research_id']}.json").read_text())
                            if flow=='C1':validate_smc_order(order,out,f,p)
                            else:validator(out,purpose='ENTRY')
                        except (ValueError,KeyError,TypeError,OSError):
                            state['decisions'].append({'date':when,'symbol':sym,'action':'FILL_BLOCKED','errors':['Entry research changed before next eligible open']});continue
                        active_policy=policy_for_strategy(p,order['strategy'])
                        qty=allowable_shares(buy,order['stop'],state['cash'],eq,active_policy)
                        if eq<=state['previous_equity']*(1-p.max_daily_loss_pct/100):qty=0
                        if qty>0:
                            fee=qty*buy*p.fee_bps/10000;state['cash']-=qty*buy+fee
                            state['positions'][sym]={'quantity':qty,'entry_price':buy,'entry_fee':fee,'stop':order['stop'],
                                'initial_stop':order['stop'],'entry_signal_atr':float(out['snapshot']['ATR14']),'highest_close':None,
                                'strategy':order['strategy'],'entry_date':when,'entry_index':index,'last_review_index':index,
                                'last_news_date':order['signal_date'],
                                'entry_research_id':order['research_id']}
                            state['positions'][sym]['execution_policy']=position_policy_record(active_policy)
                            state['positions'][sym]['breakout_reentry_count']=int(order.get('breakout_reentry',False))
                            if order.get('breakout_reentry'):state['breakout_reentry_watches'].pop(sym,None)
                            state['ledger'].append({'date':when,'symbol':sym,'event':'BUY','quantity':qty,'price':buy,'fee':fee,
                                'initial_stop':order['stop'],'strategy':order['strategy'],'realized_pnl':None,'research_id':order['research_id'],'signal_date':order['signal_date'],'original_signal_date':order.get('original_signal_date',order['signal_date']),
                                'risk_percent_used':active_policy.risk_per_trade*100,'trailing_activation_r':active_policy.trailing_activation_r})
                            state['ledger'][-1]['entry_setup']='SMC_EVIDENCE_FIRST' if flow=='C1' else 'BREAKOUT_BOUNCE' if order.get('breakout_reentry') else 'REGULAR'
                            if flow=='C1':state['ledger'][-1]['smc_context']=order['smc_context']
                        else:state['decisions'].append({'date':when,'symbol':sym,'action':'FILL_BLOCKED','errors':['Next-open gap, risk, cash or daily-loss check failed']})
                state['queued']=pending
                for sym,pos in list(state['positions'].items()):
                    trigger=protective_exit(pos,snap[sym],p) if sym in snap else None
                    if trigger:
                        reason,reference=trigger;sell(sym,snap[sym],when,reason,reference)
                state['last_marks'].update({s:{'price':float(b.Close),'date':when} for s,b in snap.items()})
                state['phase']='CLOSE';state['processed_close_keys']=[];checkpoint()
            # The close phase is resumable without repeating this day's opening fills/stops.
            close_equity=equity();daily_block=close_equity<=state['previous_equity']*(1-p.max_daily_loss_pct/100)
            # Advance every surviving holding before model research can pause this close.
            # Today's intraday checks already finished using the previously active stop.
            if p.trailing_stop_enabled:
                for sym,pos in state['positions'].items():
                    if sym not in snap:continue
                    active_policy=policy_for_strategy(p,pos['strategy'])
                    update=advance_trailing_stop(pos,float(snap[sym].Close),when,active_policy.trailing_atr_multiple,activation_r=active_policy.trailing_activation_r)
                    if update:state['stop_updates'].append({'symbol':sym,**update})
                checkpoint()
            pending_symbols={o['symbol'] for o in state['queued']}
            # No terminal liquidation. Code exits on the last close remain unfilled intentions.
            for sym,pos in list(state['positions'].items()):
                if sym not in snap or sym in pending_symbols:continue
                bar=snap[sym];key=f'{when}:{sym}:EXIT_RULE'
                if exit_signal(bar,pos['strategy']):
                    if key not in state['processed_close_keys']:
                        state['queued'].append({'side':'SELL','symbol':sym,'reason':'SELL_SIGNAL','signal_date':when})
                        state['processed_close_keys'].append(key);checkpoint()
                    continue
                # New dated disclosure candidates trigger research between scheduled reviews.
                news_trigger=False
                if news_monitor and index<len(state['dates'])-1:
                    checks=state.setdefault('news_checks',{});check_key=f'{when}:{sym}'
                    if check_key not in checks:
                        try:checks[check_key]=news_monitor(sym,when,pos.get('last_news_date',pos['entry_date']))
                        except Exception as exc:checks[check_key]={'status':'UNAVAILABLE','candidates':[],'error':type(exc).__name__}
                        if checks[check_key].get('status')=='CHECKED':pos['last_news_date']=when
                        checkpoint()
                    news_trigger=bool(checks[check_key].get('candidates'))
                # No paid last-day review: it cannot execute inside the requested period.
                if index==len(state['dates'])-1 or (not news_trigger and index-pos['last_review_index']<settings.holding_review_sessions) or not bar.Ready:continue
                key=f'{when}:{sym}:HOLDING_REVIEW'
                if key in state['processed_close_keys']:continue
                snapshot=case_snapshot(bar,purpose='HOLDING_REVIEW',position=pos,index=index)
                if news_trigger:snapshot['holding_context']['review_trigger']='New dated issuer disclosure candidate; assess actual adverse content'
                rec=decide(snapshot,key)
                pos['last_review_index']=index
                if rec['action']=='EXIT':state['queued'].append({'side':'SELL','symbol':sym,'reason':'SELL_'+flow,'signal_date':when,'research_id':rec['id']})
                state['decisions'].append(rec);state['processed_close_keys'].append(key)
                checkpoint()
            activity('SCREENING_CANDIDATES')
            # Screen on every close; reserve slots for existing pending BUYs, not future sale proceeds.
            if index<len(state['dates'])-1:
                pending_buys={o['symbol'] for o in state['queued'] if o['side']=='BUY'}
                entry_daily=reentry_candidates(daily,state.setdefault('breakout_reentry_watches',{}),index) if p.breakout_reentry_enabled else daily
                entry_snap={str(r.Symbol):r for r in entry_daily.itertuples()}
                if flow=='C1':
                    from .smc import screening_candidates
                    audit=screening_candidates(entry_daily,set(state['positions'])|pending_buys,index,settings.screening_candidates_per_session)
                    if len(state['positions'])+len(pending_buys)>=p.max_positions:
                        for r in audit:r['selected']=False;r['reasons'].append('POSITION_LIMIT')
                else:
                    audit=rank_candidates(entry_daily,'ROUTER',equity=close_equity,cash=state['cash'],trade_policy=p,
                        held_symbols=set(state['positions'])|pending_buys,available_slots=max(0,p.max_positions-len(state['positions'])-len(pending_buys)))
                if daily_block:
                    for r in audit:r['selected']=False;r['reasons'].append('DAILY_LOSS_LIMIT')
                if not any(x['date']==when for x in state['selection_audit']):state['selection_audit'].extend(audit);checkpoint()
                origins={d['symbol']:d['date'] for d in state['deferred_entries'] if d['date']<when}
                selected_symbols={r['symbol'] for r in audit if r['selected']}
                for sym,origin in origins.items():
                    review_key=f'{when}:{sym}:DEFERRED_CANCEL'
                    if sym not in selected_symbols and sym not in pending_buys and sym not in state['positions'] and f'{when}:{sym}:ENTRY' not in state['processed_close_keys'] and review_key not in state['processed_close_keys']:
                        state['decisions'].append({'date':when,'symbol':sym,'purpose':'ENTRY','action':'ENTRY_CANCELLED',
                            'original_signal_date':origin,'llm_calls':0,'explanation':'Fresh post-gap signal is no longer eligible or selected; no stale entry.'})
                        state['processed_close_keys'].append(review_key);checkpoint()
                delay=settings.review_after_gap and defer_entry_review(when,state['dates'][index+1])
                for rank in audit:
                    if not rank['selected']:continue
                    if delay:
                        key=f'{when}:{rank["symbol"]}:DEFER_ENTRY'
                        if key not in state['processed_close_keys']:
                            state['deferred_entries'].append({'symbol':rank['symbol'],'date':when})
                            state['decisions'].append({'date':when,'symbol':rank['symbol'],'purpose':'ENTRY','action':'DEFERRED_REVIEW',
                                'llm_calls':0,'explanation':'Friday/non-trading gap: recheck next trading close before researching an entry for a later open.'})
                            state['processed_close_keys'].append(key);checkpoint()
                        continue
                    sym=rank['symbol'];key=f'{when}:{sym}:ENTRY'
                    if key in state['processed_close_keys']:continue
                    bar=entry_snap[sym];snapshot=case_snapshot(bar,rank=rank)
                    if bar.Regime=='BREAKOUT_BOUNCE':snapshot['breakout_reentry']=reentry_context(state['breakout_reentry_watches'][sym])
                    if sym in origins:snapshot['original_signal_date']=origins[sym]
                    if flow=='C1':
                        # The single agent sees no SMC signal/context or routed strategy before its company screen.
                        snapshot.update(regime='UNCERTAIN',approved_candidate='NONE',research_purpose='COMPANY_SCREEN',PullbackRecent=False)
                        snapshot.pop('smc_context',None)
                    rec=decide(snapshot,key)
                    if flow=='C1' and rec['action']=='SCREEN':
                        activity('CHECKING_SMC_SIGNAL',snapshot)
                        from .smc import SMC_REASONS
                        stage=getattr(bar,'SMCStage','ENTRY_CONFIRMED' if bar.SMCSignal else 'WAITING_SWEEP')
                        rec.update(smc_stage=stage,research_explanation=rec['explanation'],
                                   explanation=SMC_REASONS[stage]+' Dated company screening passed.')
                        rec.update(research_order='EVIDENCE_BEFORE_SIGNAL',evidence_passed=True,
                                   smc_signal=bool(bar.SMCSignal),entry_setup='SMC_EVIDENCE_FIRST')
                        rec['action']='ENTER' if bool(bar.SMCSignal) else 'NO_SMC_SIGNAL'
                        if bool(bar.SMCSignal):rec['smc_context']=bar.SMCContext
                    if rec['action']=='ENTER':
                        stop=initial_stop_price(bar.Close,bar.ATR14,policy_for_strategy(p,chosen_strategy(bar)))
                        if stop>0:state['queued'].append({'side':'BUY','symbol':sym,'strategy':chosen_strategy(bar),
                            'stop':stop,'signal_date':when,'original_signal_date':origins.get(sym,when),'research_id':rec['id'],
                            'breakout_reentry':bar.Regime=='BREAKOUT_BOUNCE',**({'smc_context':bar.SMCContext} if flow=='C1' else {})})
                    elif bar.Regime=='BREAKOUT_BOUNCE' and (rec.get('company_assessment') or {}).get('adverse_risk') in {'ADVERSE_EVENT_FOUND','MATERIAL_ADVERSE'}:
                        state['breakout_reentry_watches'][sym]['status']='CANCELLED_ADVERSE'
                    if flow=='C1' and not rec.get('evidence_passed'):
                        rec['smc_stage']='NOT_CHECKED_EVIDENCE_BLOCKED'
                    state['decisions'].append(rec);state['processed_close_keys'].append(key)
                    checkpoint()
            state['deferred_entries']=[d for d in state['deferred_entries'] if d['date']==when]
            state['last_marks'].update({s:{'price':float(b.Close),'date':when} for s,b in snap.items()})
            state['curves'].append({'date':when,'equity':close_equity,'cash':state['cash'],'open_positions':len(state['positions']),
                                    'daily_loss_blocked':daily_block,'queued_orders':len(state['queued'])})
            state['previous_equity']=close_equity;state['day_index']=index+1;state['phase']='OPEN';state['processed_close_keys']=[];checkpoint()
        state['status']='COMPLETED_WITH_GAPS' if any(d.get('action') in {'BLOCKED','FILL_BLOCKED'} for d in state['decisions']) else 'COMPLETED'
        completed_total.inc()
    except PauseBudget:state['status']='PAUSED_BUDGET'
    except PauseProvider:state['status']='PAUSED_PROVIDER'
    except Cancelled:state['status']='PAUSED_USER'
    except Exception as exc:
        state=load(run_id)  # rollback any uncheckpointed partial phase mutations
        state['status']='INTERRUPTED';state['last_error']=type(exc).__name__
    activity(state['status'])
    checkpoint();return result_for(state)


def result_for(state):
    flow=state.get('research_flow','C2');reference_mode='SMC_REFERENCE' if flow=='C1' else 'ROUTER'
    decisions=[]
    for stored in state['decisions']:
        decision=dict(stored)
        cid=decision.get('id')
        if cid and len(cid)==32 and all(x in '0123456789abcdef' for x in cid) and (decision.get('action')=='PROVIDER_FAILURE' or any('BLOCK: ValidationError;' in x for x in decision.get('errors',[]))):
            failure=saved_failure(state_path(state['run_id']).parent/'research'/f'{cid}.json')
            if failure:
                decision.update(recorded_errors=decision['errors'],failure=failure,failure_category=failure['category'],
                    errors=[failure['code']+': '+failure['message']])
        if decision.get('action')=='BLOCKED' and not cid and decision.get('llm_calls',0)==0:
            decision.setdefault('failure_category','EVIDENCE')
        decisions.append(decision)
    rows=list(state['curves']);initial=state['settings']['initial_capital'];holdings=[]
    exit_settings=TradePolicy(stop_loss_mode=state['settings'].get('stop_loss_mode','ATR'),
        stop_loss_percent=state['settings'].get('stop_loss_percent',5.0),atr_stop_multiple=state['settings'].get('initial_stop_atr_multiple',2.0),take_profit_percent=state['settings'].get('take_profit_percent',0),fee_bps=state['settings']['fee_bps'],slippage_bps=state['settings']['slippage_bps'])
    for sym,pos in state['positions'].items():
        mark=state['last_marks'].get(sym,{'price':pos['entry_price'],'date':pos['entry_date']})
        holdings.append({'symbol':sym,**pos,'take_profit_reference':take_profit_reference(pos,exit_settings),'mark_price':mark['price'],'mark_date':mark['date'],
            'market_value':pos['quantity']*mark['price'],
            'unrealized_pnl':pos['quantity']*(mark['price']-pos['entry_price'])-pos['entry_fee'],
            'last_review_date':state['dates'][pos['last_review_index']]})
    eq=state['cash']+sum(h['market_value'] for h in holdings)
    if state['phase']=='CLOSE':
        rows.append({'date':state['dates'][state['day_index']],'equity':eq,'cash':state['cash'],
                     'open_positions':len(holdings),'provisional_close':True})
    realized=sum(x['realized_pnl'] or 0 for x in state['ledger']);unrealized=sum(h['unrealized_pnl'] for h in holdings)
    usage=state['usage'];costs=[u.get('cost') for u in usage]
    cost_complete=bool(usage) and all(isinstance(x,(int,float)) for x in costs) and not state['uncertain_model_calls']
    metrics={'mode':flow,'initial_capital':initial,'ending_equity':eq,'ending_cash':state['cash'],
        'total_return_pct':100*(eq/initial-1),'realized_pnl':realized,'unrealized_pnl':unrealized,'open_positions':len(holdings)}
    if rows:
        curve=pd.DataFrame([{'Date':r['date'],'Equity':r['equity']} for r in rows])
        ev=pd.DataFrame([{'Event':r['event'],'PnL':r['realized_pnl']} for r in state['ledger']],columns=['Event','PnL'])
        metrics.update(performance(curve,ev,initial));metrics['ending_equity']=eq
        # Include starting capital as the first high-water mark, including initial costs.
        values=pd.Series([initial]+[r['equity'] for r in rows]);metrics['max_drawdown_pct']=float((values/values.cummax()-1).min()*100)
    terminal=state['status'].startswith('COMPLETED')
    cutoff=rows[-1]['date'] if rows else None
    reference_curve=[r for r in state['reference']['curve'] if cutoff and r['date']<=cutoff]
    benchmark={**state['benchmark'],'curve':[r for r in state['benchmark']['curve'] if cutoff and r['date']<=cutoff]}
    if not terminal:benchmark['metrics']={}
    try:
        activity=json.loads((state_path(state['run_id']).parent/'activity.json').read_text())
        if activity.get('run_id')!=state['run_id'] or (state['status']=='RUNNING' and activity.get('date')!=state['dates'][min(state['day_index'],len(state['dates'])-1)]):activity={}
    except (OSError,ValueError):activity={}
    if state['status'] not in {'RUNNING','QUEUED'}:activity={**activity,'stage':state['status']}
    elif not activity:
        key=(state.get('inflight') or {}).get('key','').split(':')
        activity={'stage':'QUEUED' if state['status']=='QUEUED' else 'LLM_RESEARCH' if state.get('inflight') else state['phase'],
                  'symbol':key[1] if len(key)>1 else None,'updated_utc':state.get('updated_utc')}
    return normalize({'activity':activity,'updated_utc':state.get('updated_utc'),'run_id':state['run_id'],'research_flow':flow,'strategy_definition':'smc-daily-sweep-bos-ob-v1' if flow=='C1' else None,'research_order':'EVIDENCE_BEFORE_SIGNAL' if flow=='C1' else 'SIGNAL_BEFORE_RESEARCH','independent_critic':flow=='C2','version':state['version'],'created_utc':state['created_utc'],'status':state['status'],
        'research_prompt_version':state['prompt_version'],'current_research_prompt_version':CONFIG['version'],
        'research_configuration_changed':state['prompt_version']!=CONFIG['version'] or state['version']!=VERSION or state['corpus_sha256']!=corpus_info()['sha256'],
        'signal_checks':[{k:d.get(k) for k in ('date','symbol','smc_stage','smc_signal','action','explanation')} for d in decisions if d.get('evidence_passed')],
        'research_summary':{'company_screens':sum(d.get('purpose')=='COMPANY_SCREEN' for d in decisions),
            'eligible_company_sessions':sum(bool(r.get('eligible')) for r in state['selection_audit']),
            'shortlisted_company_sessions':sum(bool(r.get('selected')) for r in state['selection_audit']),
            'deferred_reviews':sum(d.get('action')=='DEFERRED_REVIEW' for d in decisions),
            'queued_buys':sum(o.get('side')=='BUY' for o in state['queued']),
            'evidence_passed':sum(bool(d.get('evidence_passed')) for d in decisions),
            'signal_checks':sum(bool(d.get('evidence_passed')) for d in decisions),
            'signals_found':sum(d.get('smc_signal') is True for d in decisions),
            'research_blocked':sum(d.get('action') in {'BLOCKED','PROVIDER_FAILURE'} for d in decisions),
            'buy_fills':sum(t.get('event')=='BUY' for t in state['ledger']),
            'no_smc_signal':sum(d.get('action')=='NO_SMC_SIGNAL' for d in decisions),'entry_decisions':sum(d.get('action')=='ENTER' for d in decisions)},
        'portfolio_memory':state.get('memory_manifest'),'settings':state['settings'],'data_source':state['data_source'],'data_provenance':state['data_provenance'],
        'strategy_policies':state.get('strategy_policies',{}),'legacy_shared_execution_policy':'strategy_policies' not in state,
        'breakout_reentry_watches':list(state.get('breakout_reentry_watches',{}).values()),
        'period':{'start':state['dates'][0],'end':state['dates'][-1]},'sessions':len(state['dates']),
        'progress':{'completed_sessions':state['day_index'],'total_sessions':len(state['dates']),'phase':state['phase'],
                    'current_date':state['dates'][min(state['day_index'],len(state['dates'])-1)]},
        'metrics':[metrics]+([{'mode':reference_mode,'initial_capital':initial,**state['reference']['metrics']}] if terminal else []),
        'curves':{flow:rows,reference_mode:reference_curve},'ledgers':{flow:state['ledger'],reference_mode:state['reference'].get('ledger',[]) if terminal else []},
        'news_checks':list(state.get('news_checks',{}).values()),
        'benchmark':benchmark,'open_holdings':holdings,'pending_orders':state['queued'],'decisions':decisions,
        'initial_stop_loss':initial_stop_settings(exit_settings),'stop_updates':state.get('stop_updates',[]),'deferred_entries':state.get('deferred_entries',[]),
        'exit_policy':{'take_profit_percent':state['settings'].get('take_profit_percent',0),'take_profit_basis':'Net of modeled entry/exit fees; execution includes slippage; ambiguous daily bars use stop first',
            'review_after_gap':state['settings'].get('review_after_gap',False),'trailing_stop_enabled':state['settings'].get('trailing_stop_enabled',False),
            'trailing_atr_multiple':state['settings'].get('trailing_atr_multiple',2.0),
            'basis':'highest completed close since entry','atr_source':'entry signal; distance fixed for the holding',
            'activation':'raised at completed close, effective from next session',
            'breakout_settings':{k:v for k,v in state['settings'].items() if k.startswith('breakout_')},
            'breakout_reentry_window_sessions':10 if state.get('strategy_policies') and flow=='C2' else None,
            'smc_signal_exit':'none; target/protective stop/adverse research exit' if flow=='C1' else None},
        'stock_selection':{'enabled':True,'audits':{flow:state['selection_audit']},'note':'C1 liquidity screens precede SMC eligibility; C2 shortlists precede specialist research. Neither shortlist is an executed entry.'},
        'inference':state.get('inference',identity(backend='openrouter',model=state['model'])),
        'model_usage':{'budget_unit':state.get('inference',{}).get('budget_unit','model_requests'),
            'provider_requests_counted':state.get('inference',{}).get('backend','openrouter')=='openrouter','attempted_calls':state['model_calls'],'budget_charged_calls':state['budget_charged'],
            'uncertain_calls_reserved':state['uncertain_model_calls'],'call_limit':state['call_limit'],
            'total_tokens_reported':sum(int(u.get('total_tokens') or 0) for u in usage),
            'provider_cost_usd':sum(costs) if cost_complete else None,'cost_reporting_complete':cost_complete},
        'accounting':{'realized_pnl':realized,'unrealized_pnl':unrealized,'equity_identity_error':eq-initial-realized-unrealized,
            'forced_end_liquidation':False,'model_cost_in_trading_returns':False},
        'comparison_valid_for_full_period':terminal,'last_error':state['last_error'],
        'disclaimer':'C2 historical simulation; automatic fills under upfront rules, no live orders. Model cost is separate USD, not deducted from INR trading returns. Partial runs are not full-period comparisons. Raw-price/survivorship and archive-coverage limitations remain.'})


_executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='c2-portfolio')
_active={};_lock=threading.RLock()

def active(run_id):
    with _lock:return run_id in _active and not _active[run_id].done()

def launch(run_id,frame):
    with _lock:
        if run_id in _active and not _active[run_id].done():raise ValueError('Run already active')
        _active[run_id]=_executor.submit(execute_run,run_id,frame.copy())

def status(run_id):
    state=load(run_id);result=result_for(state);result['worker_active']=active(run_id)
    if state['status'] in {'RUNNING','QUEUED'} and not result['worker_active']:result['status']='INTERRUPTED'
    return result

def resume(run_id,frame,additional_calls):
    with _lock:
        if active(run_id):raise ValueError('Run already active')
        state=load(run_id)
        if state['status'].startswith('COMPLETED'):raise ValueError('Completed run cannot be resumed')
        if not 0<=additional_calls<=2400:raise ValueError('Additional call allowance must be between 0 and 2400')
        settings=settings_for_state(state)
        validate_memory_state(state,settings)
        f=frame_for(frame,settings,state['data_provenance'])
        if state['version']!=VERSION or fingerprint(f)!=state['input_sha256'] or state['prompt_version']!=CONFIG['version'] or state['corpus_sha256']!=corpus_info()['sha256']:raise ValueError('Data, research or exit-policy configuration changed; start a new run')
        frozen=state.get('inference',identity(backend='openrouter',model=state['model']))
        if identity()!=frozen:raise ValueError('Inference backend/model/adapter changed; restore it or create a new run')
        state['call_limit']+=additional_calls;state['status']='QUEUED';state['consents'].append({'at':now(),'additional_calls':additional_calls,'new_limit':state['call_limit']})
        (state_path(run_id).parent/'cancel').unlink(missing_ok=True);save(state_path(run_id),state);launch(run_id,frame)
