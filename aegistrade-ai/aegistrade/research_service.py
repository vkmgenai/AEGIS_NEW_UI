"""UI-safe, optionally paid C0/C1/C2 routing comparisons. No execution tools."""
from __future__ import annotations
from .company_research import company_pack_researchable
from datetime import date, datetime, timezone
from pathlib import Path
import json
import os
import sqlite3
from contextlib import closing
import uuid
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from .llm_research import run_research_case
from .simulation_service import normalize


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
    max_output_tokens_per_case: int = Field(default=4800, ge=4800, le=6400)

    selection_run_id: str|None = Field(default=None,pattern=r"^[0-9a-f]{32}$")
    automatic_stock_selection: bool = False
    reference_capital: float = Field(default=200000,ge=1000,le=100000000)
    use_memory: bool = False
    dataset_split: str = "development"

    @model_validator(mode="after")
    def validate_config(self):
        if self.dataset_split not in {"development", "heldout"}:
            raise ValueError("dataset_split must be development or heldout")
        if self.configuration not in {"C0", "C1", "C2", "ALL"}:
            raise ValueError("configuration must be C0, C1, C2 or ALL")
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
    return [{"symbol": str(r.Symbol), "date": r.Date.date().isoformat(),
             "regime": str(r.Regime), "approved_candidate": str(r.RoutedStrategy),
             **({"selection_score":selection_lookup[r.Symbol]['score'],"selection_rank":selection_lookup[r.Symbol]['rank'],
                 "average_turnover_20_inr":selection_lookup[r.Symbol]['average_turnover_20_inr']} if r.Symbol in selection_lookup else {}),
             **{k: float(getattr(r, k)) for k in ("Close", "RSI14", "ADX14", "EMA20", "EMA50", "ATR14")}}
            for r in chosen.itertuples()]


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
    summary=[]
    for config in modes:
        rows = [x for x in outputs if x["config"] == config]
        usages = [u for x in rows for u in x.get("usage", [])]
        tokens = sum(int(u.get("total_tokens") or 0) for u in usages)
        calls = sum(int(x.get("llm_calls") or 0) for x in rows)
        reported_cost = [float(u["cost"]) for u in usages if isinstance(u.get("cost"), (int,float))]
        summary.append({"config": config, "cases": len(rows),
                        "guard_pass_count": sum(bool(x.get("guard_pass")) for x in rows),
                        "model_error_count": sum(bool(x.get("model_errors")) for x in rows),
                        "model_calls": calls, "budget_unit":identity(model=model)["budget_unit"] if config!="C0" else "none", "total_tokens_reported": tokens,
                        "reported_cost_usd": round(sum(reported_cost), 8) if usages and len(reported_cost)==len(usages) else None,
                        "cost_reporting_complete":bool(usages) and len(reported_cost)==len(usages),
                        "mean_latency_s": round(sum(float(x.get("latency_s") or 0) for x in rows) / len(rows), 3)})
    result = normalize({"run_id": uuid.uuid4().hex,
                        "created_utc": datetime.now(timezone.utc).isoformat(),
                        "model": model if needs_llm(s) else "not_used",
                        "inference":identity(model=model) if needs_llm(s) else {'backend':'none','budget_unit':'none'},
                        "settings": s.model_dump(mode="json"),"data_source":source,"data_provenance":provenance or {},
                        "prompt_version": __import__("aegistrade.agentic",fromlist=["CONFIG"]).CONFIG["version"],
                        "memory_manifest":memory_manifest,
                        "knowledge_corpus":__import__("aegistrade.corpus",fromlist=["corpus_info"]).corpus_info(),
                        "max_possible_paid_calls": required_call_budget(s),
                        "summary":summary, "outputs":outputs,
                        "disclaimer":"Research-only route audit. Not portfolio backtesting, investment advice, or order execution. Actual costs depend on provider usage."})
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / f"{result['run_id']}.json").write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    return result
