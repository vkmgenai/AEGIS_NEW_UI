"""Validated, repeatable portfolio simulations; never talks to a broker or LLM."""
from __future__ import annotations
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from .execution_policy import initial_stop_settings,strategy_policy_records
import json
import math
import uuid

import pandas as pd
from pydantic import BaseModel, Field, model_validator

from .engine import TradePolicy, backtest, buy_and_hold

MODES = ("ROUTER", "EMA_TREND", "EMA_PULLBACK", "RSI_REVERSION", "BREAKOUT")


class SimulationSettings(BaseModel):
    initial_capital: float = Field(default=200_000, ge=1_000, le=100_000_000)
    start_date: date | None = None
    end_date: date | None = None
    risk_percent: float = Field(default=1.0, ge=0.25, le=3.0)
    mode: str = Field(default="ROUTER")
    fee_bps: float = Field(default=10.0, ge=0, le=100)
    automatic_stock_selection: bool = True
    slippage_bps: float = Field(default=10.0, ge=0, le=100)
    take_profit_percent: float = Field(default=8.0,ge=0,le=100,allow_inf_nan=False)
    review_after_gap: bool = True
    stop_loss_mode: Literal["ATR","PERCENT"] = "ATR"
    stop_loss_percent: float = Field(default=5.0,ge=0.1,le=50,allow_inf_nan=False)
    initial_stop_atr_multiple: float = Field(default=2.0,ge=0.5,le=10,allow_inf_nan=False)
    trailing_stop_enabled: bool = True
    trailing_atr_multiple: float = Field(default=2.0,ge=0.5,le=10,allow_inf_nan=False)
    breakout_risk_percent:float=Field(default=.5,ge=.1,le=3,allow_inf_nan=False)
    breakout_stop_loss_mode:Literal['ATR','PERCENT']='ATR'
    breakout_stop_loss_percent:float=Field(default=5.,ge=.1,le=50,allow_inf_nan=False)
    breakout_initial_stop_atr_multiple:float=Field(default=2.5,ge=.5,le=10,allow_inf_nan=False)
    breakout_trailing_atr_multiple:float=Field(default=2.5,ge=.5,le=10,allow_inf_nan=False)
    breakout_trailing_activation_r:float=Field(default=1.,ge=0,le=5,allow_inf_nan=False)
    breakout_reentry_enabled:bool=True

    @model_validator(mode="after")
    def validate_dates_and_mode(self):
        if self.mode not in (*MODES, "ALL"):
            raise ValueError(f"mode must be ALL or one of {MODES}")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date")
        return self


def policy_from_settings(settings):
    return TradePolicy(initial_cash=settings.initial_capital,risk_per_trade=settings.risk_percent/100,
        stop_loss_mode=settings.stop_loss_mode,stop_loss_percent=settings.stop_loss_percent,
        atr_stop_multiple=settings.initial_stop_atr_multiple,fee_bps=settings.fee_bps,slippage_bps=settings.slippage_bps,
        take_profit_percent=settings.take_profit_percent,review_after_gap=settings.review_after_gap,
        trailing_stop_enabled=settings.trailing_stop_enabled,trailing_atr_multiple=settings.trailing_atr_multiple,
        breakout_risk_per_trade=settings.breakout_risk_percent/100,breakout_stop_loss_mode=settings.breakout_stop_loss_mode,
        breakout_stop_loss_percent=settings.breakout_stop_loss_percent,breakout_atr_stop_multiple=settings.breakout_initial_stop_atr_multiple,
        breakout_trailing_atr_multiple=settings.breakout_trailing_atr_multiple,breakout_trailing_activation_r=settings.breakout_trailing_activation_r,
        breakout_reentry_enabled=settings.breakout_reentry_enabled)


def normalize(value):
    """Make results JSON-safe (NaN/inf are not valid JSON)."""
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (float, int)):
        return value if math.isfinite(float(value)) else None
    if value is None or isinstance(value, (str, bool)):
        return value
    return value.item() if hasattr(value, "item") else str(value)


