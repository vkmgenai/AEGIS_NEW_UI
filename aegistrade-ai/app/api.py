"""AegisTrade local REST research console; NEVER connected to any live broker."""
from __future__ import annotations
import json,os,sqlite3,uuid,math,threading
from pathlib import Path
from datetime import timedelta,date
import pandas as pd
from fastapi import FastAPI,HTTPException,Header
from fastapi.responses import StreamingResponse,HTMLResponse
from pydantic import BaseModel,Field
from prometheus_client import Counter,Histogram,generate_latest,CONTENT_TYPE_LATEST
from starlette.responses import Response
from aegistrade.market import synthetic_market,download_nse_history
from aegistrade.strategies import prepare_indicators,entry_signal,chosen_strategy
from aegistrade.engine import backtest,TradePolicy
from aegistrade.experiments import strategy_comparison
from aegistrade.knowledge import PolicyRetriever,get_retriever
from aegistrade.lessons import ReviewedPlaybook,propose_failure_lesson
from aegistrade.safety import AuditBroker,RiskInputs,RiskParameters,utc_now
from aegistrade.security import check_reviewer_token,scan_untrusted_text
from aegistrade.openrouter import BudgetedExplainer
from aegistrade.llm_backend import backend_info,model_name,require_backend_ready
from app.backend_compat import UI_API_CONTRACT
from aegistrade.simulation_service import SimulationSettings,execute_simulation
from aegistrade.research_service import ResearchSettings,execute_research,needs_llm,required_call_budget,ResearchPreflightError,memory_preflight

DATA=Path(os.getenv('AEGIS_DATA_DIR','data'))
DATA.mkdir(parents=True,exist_ok=True)
app=FastAPI(title='AegisTrade AI - Simulation Only',version='0.21.0',docs_url='/docs')
requests_total=Counter('aegis_http_requests_total','Requests', ['route'])
workflow_seconds=Histogram('aegis_workflow_duration_seconds','Workflow duration')
blocked=Counter('aegis_trade_blocked_total','Blocked trade decisions',['reason'])
approved=Counter('aegis_trade_approved_total','Approved simulated proposals')
simulations_total=Counter('aegis_simulations_total','Completed historical simulations')
research_completed_total=Counter('aegis_research_experiments_total','Completed C0 C1 C2 research experiments',['configuration'])
research_llm_attempts_total=Counter('aegis_research_model_calls_total','Research inference units attempted; see selected backend budget unit',['configuration'])

_market_lock=threading.RLock()
_frame=None
_checkpointer=None
_runs_db=None
_broker=None
_lessons=None

def market_config():
    path=DATA/'market_config.json'
    return json.loads(path.read_text()) if path.exists() else {}

def market_source():
    return market_config().get('source',os.getenv('AEGIS_DATA_SOURCE','synthetic'))

def nse_dataset_directory():
    configured=market_config().get('dataset_dir')
    if configured:
        path=Path(configured)
        return path if path.is_absolute() else DATA/path
    return Path(os.getenv('AEGIS_NSE_DATASET_DIR',str(DATA/'nse_nifty20')))

def _load_frame():
    global _frame
    if _frame is None:
        if market_source()=='yfinance':
            # This MUST be explicitly enabled by user with internet and a data-source licence review.
            data=download_nse_history()
        elif market_source()=='nsepython':
            from aegistrade.nse_data import load_dataset
            data,_=load_dataset(nse_dataset_directory())
        elif market_source()=='synthetic':
            data=synthetic_market(n_days=620,seed=42)
        else:raise ValueError('Unknown data source; no synthetic fallback')
        _frame=prepare_indicators(data)
    return _frame

def frame():
    with _market_lock:return _load_frame()


def market_snapshot_context():
    with _market_lock:return frame(),market_source(),market_provenance()


def legacy_nse_directory():
    config=market_config()
    configured=config.get('legacy_dataset_dir') or (config.get('dataset_dir') if config.get('universe_id') in {None,'nifty20'} else None)
    if configured:
        path=Path(configured);return path if path.is_absolute() else DATA/path
    return Path(os.getenv('AEGIS_NSE_DATASET_DIR',str(DATA/'nse_nifty20')))


def broker():
    global _broker
    if _broker is None:
        _broker=AuditBroker(DATA/'simulated_orders.sqlite')
    return _broker

def lessons():
    global _lessons
    if _lessons is None:
        _lessons=ReviewedPlaybook(DATA/'reviewed_lessons.sqlite')
    return _lessons

def run_db():
    global _runs_db
    if _runs_db is None:
        _runs_db=sqlite3.connect(str(DATA/'run_context.sqlite'),check_same_thread=False)
        _runs_db.execute('PRAGMA journal_mode=WAL')
        _runs_db.execute('CREATE TABLE IF NOT EXISTS runs (thread_id TEXT PRIMARY KEY, context TEXT NOT NULL)')
        _runs_db.commit()
    return _runs_db

def checkpointer():
    global _checkpointer
    if _checkpointer is None:
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
        except ImportError as e:
            raise HTTPException(503,'Install full requirements: langgraph + langgraph-checkpoint-sqlite') from e
        _checkpointer=SqliteSaver(sqlite3.connect(str(DATA/'graph_checkpoints.sqlite'),check_same_thread=False))
    return _checkpointer

