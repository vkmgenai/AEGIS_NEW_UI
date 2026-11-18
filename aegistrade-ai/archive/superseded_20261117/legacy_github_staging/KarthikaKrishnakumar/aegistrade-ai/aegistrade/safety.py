"""Typed order payload, code-enforced risk, audit ledger and isolated SIMULATED broker.

No real brokerage access. Notebook approvals are educational and do not authenticate users.
"""
from __future__ import annotations
from .fees import BUY_FEE_BPS, SELL_FEE_BPS, FEE_MODEL
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import sqlite3
import uuid
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class OrderProposal(BaseModel):
    model_config = ConfigDict(extra="forbid",allow_inf_nan=False)
    request_id: str = Field(min_length=3, max_length=100)
    symbol: str = Field(pattern=r"^[A-Z0-9][A-Z0-9_&-]{1,29}$")
    side: Literal["BUY", "SELL"]
    quantity: int = Field(gt=0, le=100000)
    order_type: Literal["MARKET"] = "MARKET"  # deliberate MVP simplification
    reference_price: float = Field(gt=0)
    stop_loss_price: float = Field(gt=0)
    strategy: Literal["EMA_TREND", "EMA_PULLBACK", "RSI_REVERSION", "BREAKOUT", "SMC"]
    account: Literal["DEMO_ONLY"] = "DEMO_ONLY"
    signal_date: str
    expires_at_utc: str

    @field_validator("signal_date")
    @classmethod
    def valid_signal_day(cls, v:str):
        from datetime import date
        if date.fromisoformat(v).isoformat()!=v:
            raise ValueError("signal_date must be YYYY-MM-DD")
        return v

    @field_validator("expires_at_utc")
    @classmethod
    def valid_utc_expiry(cls, v:str):
        parse_utc(v)
        return v


class RiskInputs(BaseModel):
    model_config = ConfigDict(extra="forbid",allow_inf_nan=False)
    equity: float = Field(gt=0)
    available_cash: float = Field(ge=0)
    current_positions: int = Field(ge=0)
    portfolio_day_loss_pct: float = 0.0


class RiskParameters(BaseModel):
    model_config = ConfigDict(extra="forbid",allow_inf_nan=False)
    max_trade_risk_fraction: float = Field(default=0.01, gt=0, le=0.05)
    breakout_risk_fraction: float = Field(default=0.005, gt=0, le=0.03)
    breakout_atr_stop_multiple: float = Field(default=2.5, ge=0.5, le=10)
    max_position_fraction: float = Field(default=0.20, gt=0, le=0.50)
    max_positions: int = Field(default=4, ge=1)
    max_daily_loss_pct: float = Field(default=3.0, gt=0)
    fee_bps: Literal[BUY_FEE_BPS] = BUY_FEE_BPS
    max_quote_age_seconds: int = Field(default=90, ge=1)
    max_price_deviation_fraction: float = Field(default=0.02, gt=0)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc(iso: str) -> datetime:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include a UTC offset")
    return dt.astimezone(timezone.utc)


