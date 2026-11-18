"""UI-safe, optionally paid C0/C1/C2 routing comparisons. No execution tools."""
from __future__ import annotations
from .company_research import company_pack_researchable
from datetime import date, datetime, timezone
from pathlib import Path
import json
import math
import os
import sqlite3
from contextlib import closing
import uuid
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from .llm_research import run_research_case
from .simulation_service import normalize
from .fees import charge_breakdown, FEE_MODEL


FORWARD_OUTCOME_SESSIONS = 20
FORWARD_OUTCOME_NOTIONAL = 100_000.0
FORWARD_OUTCOME_SLIPPAGE_BPS = 10.0


def attach_forward_outcomes(outputs: list[dict], frame: pd.DataFrame) -> dict:
    """Attach a fixed post-decision paper outcome without leaking it into research.

    Every case/config receives the same independent notional and price window.
    This is a secondary outcome metric, not a persistent portfolio backtest.
    """
    for item in outputs:
        snapshot=item['snapshot'];symbol=snapshot['symbol'];signal=pd.Timestamp(snapshot['date'])
        future=frame[(frame.Symbol==symbol)&(pd.to_datetime(frame.Date)>signal)].sort_values('Date').head(FORWARD_OUTCOME_SESSIONS)
        outcome={'method':'FIXED_20_SESSION_NEXT_OPEN','notional':FORWARD_OUTCOME_NOTIONAL,
                 'required_sessions':FORWARD_OUTCOME_SESSIONS,'available_sessions':int(len(future)),
                 'fee_model':FEE_MODEL,'slippage_bps':FORWARD_OUTCOME_SLIPPAGE_BPS}
        if len(future)<FORWARD_OUTCOME_SESSIONS:
            item['forward_outcome']={**outcome,'available':False,'reason':'A complete post-decision window is unavailable'}
            continue
        config=item['config'];action=item.get('portfolio_action') or ('ENTER' if config=='C0' else None)
        participates=bool(item.get('guard_pass')) and item.get('selected_strategy') not in {None,'NONE'} and action=='ENTER'
        entry_bar=future.iloc[0];exit_bar=future.iloc[-1]
        entry=float(entry_bar.Open)*(1+FORWARD_OUTCOME_SLIPPAGE_BPS/10000)
        exit_price=float(exit_bar.Close)*(1-FORWARD_OUTCOME_SLIPPAGE_BPS/10000)
        if participates:
            # Include the buy charge in affordability so the case never spends
            # more than its fixed reference allocation.
            unit_cost=entry+charge_breakdown(entry,'BUY')['total']
            quantity=max(0,math.floor(FORWARD_OUTCOME_NOTIONAL/unit_cost))
            buy_turnover=quantity*entry; sell_turnover=quantity*exit_price
            buy_fee=charge_breakdown(buy_turnover,'BUY')['total'];sell_fee=charge_breakdown(sell_turnover,'SELL')['total']
            pnl=sell_turnover-sell_fee-buy_turnover-buy_fee
        else:
            quantity=0;buy_fee=0.;sell_fee=0.;pnl=0.
        item['forward_outcome']={**outcome,'available':True,'participated':participates,
            'decision':'ENTER' if participates else 'STAY_CASH','entry_date':entry_bar.Date.date().isoformat(),
            'exit_date':exit_bar.Date.date().isoformat(),'entry_price':round(entry,4),
            'exit_price':round(exit_price,4),'quantity':quantity,'fees':round(buy_fee+sell_fee,4),
            'pnl':round(pnl,2),'return_pct':round(100*pnl/FORWARD_OUTCOME_NOTIONAL,4),
            'reason':None if participates else 'Research did not produce an eligible ENTER decision'}
    return {'method':'FIXED_20_SESSION_NEXT_OPEN','sessions':FORWARD_OUTCOME_SESSIONS,
            'notional_per_case':FORWARD_OUTCOME_NOTIONAL,'slippage_bps':FORWARD_OUTCOME_SLIPPAGE_BPS,
            'fee_model':FEE_MODEL,'interpretation':'Secondary, independent case outcome calculated after research; not a persistent portfolio or architecture-quality score.'}


class ResearchPreflightError(ValueError):
    def __init__(self,code,message,action,*,context=None,status=422):
        super().__init__(message);self.code=code;self.action=action;self.context=context or {};self.status=status
    def detail(self):
        return {'code':self.code,'message':str(self),'action':self.action,'context':self.context,
                'paid_model_calls_started':False}