def auth(token: str|None):
    secret=os.getenv('AEGIS_REVIEWER_TOKEN','')
    if not check_reviewer_token(token or '',secret):
        raise HTTPException(403,'Reviewer token missing or invalid; set AEGIS_REVIEWER_TOKEN (12+ chars)')

class StartRequest(BaseModel):
    symbol:str|None=None
    inject_timeout:bool=False
    stale_seconds:int=Field(default=0,ge=0,le=1000000)
    disable_llm:bool=Field(default=True,description="Legacy field; this stage makes no model calls. Completed C2 research is always required.")
    research_run_id:str|None=None
    research_case_id:str|None=None
    capital_reference:float=Field(default=100000,ge=1000,le=100000000)

class ResumeRequest(BaseModel):
    thread_id:str
    decision:str
    payload_hash:str|None=None
    changes:dict|None=None

class SearchRequest(BaseModel):
    as_of:date|None=None
    query:str=Field(min_length=3,max_length=1500)
    top_k:int=Field(default=5,ge=1,le=12)

class LessonProposalRequest(BaseModel):
    error_code:str

class LessonReviewRequest(BaseModel):
    lesson_id:str
    decision:str
    reason:str


def _graph(ctx:dict):
    from aegistrade.workflow import build_trade_graph
    previous=ctx.get('research_context') or {}
    ctx['research_context']=_validated_research(previous.get('run_id'),previous.get('case_id'),previous.get('result_digest'))
    pol=RiskParameters(max_quote_age_seconds=600)
    return build_trade_graph(frame(),broker(),RiskInputs(equity=float(ctx.get('capital_reference',100000)),available_cash=float(ctx.get('capital_reference',100000)),current_positions=0),
         pol,PolicyRetriever(),BudgetedExplainer(enabled=False,
             model=model_name(),max_calls=2,max_output_tokens=240),
         checkpointer(),quote_price=ctx['quote_price'],quote_observed_utc=ctx['quote_time'],
         inject_timeout=ctx.get('inject_timeout',False),research_context=ctx.get('research_context'))

def _clean_graph_result(result:dict) -> dict:
    # LangGraph interrupt objects are not directly JSON serializable.
    if '__interrupt__' in result:
        return {'status':'WAITING_HUMAN', 'interrupts':[x.value for x in result['__interrupt__']],
                'note':'Human must review the exact payload and provide the reviewer token to resume.'}
    return {'status':result.get('status','FINISHED'),'result':result}