def payload_hash(order: OrderProposal) -> str:
    return hashlib.sha256(json.dumps(order.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_risk(order: OrderProposal, inputs: RiskInputs, p: RiskParameters) -> dict:
    problems = []
    if order.side != "BUY":
        problems.append("This demo gate supports BUY only; selling requires an independently specified exit/position contract")
    if order.stop_loss_price >= order.reference_price:
        problems.append("Stop must be strictly below BUY reference price")
    if inputs.current_positions >= p.max_positions:
        problems.append("Maximum concurrent positions reached")
    if inputs.portfolio_day_loss_pct >= p.max_daily_loss_pct:
        problems.append("Daily portfolio loss limit reached")
    value = order.quantity * order.reference_price
    planned_risk = order.quantity * max(0,order.reference_price - order.stop_loss_price)
    max_risk = inputs.equity*(p.breakout_risk_fraction if order.strategy=="BREAKOUT" else p.max_trade_risk_fraction)
    if planned_risk > max_risk + 1e-8:
        problems.append("Exceeds maximum planned risk")
    if value > inputs.equity*p.max_position_fraction + 1e-8:
        problems.append("Exceeds maximum position value")
    if value*(1+p.fee_bps/10_000) > inputs.available_cash + 1e-8:
        problems.append("Insufficient cash incl. fees")
    return {"ok": not problems, "reasons": problems, "planned_risk": round(planned_risk,2),
            "order_value": round(value,2), "max_risk": round(max_risk,2)}


def make_demo_order(symbol: str, entry: float, atr: float, strategy: str, signal_date: str,
                    inputs: RiskInputs, p: RiskParameters, now: datetime | None = None) -> OrderProposal:
    now = now or utc_now()
    if not all(math.isfinite(x) for x in (entry,atr)) or entry<=0 or atr<=0:
        raise ValueError("Entry and ATR must be finite and positive")
    entry=round(entry,4)
    stop = round(max(0.01, entry-(p.breakout_atr_stop_multiple if strategy=="BREAKOUT" else 2)*atr),4)
    risk_per_share = entry-stop
    if risk_per_share <= 0:
        raise ValueError("Invalid stop/risk per share")
    qty = max(0,min(math.floor(inputs.equity*(p.breakout_risk_fraction if strategy=="BREAKOUT" else p.max_trade_risk_fraction)/risk_per_share),
                    math.floor(inputs.equity*p.max_position_fraction/entry),
                    math.floor(inputs.available_cash/(entry*(1+p.fee_bps/10_000)))))
    if qty < 1:
        raise ValueError("No feasible position under the risk policy")
    return OrderProposal(request_id=f"DEMO-{uuid.uuid4().hex[:12].upper()}", symbol=symbol,
             side="BUY", quantity=qty, reference_price=round(entry,4), stop_loss_price=round(stop,4),
             strategy=strategy,signal_date=str(signal_date),expires_at_utc=(now+timedelta(minutes=10)).isoformat())


class AuditBroker:
    """Independent simulator DB with approval and order records. No outside-world broker calls."""
    def __init__(self, path="aegistrade_demo.sqlite"):
        self.path=str(path)
        self.conn=sqlite3.connect(self.path,check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("CREATE TABLE IF NOT EXISTS approvals(token TEXT PRIMARY KEY, hash TEXT NOT NULL, reviewer TEXT NOT NULL, created TEXT NOT NULL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS orders(request_id TEXT PRIMARY KEY, payload_hash TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT, event TEXT, details TEXT, created TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS controls(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.conn.commit()

    def kill_switch_enabled(self):
        row=self.conn.execute("SELECT value FROM controls WHERE key='kill_switch'").fetchone()
        return bool(row and row[0]=='true')

    def set_kill_switch(self,enabled:bool,reason:str):
        if not reason.strip():raise ValueError('A human control reason is required')
        self.conn.execute("INSERT OR REPLACE INTO controls(key,value) VALUES ('kill_switch',?)",('true' if enabled else 'false',))
        # Previously reviewed proposals must be reviewed again after an emergency stop.
        if enabled:self.conn.execute('DELETE FROM approvals')
        self.conn.commit()
        self._log('CONTROL','KILL_SWITCH_ENABLED' if enabled else 'KILL_SWITCH_DISABLED',reason)
        return {'enabled':self.kill_switch_enabled(),'old_approvals_invalidated':bool(enabled)}

    def _log(self, request_id, event, details=""):
        self.conn.execute("INSERT INTO events(request_id,event,details,created) VALUES (?,?,?,?)",
                          (request_id,event,str(details),utc_now().isoformat()))
        self.conn.commit()

    def approve(self, order: OrderProposal, reviewer="demo-human-reviewer") -> str:
        """Call ONLY after LangGraph has returned a human approve action, not from an LLM."""
        token=uuid.uuid4().hex
        self.conn.execute("INSERT INTO approvals(token,hash,reviewer,created) VALUES (?,?,?,?)",
                          (token,payload_hash(order),reviewer,utc_now().isoformat()))
        self.conn.commit()
        self._log(order.request_id,"APPROVED",reviewer)
        return token

    def submit(self, order: OrderProposal, token: str, quote_price: float, quote_observed_utc: str,
               risk_inputs: RiskInputs, policy: RiskParameters, now: datetime | None = None,
               simulate_timeout_after_commit: bool = False) -> dict:
        now=now or utc_now()
        existing=self.conn.execute("SELECT payload_hash,status FROM orders WHERE request_id=?",(order.request_id,)).fetchone()
        if existing:
            if existing[0] != payload_hash(order):
                self._log(order.request_id,"REJECT_IDEMPOTENCY_CONFLICT")
                return {"status":"REJECTED", "reason":"Same request_id used for a different payload"}
            return {"status":existing[1],"request_id":order.request_id,"idempotent_replay":True}
        if self.kill_switch_enabled():
            self._log(order.request_id,'REJECT_KILL_SWITCH')
            return {'status':'REJECTED','reason':'Human kill switch is active'}
        a=self.conn.execute("SELECT hash FROM approvals WHERE token=?",(token,)).fetchone()
        if not a or a[0] != payload_hash(order):
            self._log(order.request_id,"REJECT_APPROVAL_MISMATCH")
            return {"status":"REJECTED","reason":"Missing or mismatched exact-payload approval"}
        rv=validate_risk(order,risk_inputs,policy)
        if not rv["ok"]:
            self._log(order.request_id,"REJECT_RISK",rv["reasons"])
            return {"status":"REJECTED","reason":"; ".join(rv["reasons"])}
        try:
            quote_at=parse_utc(quote_observed_utc)
            expiry=parse_utc(order.expires_at_utc)
        except ValueError as e:
            self._log(order.request_id,"REJECT_TIME",str(e))
            return {"status":"REJECTED","reason":str(e)}
        age=(now-quote_at).total_seconds()
        if age < 0 or age>policy.max_quote_age_seconds or now>expiry:
            self._log(order.request_id,"REJECT_STALE",f"age={age:.2f} seconds")
            return {"status":"REJECTED","reason":"Quote too old/future or approval payload expired"}
        if not math.isfinite(quote_price) or quote_price<=0 or abs(quote_price/order.reference_price-1)>policy.max_price_deviation_fraction:
            self._log(order.request_id,"REJECT_PRICE_MOVE")
            return {"status":"REJECTED","reason":"Price deviation exceeds policy"}
        self.conn.execute("INSERT INTO orders(request_id,payload_hash,payload,status,created) VALUES (?,?,?,?,?)",
                          (order.request_id,payload_hash(order),order.model_dump_json(),"ACCEPTED_SIMULATED",now.isoformat()))
        self.conn.commit()
        self._log(order.request_id,"ACCEPTED_SIMULATED")
        if simulate_timeout_after_commit:
            raise TimeoutError("Educational injected timeout AFTER a committed simulated order")
        return {"status":"ACCEPTED_SIMULATED","request_id":order.request_id,"idempotent_replay":False}

    def reconcile(self, request_id:str) -> dict:
        r=self.conn.execute("SELECT status,payload_hash FROM orders WHERE request_id=?",(request_id,)).fetchone()
        return {"request_id":request_id,"status":r[0],"payload_hash":r[1]} if r else {"request_id":request_id,"status":"NOT_FOUND"}

    def events(self) -> list:
        return self.conn.execute("SELECT request_id,event,details,created FROM events ORDER BY id").fetchall()