def memory_preflight():
    """Read readiness without creating/freezing/editing the user's lesson store."""
    path=Path(os.getenv('AEGIS_DATA_DIR','data'))/'reviewed_lessons.sqlite'
    frozen=None;count=0
    if path.exists():
        try:
            with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)) as conn:
                row=conn.execute("SELECT value FROM playbook_meta WHERE key='frozen'").fetchone()
                frozen=json.loads(row[0]) if row else None
                count=conn.execute("SELECT count(*) FROM lessons WHERE status='ACCEPTED'").fetchone()[0]
        except (sqlite3.Error,ValueError,TypeError):
            return {'available':False,'accepted_lessons':0,'frozen':None,'reason':'The reviewed playbook could not be read. Leave lesson memory off and inspect Learning & Lessons.'}
    available=bool(frozen and frozen.get('count',0)>0 and count>0)
    reason=('Frozen reviewed lessons are ready.' if available else
            'No frozen playbook with accepted lessons exists. Leave Use frozen human-reviewed lessons off. Freeze accepted lessons in Learning & Lessons only after reviewing them.')
    return {'available':available,'accepted_lessons':count,'frozen':frozen,'reason':reason}


def load_reviewed_memory():
    readiness=memory_preflight()
    if not readiness['available']:
        raise ResearchPreflightError('MEMORY_NOT_READY',readiness['reason'],
            'Run with lesson memory off. To enable it later, accept relevant lessons in Learning & Lessons and explicitly freeze the reviewed playbook.')
    from .lessons import ReviewedPlaybook
    book=ReviewedPlaybook(Path(os.getenv('AEGIS_DATA_DIR','data'))/'reviewed_lessons.sqlite')
    try:
        manifest=book.freeze_info()
        if not manifest or not manifest.get('count'):raise ValueError('Frozen reviewed playbook changed; inspect Learning & Lessons')
        lessons=[]
        for topic in ('regime','grounding'):lessons.extend(book.retrieve(topic,['indicator','strategy','regime','decision']))
        return lessons,manifest
    finally:book.conn.close()


class ResearchSettings(BaseModel):
    configuration: str = "C0"  # C0 / C1 / C2 / ALL
    cases: int = Field(default=1, ge=1, le=3)
    start_date: date | None = None
    end_date: date | None = None
    consent_to_paid_calls: bool = False
    max_output_tokens_per_case: int = Field(default=3600, ge=2400, le=4800)

    selection_run_id: str|None = Field(default=None,pattern=r"^[0-9a-f]{32}$")
    automatic_stock_selection: bool = False
    reference_capital: float = Field(default=200000,ge=1000,le=100000000)
    use_memory: bool = False
    dataset_split: str = "development"
    research_purpose: str = "ENTRY"

    @model_validator(mode="after")
    def validate_config(self):
        if self.dataset_split not in {"development", "heldout"}:
            raise ValueError("dataset_split must be development or heldout")
        if self.configuration not in {"C0", "C1", "C2", "ALL"}:
            raise ValueError("configuration must be C0, C1, C2 or ALL")
        if self.research_purpose not in {'ENTRY','HOLDING_REVIEW'}:
            raise ValueError('research_purpose must be ENTRY or HOLDING_REVIEW')
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Invalid date range")
        return self


def needs_llm(s: ResearchSettings) -> bool:
    return s.configuration != "C0"


def required_call_budget(s: ResearchSettings) -> int:
    multiplier = {"C0":0, "C1":8, "C2":8, "ALL":16}[s.configuration]
    return s.cases * multiplier


