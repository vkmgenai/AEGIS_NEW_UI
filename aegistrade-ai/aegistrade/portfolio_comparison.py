"""Coordinated single-stock C0/C1/C2 historical comparison.

C0 is deterministic ROUTER, C1 is evidence-first SMC, and C2 is the
multi-specialist ROUTER. The distinct C1 strategy is recorded so returns are
never presented as a pure orchestration ablation.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
import json
import os
import uuid

import pandas as pd
from pydantic import BaseModel, Field, model_validator

from .c2_portfolio import C1PortfolioSettings, C2PortfolioSettings, create_run, launch, status as child_status
from .simulation_service import SimulationSettings, execute_simulation, normalize


class ComparisonSettings(BaseModel):
    symbol: str = Field(pattern=r'^[A-Z0-9][A-Z0-9_&-]{1,29}$')
    start_date: date
    end_date: date
    initial_capital: float = Field(default=200_000, ge=1_000, le=100_000_000)
    risk_percent: float = Field(default=1.0, ge=.25, le=3.0)
    stop_loss_enabled: bool = True
    stop_loss_percent: float = Field(default=5.0, ge=.1, le=50)
    take_profit_percent: float = Field(default=8.0, gt=0, le=100)
    slippage_bps: float = Field(default=10.0, ge=0, le=100)
    holding_review_sessions: int = Field(default=5, ge=1, le=60)
    max_model_calls_per_flow: int = Field(default=240, ge=8, le=2400)
    consent_to_paid_calls: bool = False
    approve_historical_rules: bool = False

    @model_validator(mode='after')
    def valid_period(self):
        if self.start_date > self.end_date:raise ValueError('Start date must be on or before end date')
        if not self.consent_to_paid_calls or not self.approve_historical_rules:
            raise ValueError('External-inference consent and historical-rule approval are required')
        return self


def root():return Path(os.getenv('AEGIS_DATA_DIR','data'))/'portfolio_comparisons'


def _path(run_id):
    if len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):raise ValueError('Invalid comparison ID')
    return root()/f'{run_id}.json'


def _save(value):
    path=_path(value['run_id']);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temp.write_text(json.dumps(normalize(value),allow_nan=False));temp.replace(path)
    finally:temp.unlink(missing_ok=True)


def load(run_id):return json.loads(_path(run_id).read_text())


def create(frame:pd.DataFrame,settings:ComparisonSettings,*,source='synthetic',provenance=None):
    symbol=settings.symbol.upper();one=frame[frame.Symbol.astype(str).str.upper()==symbol].copy()
    if one.empty:raise ValueError('Selected stock is absent from the active universe')
    common=dict(initial_capital=settings.initial_capital,start_date=settings.start_date,end_date=settings.end_date,
        risk_percent=settings.risk_percent,stop_loss_enabled=settings.stop_loss_enabled,stop_loss_mode='PERCENT',
        stop_loss_percent=settings.stop_loss_percent,take_profit_percent=settings.take_profit_percent,
        slippage_bps=settings.slippage_bps,trailing_stop_enabled=False,breakout_reentry_enabled=False,
        smc_reentry_enabled=False,review_after_gap=True)
    c0_settings=SimulationSettings(**common,mode='ROUTER',automatic_stock_selection=False)
    c1_settings=C1PortfolioSettings(**common,mode='SMC',automatic_stock_selection=True,target_symbol=symbol,
        consent_to_paid_calls=True,approve_historical_rules=True,max_model_calls=settings.max_model_calls_per_flow,
        holding_review_sessions=settings.holding_review_sessions,screening_candidates_per_session=1)
    c2_settings=C2PortfolioSettings(**common,mode='ROUTER',automatic_stock_selection=True,target_symbol=symbol,
        consent_to_paid_calls=True,approve_historical_rules=True,max_model_calls=settings.max_model_calls_per_flow,
        holding_review_sessions=settings.holding_review_sessions)
    provenance=provenance or {}
    c0=execute_simulation(one,c0_settings,source=source,provenance=provenance)
    c1=create_run(frame,c1_settings,source=source,provenance=provenance)
    c2=create_run(frame,c2_settings,source=source,provenance=provenance)
    run={'run_id':uuid.uuid4().hex,'created_utc':datetime.now(timezone.utc).isoformat(),'settings':settings.model_dump(mode='json'),
         'data_source':source,'data_provenance':provenance,'children':{'C1':c1,'C2':c2},'c0':c0,
         'comparison_design':{'C0':'Deterministic technical ROUTER; zero LLM calls','C1':'Single evidence-first agent with SMC strategy',
             'C2':'Supervisor with market, strategy and critic specialists using ROUTER signals',
             'interpretation':'C0 and C2 share ROUTER signals. C1 uses SMC, so three-way P&L is a system comparison, not a pure agent-architecture ablation.'}}
    _save(run)
    launch(c1,frame);launch(c2,frame)
    return result(run)


def _flow_view(name,value):
    if name=='C0':
        return {'status':'COMPLETED','run_id':value['run_id'],'metrics':value['metrics'][0],
                'curve':value['curves']['ROUTER'],'ledger':value['ledgers']['ROUTER'],'model_usage':{'attempted_calls':0,'call_limit':0}}
    metric=(value.get('metrics') or [{}])[0]
    return {'status':value['status'],'run_id':value['run_id'],'metrics':metric,'curve':value.get('curves',{}).get(name,[]),
            'ledger':value.get('ledgers',{}).get(name,[]),'model_usage':value.get('model_usage',{}),
            'progress':value.get('progress',{}),'worker_active':value.get('worker_active',False),'last_error':value.get('last_error')}


def result(saved):
    flows={'C0':_flow_view('C0',saved['c0'])}
    for name in ('C1','C2'):
        flows[name]=_flow_view(name,child_status(saved['children'][name]))
    states=[flows[x]['status'] for x in ('C1','C2')]
    overall=('COMPLETED' if all(x.startswith('COMPLETED') for x in states) else
             'PAUSED' if any(x.startswith('PAUSED') for x in states) else
             'RUNNING' if any(flows[x].get('worker_active') for x in ('C1','C2')) else 'INTERRUPTED')
    return normalize({k:saved[k] for k in ('run_id','created_utc','settings','data_source','data_provenance','comparison_design')}|
                     {'status':overall,'flows':flows})


def status(run_id):return result(load(run_id))


def recent(limit=15):
    rows=[]
    for path in sorted(root().glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:limit] if root().exists() else []:
        try:
            obj=json.loads(path.read_text());rows.append({k:obj[k] for k in ('run_id','created_utc','settings','children')})
        except (OSError,ValueError,KeyError):continue
    return {'runs':rows}