def _validated_research(run_id,case_id,expected_digest=None):
    if not run_id or not case_id:
        raise HTTPException(422,'Complete C2 research first and select its passing case before preparing an order')
    run=research_experiments_result(run_id)
    matches=[x for x in run['outputs'] if x.get('config')=='C2' and x.get('case_id')==case_id]
    if len(matches)!=1:raise HTTPException(422,'Select one completed C2 research case')
    from aegistrade.research_gate import validate_completed_c2
    try:context=validate_completed_c2(matches[0])
    except (ValueError,KeyError,TypeError):
        raise HTTPException(422,'C2 research is incomplete, failed, or rejected; rerun C2 before human review') from None
    if expected_digest and context['result_digest']!=expected_digest:
        raise HTTPException(409,'Research changed after proposal creation; create a new proposal and approval')
    snapshot=context['snapshot'];sym=context['symbol'];signal_date=context['date']
    rows=frame()[(frame().Symbol==sym)&(frame().Date==pd.Timestamp(signal_date))]
    if len(rows)!=1:raise HTTPException(422,'Research snapshot is absent from current market data')
    bar=rows.iloc[0];strategy=chosen_strategy(bar,'ROUTER')
    if (str(bar.Regime)!=snapshot['regime'] or any(not math.isfinite(float(bar[k])) or abs(float(bar[k])-snapshot[k])>1e-8
        for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14'))):
        raise HTTPException(409,'Market evidence changed; rerun C2 research and obtain fresh approval')
    if context['strategy']!=strategy or strategy=='NONE' or not entry_signal(bar,strategy):
        raise HTTPException(422,'C2 case has no eligible BUY signal. Abstention is a valid research outcome.')
    context.update(run_id=run_id,case_id=case_id)
    return context

def _build_start(req:StartRequest):
    if broker().kill_switch_enabled():raise HTTPException(423,"Human kill switch is active; new proposals are blocked")
    research_context=_validated_research(req.research_run_id,req.research_case_id)
    if req.symbol and req.symbol.upper()!=research_context['symbol']:
        raise HTTPException(422,'Requested symbol differs from the researched case')
    sym=research_context['symbol'];signal_date=research_context['date']
    price=float(research_context['snapshot']['Close'])
    now=utc_now()
    from datetime import timedelta
    quote_time=(now-timedelta(seconds=req.stale_seconds)).isoformat()
    thread=uuid.uuid4().hex
    ctx={'symbol':sym,'signal_date':signal_date,'quote_price':price,'quote_time':quote_time,
         'inject_timeout':req.inject_timeout,'disable_llm':req.disable_llm,
         'capital_reference':req.capital_reference,'research_context':research_context}
    run_db().execute('INSERT INTO runs(thread_id,context) VALUES (?,?)',(thread,json.dumps(ctx)))
    run_db().commit()
    return thread,ctx

@app.get('/',response_class=HTMLResponse,include_in_schema=False)
def api_home():
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AegisTrade AI — API</title>
<style>body{font:18px/1.6 system-ui,sans-serif;max-width:700px;margin:60px auto;padding:24px;color:#173b5d}a{color:#2456c5}li{margin:12px 0}</style>
</head><body><h1>AegisTrade AI</h1>
<p>This is the FastAPI backend on port 8000. Use the dashboard for your project demonstration.</p>
<ul><li><a href="http://127.0.0.1:8501">Open the dashboard — port 8501</a></li>
<li><a href="/docs">Open interactive API documentation</a></li>
<li><a href="/health">Check API health and inference readiness</a></li></ul>
<p>Simulation only. No live broker connection.</p></body></html>"""


@app.get('/health')
def health():
    requests_total.labels('health').inc()
    return {'ok':True,'version':app.version,'ui_api_contract':UI_API_CONTRACT,'mode':'SIMULATION_ONLY','data_source':market_source(),
            'dated_web_search_supported':True,'dated_web_search_enabled':os.getenv('AEGIS_DATED_WEB_SEARCH','true').lower()=='true',
            'dated_web_search_provider':'duckduckgo_html','dated_web_max_queries':2,'dated_web_max_pages':4,
            'universe_switching_supported':True,'universe_profiles':['nifty20','nifty100','research30'],
            'configurable_stop_loss_supported':True,'initial_stop_methods':['ATR','PERCENT'],
            'portfolio_memory_supported':True,'max_portfolio_lessons_per_case':3,'company_evidence_view':'company-view-v4-materiality',
            'fresh_adverse_profit_policy_supported':True,'take_profit_default_percent':8.0,'friday_entry_review':'Next trading close; fill no earlier than the following eligible open',
            'trailing_stop_supported':True,'trailing_stop_scope':'historical_portfolios','default_trailing_atr_multiple':2.0,
            'live_broker_enabled':False,'openrouter_opt_in':bool(os.getenv('OPENROUTER_API_KEY')),
            'llm_experiments_enabled':backend_info()['ready'] and os.getenv('AEGIS_ENABLE_LLM_EXPERIMENTS','false').lower()=='true',
            'inference':backend_info(),
            'ui_llm_max_cases':3,'agent_model':model_name(),
            'c2_required_before_order':True,'company_research_required':True,'company_decision_cutoff':'15:30 Asia/Kolkata on signal date',
            'c2_architecture':'supervisor + market/strategy/critic specialists','max_calls_per_agent_case':8}

@app.get('/market/universe')
def universe():
    f,source,provenance=market_snapshot_context()
    return {'symbols':sorted(f.Symbol.unique().tolist()),'first_date':str(f.Date.min().date()),
            'last_date':str(f.Date.max().date()),'total_rows':len(f),
            'source':source,'provenance':provenance}

@app.get('/market/history')
def market_history(symbol: str='RELIANCE', limit: int=180):
    """Validated daily-bar history for Streamlit charts; never a live price feed."""
    if not 10 <= limit <= 2000:
        raise HTTPException(422,'limit must be between 10 and 2000')
    f=frame()
    rows=f[f.Symbol==symbol.upper()].tail(limit).copy()
    if rows.empty:
        raise HTTPException(404,'Unknown symbol')
    data=[]
    for row in rows.itertuples():
        def safe(value):
            return round(float(value),4) if pd.notna(value) else None
        data.append({'date':str(row.Date.date()),'open':safe(row.Open),'high':safe(row.High),
                     'low':safe(row.Low),'close':safe(row.Close),'volume':int(row.Volume),
                     'ema20':safe(row.EMA20),'ema50':safe(row.EMA50),
                     'rsi14':safe(row.RSI14),'regime':str(row.Regime)})
    return {'symbol':symbol.upper(),'source':market_source(),
            'adjustment_note':'Demonstration bars, not an executable price feed',
            'bars':data}

@app.get('/research/latest')
def market_snapshot(symbol:str='RELIANCE'):
    f=frame(); r=f[f.Symbol==symbol.upper()]
    if r.empty:raise HTTPException(404,'Unknown symbol')
    x=r.iloc[-1]
    def value(n):
        v=x[n]
        return round(float(v),5) if pd.notna(v) else None
    return {'symbol':symbol.upper(),'signal_date':str(x.Date.date()),'Close':value('Close'),
            'EMA20':value('EMA20'),'EMA50':value('EMA50'),'RSI14':value('RSI14'),
            'ATR14':value('ATR14'),'ADX14':value('ADX14'),'regime':str(x.Regime),
            'approved_candidate':str(x.RoutedStrategy),'disclaimer':'Daily research snapshot, not a live quote'}

@app.get('/backtest/compare')
def compare():
    requests_total.labels('backtest').inc()
    return {'mode':'synthetic_or_opt_in_research','source':market_source(),
            'metrics':strategy_comparison(frame()),
            'warning':'A backtest is not a guarantee of future return. C1/C2 rows are only routing proxies, not actual agent ablations.'}

@app.get('/backtest/curve')
def backtest_curve(mode:str='ROUTER'):
    if mode not in {'ROUTER','EMA_TREND','RSI_REVERSION','BREAKOUT'}:raise HTTPException(422,'Invalid mode')
    equity,events,metrics=backtest(frame(),mode)
    return {'mode':mode,'metrics':metrics,'equity':[{'date':str(r.Date.date()),'equity':round(float(r.Equity),2)} for r in equity.itertuples()],
            'events':[{'date':str(r.Date.date()),'symbol':r.Symbol,'event':r.Event,'qty':int(r.Quantity),'price':float(r.Price)} for r in events.tail(50).itertuples()]}

@app.post('/knowledge/search')
def search(body:SearchRequest):
    guard=scan_untrusted_text(body.query)
    if not guard['ok']:
        blocked.labels('injection').inc()
        raise HTTPException(400,'Potential instruction injection in query')
    mode=os.getenv('AEGIS_RETRIEVAL_MODE','offline')
    retriever=get_retriever(mode)
    return {'mode':mode,'results':retriever.search(body.query,body.top_k,as_of=body.as_of.isoformat() if body.as_of else None),'corpus_sha256':retriever.corpus_sha256,'pipeline':'BM25 + dense retrieval -> RRF -> reranker'}

@app.post('/workflow/start')
def workflow_start(body:StartRequest,x_reviewer_token:str|None=Header(default=None)):
    if not body.disable_llm:
        auth(x_reviewer_token)  # avoid unauthorized OpenRouter spend
    thread,ctx=_build_start(body)
    try:
        out=_graph(ctx).invoke({'symbol':ctx['symbol'],'signal_date':ctx['signal_date'],'edit_count':0},
                               {'configurable':{'thread_id':thread}})
    except HTTPException:
        raise
    except Exception as e:
        blocked.labels('workflow_error').inc()
        raise HTTPException(500,f'Workflow failed: {type(e).__name__}: {e}') from e
    return {'thread_id':thread,'context':ctx,**_clean_graph_result(out)}

@app.post('/workflow/start/stream')
def workflow_start_stream(body:StartRequest,x_reviewer_token:str|None=Header(default=None)):
    if not body.disable_llm:
        auth(x_reviewer_token)
    thread,ctx=_build_start(body)
    def events():
        yield 'data: '+json.dumps({'event':'thread_started','thread_id':thread,'context':ctx})+'\n\n'
        try:
            for update in _graph(ctx).stream({'symbol':ctx['symbol'],'signal_date':ctx['signal_date'],'edit_count':0},
                        {'configurable':{'thread_id':thread}},stream_mode='updates'):
                summary={k:(v if k=='__interrupt__' else {'status':v.get('status'),'trace':v.get('trace',[])})
                         for k,v in update.items() if isinstance(v,dict)}
                yield 'data: '+json.dumps({'event':'graph_update','data':summary},default=str)+'\n\n'
            yield 'data: '+json.dumps({'event':'end','thread_id':thread})+'\n\n'
        except Exception as e:
            yield 'data: '+json.dumps({'event':'error','error':type(e).__name__})+'\n\n'
    return StreamingResponse(events(),media_type='text/event-stream')

@app.get('/workflow/status/{thread_id}')
def workflow_status(thread_id:str):
    row=run_db().execute('SELECT context FROM runs WHERE thread_id=?',(thread_id,)).fetchone()
    if not row:raise HTTPException(404,'Unknown thread')
    graph=_graph(json.loads(row[0]))
    snap=graph.get_state({'configurable':{'thread_id':thread_id}})
    return {'thread_id':thread_id,'state':snap.values,'next':list(snap.next),
            'pending_interrupts':[i.value for task in snap.tasks for i in getattr(task,'interrupts',[])]}

@app.post('/workflow/resume')
def workflow_resume(body:ResumeRequest,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    row=run_db().execute('SELECT context FROM runs WHERE thread_id=?',(body.thread_id,)).fetchone()
    if not row:raise HTTPException(404,'Unknown thread')
    if body.decision not in {'approve','edit','reject'}:raise HTTPException(422,'decision must be approve/edit/reject')
    from langgraph.types import Command
    payload={'decision':body.decision,'payload_hash':body.payload_hash,'changes':body.changes}
    out=_graph(json.loads(row[0])).invoke(Command(resume=payload),{'configurable':{'thread_id':body.thread_id}})
    if out.get('status')=='APPROVED':approved.inc()
    return {'thread_id':body.thread_id,**_clean_graph_result(out)}

@app.get('/orders/status/{request_id}')
def order_status(request_id:str):
    return broker().reconcile(request_id)

@app.get('/audit/events')
def audit():
    return [{'request_id':r[0],'event':r[1],'details':r[2],'created':r[3]} for r in broker().events()[-100:]]

@app.post('/lessons/candidate')
def lesson_candidate(body:LessonProposalRequest,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    try:
        cand=propose_failure_lesson(body.error_code)
        lesson_id=lessons().propose(cand['topic'],cand['lesson'],cand['applies_when'])
    except ValueError as e:
        raise HTTPException(422,str(e)) from e
    return {'id':lesson_id,'candidate':cand,'status':'PENDING_HUMAN'}

@app.post('/lessons/review')
def lesson_review(body:LessonReviewRequest,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    try:lessons().review(body.lesson_id,body.decision,body.reason)
    except ValueError as e:raise HTTPException(422,str(e)) from e
    return {'lesson_id':body.lesson_id,'reviewed':True}

@app.post('/lessons/freeze')
def freeze(x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    return lessons().freeze('authenticated_demo_reviewer')

@app.get('/lessons')
def all_lessons():
    l=lessons()
    return {'lessons':[{'id':r[0],'topic':r[1],'text':r[2],'condition':r[3],'status':r[4],'review_reason':r[5]} for r in l.all_lessons()],
            'frozen':l.freeze_info()}

@app.get('/metrics')
def metrics():
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)


@app.post('/simulation/run')
def simulation_run(body:SimulationSettings):
    """Date-limited historic portfolio run, with optional ALL-four-strategy comparison."""
    requests_total.labels('simulation_run').inc()
    try:
        run_frame,source,provenance=market_snapshot_context()
        result=execute_simulation(run_frame,body,save_dir=DATA/'simulation_runs',source=source,provenance=provenance)
        simulations_total.inc()
        return result
    except ValueError as e:
        raise HTTPException(422,str(e)) from e


@app.get('/simulation/recent')
def simulation_recent():
    """Return locally saved simulation metadata (no external trading accounts)."""
    folder=DATA/'simulation_runs'
    result=[]
    for path in sorted(folder.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:15] if folder.exists() else []:
        try:
            obj=json.loads(path.read_text(encoding='utf-8'))
            result.append({'run_id':obj['run_id'],'period':obj['period'],'settings':obj['settings'],
                           'created_utc':obj['created_utc']})
        except (ValueError,KeyError,OSError):
            continue
    return {'runs':result}


@app.get('/simulation/result/{run_id}')
def simulation_result(run_id:str):
    if len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):
        raise HTTPException(422,'Invalid run ID')
    path=DATA/'simulation_runs'/f'{run_id}.json'
    if not path.exists():raise HTTPException(404,'Simulation run not found')
    return json.loads(path.read_text(encoding='utf-8'))


@app.get('/research/experiments/preflight')
def research_preflight():
    return {'memory':memory_preflight(),'paid_model_calls':0}


@app.post('/research/experiments/run')
def research_experiments_run(body:ResearchSettings,x_reviewer_token:str|None=Header(default=None)):
    """Research LLM runs; blocked without explicit opt-in and reviewer auth."""
    requests_total.labels('research_experiments_run').inc()
    if needs_llm(body):
        auth(x_reviewer_token)
        if not body.consent_to_paid_calls:
            raise HTTPException(400,'Tick the explicit external-model usage consent first')
        if os.getenv('AEGIS_ENABLE_LLM_EXPERIMENTS','false').lower() != 'true':
            raise HTTPException(403,'Set AEGIS_ENABLE_LLM_EXPERIMENTS=true in private .env and restart API')
        try:require_backend_ready()
        except ValueError as exc:raise HTTPException(503,str(exc)) from None
    if required_call_budget(body)>48:
        raise HTTPException(422,'UI model-call budget exceeds 48 attempted requests')
    try:
        run_frame,source,provenance=market_snapshot_context()
        if source=='nsepython':
            from datetime import date
            if provenance.get('requested_start'):
                earliest=date.fromisoformat(provenance['requested_start']);latest=date.fromisoformat(provenance['requested_end'])
                if body.start_date and body.start_date<earliest:raise ValueError('Research cases cannot predate the frozen-universe evaluation start')
                if body.end_date and (body.end_date<earliest or body.end_date>latest):raise ValueError('Research end date is outside the downloaded evaluation window')
                if body.start_date is None:body=body.model_copy(update={'start_date':earliest})
        result=execute_research(run_frame,body,source=source,provenance=provenance,
                 model=model_name(),
                 save_dir=DATA/'research_runs')
        for r in result['summary']:
            research_completed_total.labels(r['config']).inc()
            if r['model_calls']:
                research_llm_attempts_total.labels(r['config']).inc(r['model_calls'])
        return result
    except ResearchPreflightError as e:
        raise HTTPException(e.status,e.detail()) from None
    except ValueError as e:
        raise HTTPException(422,str(e)) from e


@app.get('/research/experiments/recent')
def research_experiments_recent():
    folder=DATA/'research_runs'
    result=[]
    for path in sorted(folder.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:15] if folder.exists() else []:
        try:
            obj=json.loads(path.read_text(encoding='utf-8'))
            result.append({'run_id':obj['run_id'],'model':obj['model'],'created_utc':obj['created_utc'],
                           'settings':obj['settings'],'summary':obj['summary']})
        except (ValueError,KeyError,OSError):
            continue
    return {'runs':result}


@app.get('/research/experiments/result/{run_id}')
def research_experiments_result(run_id:str):
    if len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):
        raise HTTPException(422,'Invalid run ID')
    path=DATA/'research_runs'/f'{run_id}.json'
    if not path.exists():raise HTTPException(404,'Research run not found')
    return json.loads(path.read_text(encoding='utf-8'))


class ReflectionRequest(BaseModel):
    run_id:str
    case_id:str
    consent_to_paid_calls:bool=False

@app.post('/lessons/reflect')
def reflect_lesson(body:ReflectionRequest,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    if not body.consent_to_paid_calls:raise HTTPException(400,'Reflection needs consent for one paid model call')
    if os.getenv('AEGIS_ENABLE_LLM_EXPERIMENTS','false').lower()!='true':
        raise HTTPException(403,'External model experiments are not enabled')
    try:require_backend_ready()
    except ValueError as exc:raise HTTPException(503,str(exc)) from None
    if lessons().freeze_info():raise HTTPException(422,'Playbook is frozen; do not generate lessons for this version')
    from aegistrade.reflection import reflect_development_failure
    try:
        candidate,usage=reflect_development_failure(research_experiments_result(body.run_id),body.case_id,
                            model_name())
        lesson_id=lessons().propose(candidate['topic'],candidate['lesson'],candidate['applies_when'])
        return {'id':lesson_id,'candidate':candidate,'usage':usage,'status':'PENDING_HUMAN',
                'source_run_id':body.run_id,'source_case_id':body.case_id}
    except ValueError as exc:raise HTTPException(422,str(exc)) from None
    except Exception:raise HTTPException(502,'Reflection failed; inspect provider access and response format') from None


class KillSwitchRequest(BaseModel):
    enabled:bool
    reason:str=Field(min_length=3,max_length=300)

@app.get('/controls')
def control_status():
    return {'kill_switch_enabled':broker().kill_switch_enabled(),'live_broker_enabled':False}

@app.post('/controls/kill-switch')
def change_kill_switch(body:KillSwitchRequest,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    return broker().set_kill_switch(body.enabled,body.reason)


def market_provenance():
    if market_source()!='nsepython':
        return {'provider':market_source(),'synthetic':market_source()=='synthetic'}
    path=nse_dataset_directory()/'manifest.json'
    details=json.loads(path.read_text())
    result={k:details.get(k) for k in ('provider','status','requested_start','requested_end','membership_mode',
        'membership_asof','survivorship_bias','price_adjustment','universe_selection','symbols','sha256','limitation','universe_id','universe_name','selection_bias','coverage_policy','history_availability_note')}
    try:result['dataset_dir']=str(nse_dataset_directory().resolve().relative_to(DATA.resolve()))
    except ValueError:result['dataset_dir']=str(nse_dataset_directory().resolve())
    result['universe_id']=details.get('universe_id') or market_config().get('universe_id','nifty20')
    return result

class SelectionRequest(BaseModel):
    asof:str|None=None
    reference_capital:float=Field(default=200000,ge=1000,le=100000000)

@app.post('/market/selection')
def stock_selection(body:SelectionRequest):
    from aegistrade.selection import prepare_selection_features,rank_candidates,SelectionPolicy
    from dataclasses import asdict
    run_frame,source,provenance=market_snapshot_context()
    f=prepare_selection_features(run_frame)
    try:
        if body.asof:f=f[f.Date<=pd.Timestamp(body.asof)]
    except ValueError:raise HTTPException(422,'Invalid as-of date') from None
    if f.empty:raise HTTPException(422,'No data on or before the selected date')
    when=f.Date.max()
    if provenance.get('requested_start') and when<pd.Timestamp(provenance['requested_start']):
        raise HTTPException(422,'Stock selection cannot predate the frozen-universe evaluation start')
    daily=f[f.Date==when]
    audit=rank_candidates(daily,equity=body.reference_capital,cash=body.reference_capital)
    return {'asof':str(when.date()),'reference_capital':body.reference_capital,
            'policy':asdict(SelectionPolicy()),'audit':audit,'provenance':provenance,
            'note':'Deterministic shortlist, not order approval. C2 research and human approval remain mandatory for supervised submissions.'}


@app.get('/market/datasets')
def market_datasets():
    from aegistrade.universes import catalogue
    from aegistrade.dataset_jobs import status
    active=nse_dataset_directory() if market_source()=='nsepython' else DATA/'__no_active_nse_dataset__'
    rows=catalogue(DATA,active,legacy=legacy_nse_directory())
    for row in rows:row['preparation']=status(DATA,row['id'])
    return {'datasets':rows,'generation_calls':0}


@app.get('/market/dataset')
def market_dataset_status(universe_id:str|None=None):
    from aegistrade.universes import folder
    from aegistrade.dataset_jobs import status
    key=universe_id or market_config().get('universe_id','nifty20')
    try:target=folder(DATA,key,legacy_nse_directory())
    except ValueError as exc:raise HTTPException(422,str(exc)) from None
    path=target/'manifest.json'
    return {'universe_id':key,'active_source':market_source(),
            'active':market_source()=='nsepython' and target.resolve()==nse_dataset_directory().resolve(),
            'available':path.exists(),'manifest':json.loads(path.read_text()) if path.exists() else None,
            'preparation':status(DATA,key),
            'cached_chunks':sum(1 for _ in (target/'chunks').glob('*/*.csv')) if target.exists() else 0}


class DatasetPreparation(BaseModel):
    universe_id:str
    start_date:date
    end_date:date

@app.post('/market/dataset/prepare')
def prepare_nse_dataset(body:DatasetPreparation,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    from aegistrade.dataset_jobs import prepare
    try:return prepare(DATA,body.universe_id,body.start_date,body.end_date,legacy=legacy_nse_directory())
    except ValueError as exc:raise HTTPException(422,str(exc)) from None


class DatasetActivation(BaseModel):
    acknowledge_provisional_data:bool=False
    universe_id:str|None=None

@app.post('/market/dataset/activate')
def activate_nse_dataset(body:DatasetActivation,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    if not body.acknowledge_provisional_data:raise HTTPException(400,'Acknowledge dataset provenance and corporate-action limitations before activation')
    from aegistrade.nse_data import load_dataset
    from aegistrade.universes import folder,profile,validate_manifest
    key=body.universe_id or market_config().get('universe_id','nifty20')
    try:
        target=folder(DATA,key,legacy_nse_directory());data,manifest=load_dataset(target)
        validate_manifest(key,manifest)
        prepared=prepare_indicators(data)
    except (ValueError,FileNotFoundError,KeyError):raise HTTPException(422,'A complete validated dataset is required; prepare the selected universe first') from None
    global _frame
    with _market_lock:
        legacy=legacy_nse_directory()
        def stored(path):
            try:return str(path.resolve().relative_to(DATA.resolve()))
            except ValueError:return str(path.resolve())
        config={'source':'nsepython','universe_id':key,'dataset_dir':stored(target),'legacy_dataset_dir':stored(legacy)}
        tmp=DATA/('market_config.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(config,indent=2));tmp.replace(DATA/'market_config.json')
        _frame=prepared
    return {'activated':True,'source':'nsepython','universe_id':key,'universe_name':profile(key)['name'],'symbols':len(manifest['symbols']),'rows':len(data),
            'note':'New activity uses this dataset. Existing portfolio workers keep their captured input; saved runs retain original provenance.'}


@app.get('/market/ohlcv.csv')
def export_active_ohlcv():
    data=frame()[['Date','Symbol','Open','High','Low','Close','Volume']].copy()
    data['Date']=data.Date.dt.strftime('%Y-%m-%d')
    return StreamingResponse(iter([data.to_csv(index=False)]),media_type='text/csv',
        headers={'Content-Disposition':'attachment; filename="aegistrade_active_ohlcv.csv"'})


@app.get('/knowledge/status')
def knowledge_status():
    from aegistrade.corpus import corpus_info
    info=corpus_info();path=DATA/'rag'/'index_status.json'
    built=json.loads(path.read_text()) if path.exists() else None
    mode=os.getenv('AEGIS_RETRIEVAL_MODE','offline')
    expected_store='QdrantIndex' if os.getenv('AEGIS_QDRANT_URL') else 'ChromaIndex'
    verified=bool(built and built.get('mode')==mode and built.get('corpus',{}).get('sha256')==info['sha256'] and
                  (mode!='neural' or built.get('vector_store')==expected_store))
    return {'mode':mode,'corpus':info,'verified_index_for_current_corpus':verified,
            'index':built,'pipeline':'BM25 + MiniLM vectors + RRF + cross-encoder' if mode=='neural' else 'BM25 + TF-IDF surrogate + RRF + lexical rerank',
            'generation':'Retrieved passages feed C2 via MCP. This screen performs retrieval only, not paid answer generation.'}

class CompanyResearchRequest(BaseModel):
    symbol:str=Field(pattern=r'^[A-Z0-9][A-Z0-9_&-]{1,29}$')
    signal_date:date
    refresh:bool=False

@app.get('/company/research')
def company_research_status(symbol:str,signal_date:date):
    from aegistrade.company_research import read_company_research
    try:return read_company_research(symbol,signal_date.isoformat())
    except (ValueError,KeyError,TypeError,OSError):raise HTTPException(422,'Invalid or changed company evidence pack') from None

@app.post('/company/research/prepare')
def prepare_company_evidence(body:CompanyResearchRequest,x_reviewer_token:str|None=Header(default=None)):
    """Public archive download/extraction; no paid model request. Reviewer-authorized bounded work."""
    auth(x_reviewer_token)
    f=frame()
    if body.symbol not in set(f.Symbol) or not ((f.Symbol==body.symbol)&(f.Date.dt.date==body.signal_date)).any():
        raise HTTPException(422,'Select a symbol/session present in the active dataset')
    from aegistrade.company_research import prepare_company_research
    try:return prepare_company_research(body.symbol,body.signal_date.isoformat(),refresh=body.refresh)
    except Exception:raise HTTPException(502,'Public company archive unavailable or invalid; no model calls made. Retry preparation later.') from None

# C2 historical portfolio jobs: paid consent and reviewer auth precede all model work.
from aegistrade.c2_portfolio import C2PortfolioSettings

def _paid_c2_portfolio_auth(token,consent):
    auth(token)
    if not consent:raise HTTPException(400,'Explicit paid-run consent is required')
    if os.getenv('AEGIS_ENABLE_LLM_EXPERIMENTS','false').lower()!='true':
        raise HTTPException(403,'Enable external model experiments in the private .env')
    try:require_backend_ready()
    except ValueError as exc:raise HTTPException(503,str(exc)) from None

@app.post('/simulation/c2/run')
def c2_portfolio_start(body:C2PortfolioSettings,x_reviewer_token:str|None=Header(default=None)):
    _paid_c2_portfolio_auth(x_reviewer_token,body.consent_to_paid_calls)
    from aegistrade.c2_portfolio import create_run,launch,status
    try:
        run_frame,source,provenance=market_snapshot_context()
        rid=create_run(run_frame,body,source=source,provenance=provenance)
        launch(rid,run_frame);return status(rid)
    except ValueError as e:raise HTTPException(422,str(e)) from None

@app.get('/simulation/c2/recent')
def c2_portfolio_recent():
    from aegistrade.c2_portfolio import root
    runs=[]
    for path in sorted(root().glob('*/state.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:20]:
        try:
            s=json.loads(path.read_text());runs.append({k:s[k] for k in ('run_id','created_utc','status','settings')})
        except (OSError,ValueError,KeyError):continue
    return {'runs':runs}

@app.get('/simulation/c2/status/{run_id}')
def c2_portfolio_status(run_id:str):
    from aegistrade.c2_portfolio import status
    try:return status(run_id)
    except FileNotFoundError:raise HTTPException(404,'C2 portfolio run not found') from None
    except ValueError:raise HTTPException(422,'Invalid C2 portfolio run') from None

class C2PortfolioResume(BaseModel):
    additional_model_calls:int=Field(default=48,ge=0,le=2400)
    consent_to_paid_calls:bool=False

def frame_for_saved_portfolio(run_id):
    """Resolve original NSE data by checksum, not whichever universe is active now."""
    from aegistrade.c2_portfolio import load
    from aegistrade.universes import folder,PROFILES
    from aegistrade.nse_data import load_dataset
    state=load(run_id)
    if state.get('data_source')!='nsepython':return frame()
    provenance=state.get('data_provenance',{});expected=provenance.get('sha256')
    for key in PROFILES:
        target=folder(DATA,key,legacy_nse_directory());manifest=target/'manifest.json'
        if not manifest.exists():continue
        saved=json.loads(manifest.read_text())
        if expected and saved.get('sha256')==expected:
            data,_=load_dataset(target);return prepare_indicators(data)
    raise ValueError('Original frozen-universe dataset is missing or changed; restore it before resuming this portfolio')


@app.post('/simulation/c2/resume/{run_id}')
def c2_portfolio_resume(run_id:str,body:C2PortfolioResume,x_reviewer_token:str|None=Header(default=None)):
    _paid_c2_portfolio_auth(x_reviewer_token,body.consent_to_paid_calls)
    from aegistrade.c2_portfolio import resume,status
    try:resume(run_id,frame_for_saved_portfolio(run_id),body.additional_model_calls);return status(run_id)
    except FileNotFoundError:raise HTTPException(404,'C2 portfolio run not found') from None
    except ValueError as e:raise HTTPException(409,str(e)) from None

@app.post('/simulation/c2/pause/{run_id}')
def c2_portfolio_pause(run_id:str,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    from aegistrade.c2_portfolio import state_path
    try:
        path=state_path(run_id)
        if not path.exists():raise HTTPException(404,'C2 portfolio run not found')
        (path.parent/'cancel').touch();return {'pause_requested':True,'note':'Stops at the next safe boundary; an active provider request may finish.'}
    except ValueError:raise HTTPException(422,'Invalid run ID') from None

@app.get('/simulation/c2/research/{run_id}/{decision_id}')
def c2_portfolio_research(run_id:str,decision_id:str):
    from aegistrade.c2_portfolio import state_path,valid_id
    try:path=state_path(run_id).parent/'research'/f'{valid_id(decision_id)}.json'
    except ValueError:raise HTTPException(422,'Invalid research ID') from None
    if not path.exists():raise HTTPException(404,'Research record not found')
    return json.loads(path.read_text())


class PortfolioLessonDraft(BaseModel):
    run_id:str
class PortfolioLessonReview(BaseModel):
    candidate_id:str
    decision:str
    reason:str
    lesson:str|None=None
    applies_when:str|None=None
class PortfolioLessonFreeze(BaseModel):
    candidate_ids:list[str]

@app.get('/portfolio-lessons')
def portfolio_lessons_get():
    from aegistrade import portfolio_memory as memory
    try:return {'candidates':memory.list_candidates(),'versions':memory.list_versions(),'model_calls':0}
    except ValueError as exc:raise HTTPException(422,str(exc)) from None

@app.post('/portfolio-lessons/draft')
def portfolio_lessons_draft(body:PortfolioLessonDraft,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    from aegistrade import portfolio_memory as memory
    try:return memory.draft_from_run(body.run_id)
    except ValueError as exc:raise HTTPException(422,str(exc)) from None

@app.post('/portfolio-lessons/review')
def portfolio_lessons_review(body:PortfolioLessonReview,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    from aegistrade import portfolio_memory as memory
    try:
        memory.review(body.candidate_id,body.decision,body.reason,body.lesson,body.applies_when)
        return {'ok':True,'model_calls':0}
    except ValueError as exc:raise HTTPException(422,str(exc)) from None

@app.post('/portfolio-lessons/freeze')
def portfolio_lessons_freeze(body:PortfolioLessonFreeze,x_reviewer_token:str|None=Header(default=None)):
    auth(x_reviewer_token)
    from aegistrade import portfolio_memory as memory
    try:return memory.freeze(body.candidate_ids)
    except ValueError as exc:raise HTTPException(422,str(exc)) from None