def select_cases(frame: pd.DataFrame, s: ResearchSettings, *, allowed_symbols=None) -> list[dict]:
    f = frame[frame.Ready].sort_values(["Date", "Symbol"]).copy()
    if s.start_date:
        f = f[f.Date.dt.date >= s.start_date]
    if s.end_date:
        f = f[f.Date.dt.date <= s.end_date]
    selection_lookup={}
    if s.automatic_stock_selection:
        from .selection import prepare_selection_features,rank_candidates
        if f.empty:raise ValueError('No market data within selected dates')
        asof=f.Date.max()
        prepared=prepare_selection_features(frame)
        daily=prepared[prepared.Date==asof]
        ranked=rank_candidates(daily,equity=s.reference_capital,cash=s.reference_capital)
        eligible=[r for r in ranked if r['eligible'] and (r['symbol'] in allowed_symbols if allowed_symbols is not None else r['selected'])][:s.cases]
        if not eligible:raise ValueError('No eligible stock at the selected final date; no paid model request was made. Choose an earlier date or inspect the screening reasons.')
        selection_lookup={r['symbol']:r for r in eligible}
        chosen=pd.concat([f[(f.Symbol==r['symbol'])&(f.Date==asof)] for r in eligible])
    else:
        if len(f)<s.cases:raise ValueError('Insufficient ready historical rows within selected period')
        chosen=f.iloc[[round(i*(len(f)-1)/max(1,s.cases-1)) for i in range(s.cases)]] if s.cases>1 else f.iloc[[-1]]
    cases=[{"symbol": str(r.Symbol), "date": r.Date.date().isoformat(),
             "regime": str(r.Regime), "approved_candidate": str(r.RoutedStrategy),
             **({"selection_score":selection_lookup[r.Symbol]['score'],"selection_rank":selection_lookup[r.Symbol]['rank'],
                 "average_turnover_20_inr":selection_lookup[r.Symbol]['average_turnover_20_inr']} if r.Symbol in selection_lookup else {}),
             **{k: float(getattr(r, k)) for k in ("Close", "RSI14", "ADX14", "EMA20", "EMA50", "ATR14", "PriorHigh", "PullbackRecent")}}
            for r in chosen.itertuples()]
    if s.research_purpose=='HOLDING_REVIEW':
        for case in cases:
            case['research_purpose']='HOLDING_REVIEW'
            case['holding_context']={'quantity':1,'entry_price':case['Close'],'stop_price':max(.01,case['Close']-2*case['ATR14']),
                'strategy':case['approved_candidate'] if case['approved_candidate']!='NONE' else 'EMA_TREND',
                'holding_sessions':5,'review_trigger':'Controlled AI Experiment holding review'}
    return cases