def execute_simulation(market_frame: pd.DataFrame, settings: SimulationSettings, *, save_dir: Path | None = None, source="synthetic", provenance:dict|None=None) -> dict:
    """Run fixed strategies against the *same* history, capital and risk limits.

    Indicators are calculated before slicing, so the first selected session has
    historically available warm-up values. No historical results imply C2 LLM trades.
    """
    if source=='nsepython' and provenance and provenance.get('requested_start'):
        earliest=date.fromisoformat(provenance['requested_start'])
        latest=date.fromisoformat(provenance['requested_end'])
        if settings.start_date and settings.start_date<earliest:
            raise ValueError('Warm-up rows cannot be evaluated: the stock universe was selected for a later start date')
        if settings.end_date and settings.end_date>latest:
            raise ValueError('Evaluation end exceeds the downloaded window')
        if settings.start_date is None:settings=settings.model_copy(update={'start_date':earliest})
        if settings.end_date is None:settings=settings.model_copy(update={'end_date':latest})
    from .selection import prepare_selection_features
    f = prepare_selection_features(market_frame) if settings.automatic_stock_selection else market_frame.copy()
    if settings.start_date:
        f = f[f.Date.dt.date >= settings.start_date]
    if settings.end_date:
        f = f[f.Date.dt.date <= settings.end_date]
    days = f.Date.nunique()
    if days < 45:
        raise ValueError(f"Selected period has {days} sessions; choose at least 45 sessions")
    if f.Symbol.nunique() < 1:
        raise ValueError("Selected period contains no symbols")
    policy = policy_from_settings(settings)
    chosen_modes = MODES if settings.mode == "ALL" else (settings.mode,)
    metrics, curves, ledgers = [], {}, {}
    selection_audits={};stop_updates={};reentry_watches={}
    from dataclasses import asdict
    from .selection import SelectionPolicy
    for mode in chosen_modes:
        eq, events, result = backtest(f, mode=mode, p=policy,automatic_selection=settings.automatic_stock_selection)
        selection_audits[mode]=eq.attrs.get("selection_audit",[])
        stop_updates[mode]=eq.attrs.get('stop_updates',[])
        reentry_watches[mode]=list(eq.attrs.get('breakout_reentry_watches',{}).values())
        metrics.append(normalize({"mode": mode, "initial_capital": settings.initial_capital,
                                  "ending_cash": float(eq.Cash.iloc[-1]), **result}))
        curves[mode] = [{"date": r.Date.date().isoformat(), "equity": round(float(r.Equity), 2),
                         "cash": round(float(r.Cash), 2), "open_positions": int(r.Positions)}
                        for r in eq.itertuples()]
        ledgers[mode] = [{"date": r.Date.date().isoformat(), "symbol": str(r.Symbol),
                          "event": str(r.Event), "quantity": int(r.Quantity),
                          "price": round(float(r.Price), 4), "fee": round(float(r.Fee), 4),
                          "strategy": str(r.Strategy), "realized_pnl": normalize(float(r.PnL)),
                          'risk_percent_used':normalize(float(r.RiskPercent)),'initial_stop':normalize(float(r.InitialStop)),
                          'trailing_activation_r':normalize(float(r.TrailingActivationR)),'entry_setup':r.EntrySetup if str(r.Event)=='BUY' else None}
                         for r in events.itertuples()]
    benchmark_curve,benchmark_metrics=buy_and_hold(f,policy)
    result = normalize({
        "benchmark":{"name":"EQUAL_WEIGHT_BUY_AND_HOLD","metrics":benchmark_metrics,
                     "curve":[{"date":r.Date.date().isoformat(),"equity":round(r.Equity,2)} for r in benchmark_curve.itertuples()],
                     "assumptions":"Buy equal allocations at first selected session open, same fees/slippage, hold to final close. No stops or active-strategy exposure caps."},
        "run_id": uuid.uuid4().hex,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "data_source": source,
        "data_provenance":provenance or {"provider":source},
        "synthetic_warning": source == "synthetic",
        "sessions": int(days),
        "period": {"start": f.Date.min().date().isoformat(), "end": f.Date.max().date().isoformat()},
        "settings": settings.model_dump(mode="json"),
        "breakout_reentry_watches":reentry_watches,"stop_updates":stop_updates,"initial_stop_loss":initial_stop_settings(policy),'strategy_policies':strategy_policy_records(policy),
        "metrics": metrics,
        "curves": curves,
        "ledgers": ledgers,
        "stock_selection":{"enabled":settings.automatic_stock_selection,"version":SelectionPolicy().version,"policy":asdict(SelectionPolicy()),
                           "audits":selection_audits,"note":"Signals ranked at each completed close; actual next-open quantity is recalculated. No LLM-selected portfolio returns."},
        "disclaimer": "Deterministic historical simulation only. ROUTER is code-based, NOT OpenRouter C2.",
    })
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / f"{result['run_id']}.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    return result