def execute_research(frame: pd.DataFrame, s: ResearchSettings, *, model: str|None=None, save_dir: Path | None = None, source: str|None=None, provenance:dict|None=None) -> dict:
    from .llm_backend import require_backend_ready,model_name,identity
    model=model_name(model)
    if needs_llm(s):
        if not s.consent_to_paid_calls:
            raise ValueError("Paid model requests require explicit consent_to_paid_calls")
        require_backend_ready()
        if os.getenv("AEGIS_ENABLE_LLM_EXPERIMENTS", "false").lower() != "true":
            raise ValueError("Enable AEGIS_ENABLE_LLM_EXPERIMENTS=true in your private .env first")
    approved_lessons,memory_manifest=load_reviewed_memory() if s.use_memory else ([],None)
    allowed_symbols=None
    if s.selection_run_id:
        if not s.automatic_stock_selection or not s.end_date:raise ValueError('Selection hand-off needs automatic selection and an explicit date')
        path=Path(os.getenv('AEGIS_DATA_DIR','data'))/'simulation_runs'/f'{s.selection_run_id}.json'
        if not path.exists():raise ValueError('Source simulation run not found')
        simulation=json.loads(path.read_text())
        audit=simulation.get('stock_selection',{}).get('audits',{}).get('ROUTER',[])
        allowed_symbols={r['symbol'] for r in audit if r['date']==s.end_date.isoformat() and r['selected']}
        if not allowed_symbols:raise ValueError('The source simulation selected no new stock on this date')
    cases = select_cases(frame, s,allowed_symbols=allowed_symbols)
    if needs_llm(s):
        from .company_research import prepare_company_research
        for case in cases:
            try:pack=prepare_company_research(case['symbol'],case['date'])
            except Exception as exc:
                from .dated_web import eligible
                if eligible(case):continue
                raise ResearchPreflightError('COMPANY_ARCHIVE_UNAVAILABLE',
                    f"Could not prepare historical company evidence for {case['symbol']} on {case['date']}. no paid model call was made.",
                    'Open Historical company research, prepare/inspect this exact stock and date, then retry. Public archive access may be unavailable.',
                    context={'symbol':case['symbol'],'date':case['date'],'error_type':type(exc).__name__},status=502) from None
            from .dated_web import eligible
            if not company_pack_researchable(pack) and not eligible(case):
                reasons='; '.join(pack.get('reasons',[]))
                raise ResearchPreflightError('COMPANY_EVIDENCE_INSUFFICIENT',
                    f"Historical company evidence insufficient for {case['symbol']} on {case['date']}: {reasons}. no paid model call was made.",
                    'Prepare/inspect this exact stock/date in Historical company research. Resolve the missing filings or choose another case with available evidence; this check cannot be bypassed.',
                    context={'symbol':case['symbol'],'date':case['date']})
    modes = ["C0", "C1", "C2"] if s.configuration == "ALL" else [s.configuration]
    outputs = []
    for snapshot in cases:
        for config in modes:
            output = run_research_case(snapshot, config, model=model,
                                       max_calls=8, max_output_tokens=s.max_output_tokens_per_case,
                                       **({"lessons": approved_lessons} if s.use_memory else {}))
            outputs.append({"snapshot":normalize(snapshot),"case_id": f"{snapshot['symbol']}-{snapshot['date']}", **normalize(output)})
    forward_policy=attach_forward_outcomes(outputs,frame) if s.research_purpose=='ENTRY' else {
        'method':'NOT_APPLICABLE','interpretation':'Forward entry P&L is not computed for holding-review experiments.'}
    summary=[]
    for config in modes:
        rows = [x for x in outputs if x["config"] == config]
        usages = [u for x in rows for u in x.get("usage", [])]
        tokens = sum(int(u.get("total_tokens") or 0) for u in usages)
        calls = sum(int(x.get("llm_calls") or 0) for x in rows)
        reported_cost = [float(u["cost"]) for u in usages if isinstance(u.get("cost"), (int,float))]
        latencies=sorted(float(x.get('latency_s') or 0) for x in rows)
        p95=latencies[min(len(latencies)-1,max(0,int(.95*len(latencies)+.999999)-1))]
        errors=sum(bool(x.get('model_errors')) for x in rows)
        passes=sum(bool(x.get('guard_pass')) and not x.get('model_errors') for x in rows)
        summary.append({"config": config, "cases": len(rows),"task_success_count":passes,
                        "task_success_pct":round(100*passes/len(rows),2),
                        "guard_pass_count": sum(bool(x.get("guard_pass")) for x in rows),
                        "policy_violation_count":sum(not x.get('guard_pass') and not x.get('model_errors') for x in rows),
                        "model_error_count": errors,
                        "model_calls": calls, "budget_unit":identity(model=model)["budget_unit"] if config!="C0" else "none", "total_tokens_reported": tokens,
                        "reported_cost_usd": round(sum(reported_cost), 8) if usages and len(reported_cost)==len(usages) else None,
                        "cost_reporting_complete":bool(usages) and len(reported_cost)==len(usages),
                        "forward_outcomes_available":sum(bool(x.get('forward_outcome',{}).get('available')) for x in rows),
                        "forward_entries":sum(bool(x.get('forward_outcome',{}).get('participated')) for x in rows),
                        "forward_pnl":round(sum(float(x.get('forward_outcome',{}).get('pnl') or 0) for x in rows if x.get('forward_outcome',{}).get('available')),2),
                        "forward_return_pct_on_case_notional":round(100*sum(float(x.get('forward_outcome',{}).get('pnl') or 0) for x in rows if x.get('forward_outcome',{}).get('available'))/(FORWARD_OUTCOME_NOTIONAL*max(1,sum(bool(x.get('forward_outcome',{}).get('available')) for x in rows))),4),
                        "mean_latency_s": round(sum(latencies)/len(rows),3),"median_latency_s":round(latencies[len(latencies)//2],3),
                        "p95_latency_s":round(p95,3)})
    result = normalize({"run_id": uuid.uuid4().hex,
                        "created_utc": datetime.now(timezone.utc).isoformat(),
                        "model": model if needs_llm(s) else "not_used",
                        "inference":identity(model=model) if needs_llm(s) else {'backend':'none','budget_unit':'none'},
                        "settings": s.model_dump(mode="json"),"data_source":source,"data_provenance":provenance or {},
                        "prompt_version": __import__("aegistrade.agentic",fromlist=["CONFIG"]).CONFIG["version"],
                        "memory_manifest":memory_manifest,
                        "knowledge_corpus":__import__("aegistrade.corpus",fromlist=["corpus_info"]).corpus_info(),
                        "architecture_comparison_contract":{
                            "primary_comparison":["C1_SINGLE_AGENT","C2_MULTI_AGENT"],
                            "secondary_reference":"C0_DETERMINISTIC_NO_LLM",
                            "same_cases":True,"same_model":True,"same_evidence":True,
                            "same_available_read_tools":True,"same_case_call_ceiling":8,
                            "same_case_output_token_budget":s.max_output_tokens_per_case,
                            "c1_tools":["market_snapshot","company_evidence","search_policy","check_strategy","search_dated_web"],
                            "c2_tool_union":["market_snapshot","company_evidence","search_policy","check_strategy","search_dated_web"],
                            "interpretation":"C1 versus C2 tests architecture quality and cost. C0 is not the single-agent baseline."
                        },
                        "forward_outcome_policy":forward_policy,
                        "max_possible_paid_calls": required_call_budget(s),
                        "summary":summary, "outputs":outputs,
                        "status":"COMPLETED",
                        "human_review_required":[],"human_decisions":[],
                        "disclaimer":"Research-only route audit. Not portfolio backtesting, investment advice, or order execution. Actual costs depend on provider usage."})
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / f"{result['run_id']}.json").write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    return result
