"""Causal, next-session daily-bar backtester; one cash-only portfolio."""
from __future__ import annotations
from .fees import BUY_FEE_BPS, SELL_FEE_BPS, FEE_MODEL
from dataclasses import dataclass, asdict, field
import math
import numpy as np
import pandas as pd
from .strategies import entry_signal, exit_signal, chosen_strategy
from .execution_policy import protective_exit,defer_entry_review,take_profit_reference,initial_stop_price,policy_for_strategy,position_policy_record
from .trailing_stop import advance_trailing_stop,stop_exit_reason
from .breakout_reentry import register_breakout_stop,reentry_candidates
from . import smc_reentry


@dataclass(frozen=True)
class TradePolicy:
    initial_cash: float = 100_000
    risk_per_trade: float = 0.01
    max_position_fraction: float = 0.20
    max_positions: int = 4
    fee_bps: float = field(default=BUY_FEE_BPS, init=False)
    stop_loss_enabled: bool = True
    slippage_bps: float = 10.0
    atr_stop_multiple: float = 2.0
    stop_loss_mode: str = "ATR"
    stop_loss_percent: float = 5.0
    max_daily_loss_pct: float = 3.0
    take_profit_percent: float = 0.0
    review_after_gap: bool = False
    trailing_stop_enabled: bool = False
    trailing_atr_multiple: float = 2.0
    trailing_activation_r: float = 0.0
    breakout_risk_per_trade: float = 0.005
    breakout_stop_loss_mode: str = 'ATR'
    breakout_stop_loss_percent: float = 5.0
    breakout_atr_stop_multiple: float = 2.5
    breakout_trailing_atr_multiple: float = 2.5
    breakout_trailing_activation_r: float = 1.0
    breakout_reentry_enabled:bool=True
    smc_reentry_enabled:bool=False
    smc_reentry_window_sessions:int=10


def allowable_shares(entry: float, stop: float, cash: float, equity: float, p: TradePolicy) -> int:
    if not all(np.isfinite([entry, stop, cash, equity])) or not (entry > 0 and cash > 0 and equity > 0):
        return 0
    if p.stop_loss_enabled and not (0 < stop < entry):
        return 0
    risk_cap = math.floor(equity * p.risk_per_trade / (entry - stop)) if p.stop_loss_enabled else math.inf
    exposure_cap = math.floor(equity * p.max_position_fraction / entry)
    available_cap = math.floor(cash / (entry * (1 + p.fee_bps / 10_000)))
    return max(0, int(min(risk_cap, exposure_cap, available_cap)))


def backtest(frame: pd.DataFrame, mode: str = "ROUTER", p: TradePolicy | None = None, *, automatic_selection:bool=False, screening_limit:int=3) -> tuple[pd.DataFrame,pd.DataFrame,dict]:
    """Signal from day T close enters at T+1 open. Stops use daily OHLC and conservative gap handling.

    This is a research backtest, not executable broker infrastructure. No same-bar close lookahead.
    Entry signal has no certainty of execution in actual markets; corporate actions/data licensing need review.
    """
    p = p or TradePolicy()
    cash = float(p.initial_cash)
    positions: dict[str, dict] = {}
    queued: list[dict] = []
    rows, trade_events = [], []
    selection_audit=[]
    stop_updates=[]
    reentry_watches={}
    smc_watches={}
    last_marks = {}
    previous_equity = cash
    byday = frame.sort_values(["Date","Symbol"]).groupby("Date", sort=True)
    trading_dates=list(byday.groups)
    for day_index,(date, daily) in enumerate(byday):
        snap = {str(r.Symbol):r for r in daily.itertuples(index=False)}
        pending=[]
        def marked(at_open=False):
            return cash + sum(q['quantity']*(float(getattr(snap[s], 'Open' if at_open else 'Close'))
                            if s in snap else last_marks[s]) for s,q in positions.items())
        # Orders generated from PREVIOUS session's completed close.
        for order in sorted(queued, key=lambda a: 0 if a["side"] == "SELL" else 1):
            sym = order["symbol"]
            if sym not in snap:
                pending.append(order)
                continue
            bar = snap[sym]
            if order["side"]=="BUY" and p.review_after_gap and defer_entry_review(order["signal_date"],date):
                continue  # Delayed fill needs a fresh completed-close signal.
            if order["side"] == "SELL" and sym in positions:
                pos = positions.pop(sym)
                sell = float(bar.Open) * (1 - p.slippage_bps/10_000)
                notional = sell * pos["quantity"]
                fee = notional * SELL_FEE_BPS/10_000
                cash += notional - fee
                reason=stop_exit_reason(pos) if float(bar.Open)<=pos['stop'] else ('SELL_TAKE_PROFIT' if take_profit_reference(pos,p) is not None and float(bar.Open)>=take_profit_reference(pos,p) else 'SELL_SIGNAL')
                if reason in {'SELL_STOP','SELL_TRAILING_STOP'}:
                    register_breakout_stop(reentry_watches,{**pos,'symbol':sym},str(date.date()),day_index,p.breakout_reentry_enabled)
                    smc_reentry.register_stop(smc_watches,{**pos,'symbol':sym},str(date.date()),day_index,enabled=p.smc_reentry_enabled,window=p.smc_reentry_window_sessions)
                trade_events.append(dict(Date=date,Symbol=sym,Event=reason,Quantity=pos["quantity"],Price=sell,Fee=fee,Strategy=pos["strategy"],PnL=(sell-pos["entry_price"])*pos["quantity"]-fee-pos["entry_fee"]))
            elif order["side"] == "BUY" and sym not in positions and len(positions) < p.max_positions:
                buy = float(bar.Open) * (1 + p.slippage_bps/10_000)
                # Stop was fixed when signal was generated; reject if a gap makes it invalid.
                stop = float(order["stop"])
                equity_at_open = marked(at_open=True)
                if equity_at_open <= previous_equity*(1-p.max_daily_loss_pct/100):
                    continue
                active_policy=policy_for_strategy(p,order['strategy'])
                quantity = allowable_shares(buy,stop,cash,equity_at_open,active_policy)
                if order.get('smc_reentry'):
                    watch=smc_watches.get(sym)
                    if not watch or watch['status']!='WATCHING' or smc_reentry.context(watch)!=order['smc_reentry']:continue
                if quantity > 0:
                    value = buy*quantity
                    fee = value*p.fee_bps/10_000
                    cash -= value + fee
                    positions[sym] = dict(quantity=quantity,entry_price=buy,stop=stop,initial_stop=stop,
                        entry_signal_atr=order['signal_atr'],highest_close=None,entry_fee=fee,strategy=order["strategy"],entry_date=date)
                    positions[sym]['smc_context']=order.get('smc_context')
                    positions[sym]['smc_reentry_count']=int(bool(order.get('smc_reentry')))
                    if order.get('smc_reentry'):smc_watches.pop(sym,None)
                    positions[sym]['execution_policy']=position_policy_record(active_policy)
                    positions[sym]['symbol']=sym
                    positions[sym]['breakout_reentry_count']=int(order.get('breakout_reentry',False))
                    if order.get('breakout_reentry'):reentry_watches.pop(sym,None)
                    trade_events.append(dict(Date=date,Symbol=sym,Event="BUY",Quantity=quantity,Price=buy,Fee=fee,Strategy=order["strategy"],PnL=np.nan,
                        RiskPercent=active_policy.risk_per_trade*100,InitialStop=stop,TrailingActivationR=active_policy.trailing_activation_r,EntrySetup="SMC_RECOVERY" if order.get("smc_reentry") else "BREAKOUT_BOUNCE" if order.get("breakout_reentry") else "REGULAR"))
        queued = pending
        # Apply protective stop if intraday low penetrates; opening gap below stop fills at open, not stop.
        for sym,pos in list(positions.items()):
            if sym not in snap:
                continue
            bar = snap[sym]
            trigger=protective_exit(pos,bar,p)
            if trigger:
                reason,ref=trigger
                if reason in {'SELL_STOP','SELL_TRAILING_STOP'}:
                    register_breakout_stop(reentry_watches,{**pos,'symbol':sym},str(date.date()),day_index,p.breakout_reentry_enabled)
                    smc_reentry.register_stop(smc_watches,{**pos,'symbol':sym},str(date.date()),day_index,enabled=p.smc_reentry_enabled,window=p.smc_reentry_window_sessions)
                sell = ref*(1-p.slippage_bps/10_000)
                value = sell*pos["quantity"]
                fee = value*SELL_FEE_BPS/10_000
                cash += value-fee
                trade_events.append(dict(Date=date,Symbol=sym,Event=reason,Quantity=pos["quantity"],Price=sell,Fee=fee,Strategy=pos["strategy"],PnL=(sell-pos["entry_price"])*pos["quantity"]-fee-pos["entry_fee"]))
                del positions[sym]
        # Today's low was tested against yesterday's stop. Ratchets apply only afterwards.
        if p.trailing_stop_enabled:
            for sym,pos in positions.items():
                if sym not in snap:continue
                active_policy=policy_for_strategy(p,pos['strategy'])
                update=advance_trailing_stop(pos,float(snap[sym].Close),str(date.date()),active_policy.trailing_atr_multiple,activation_r=active_policy.trailing_activation_r)
                if update:stop_updates.append({'symbol':sym,**update})
        marked_equity = marked()
        daily_loss_block = marked_equity <= previous_equity*(1-p.max_daily_loss_pct/100)
        # At T close rank only T-available candidates. Fills and actual sizing still use a later open.
        daily=reentry_candidates(daily,reentry_watches,day_index) if p.breakout_reentry_enabled else daily
        entry_snap={str(r.Symbol):r for r in daily.itertuples(index=False)}
        smc_reentry.expire(smc_watches,day_index)
        eligible_symbols=None
        if automatic_selection:
            from .selection import rank_candidates
            if mode=='SMC':
                from .smc import screening_candidates
                audit=screening_candidates(daily,set(positions),day_index,screening_limit,priority_symbols=smc_reentry.priority_symbols(smc_watches))
                if len(positions)>=p.max_positions:
                    for item in audit:item['selected']=False;item['reasons'].append('POSITION_LIMIT')
            else:
                audit=rank_candidates(daily,mode,equity=marked_equity,cash=cash,trade_policy=p,
                                      held_symbols=positions,available_slots=max(0,p.max_positions-len(positions)))
            if daily_loss_block:
                for row in audit:
                    row['selected']=False
                    if 'DAILY_LOSS_LIMIT' not in row['reasons']:row['reasons'].append('DAILY_LOSS_LIMIT')
            selection_audit.extend(audit)
            eligible_symbols=[r['symbol'] for r in audit if r['selected']]
        for sym,bar in snap.items():
            if sym in positions and exit_signal(bar,positions[sym]['strategy']):
                queued.append(dict(side='SELL',symbol=sym))
        ordered=eligible_symbols if eligible_symbols is not None else list(snap)
        if p.review_after_gap and day_index+1<len(trading_dates) and defer_entry_review(date,trading_dates[day_index+1]):
            ordered=[]  # Fresh next-session close must qualify before any later-open entry.
        for sym in ordered:
            bar=entry_snap[sym]
            if sym in positions or daily_loss_block:continue
            if sym in reentry_watches and bar.Regime!='BREAKOUT_BOUNCE':continue
            strategy=chosen_strategy(bar,mode)
            watch=smc_watches.get(sym) if strategy=='SMC' and p.smc_reentry_enabled else None
            watched=watch is not None and watch['status']!='EXPIRED'
            signal=smc_reentry.recovery(bar,watch,day_index)[0] if watched else entry_signal(bar,strategy)
            if signal and strategy!='NONE' and np.isfinite(bar.ATR14) and bar.ATR14>0:
                active_policy=policy_for_strategy(p,strategy)
                stop=initial_stop_price(bar.Close,bar.ATR14,active_policy)
                if stop>0 or not active_policy.stop_loss_enabled:queued.append(dict(side='BUY',symbol=sym,strategy=strategy,stop=stop,signal_atr=float(bar.ATR14),signal_date=str(date.date()),breakout_reentry=bar.Regime=='BREAKOUT_BOUNCE',smc_context=watch['smc_context'] if watched else getattr(bar,'SMCContext',None),smc_reentry=smc_reentry.context(watch) if watched else None))
        last_marks.update({s:float(bar.Close) for s,bar in snap.items()})
        previous_equity = marked_equity
        rows.append(dict(Date=date,Equity=marked_equity,Cash=cash,Positions=len(positions),QueuedOrders=len(queued),DailyLossBlocked=daily_loss_block))
    equity = pd.DataFrame(rows)
    equity.attrs['selection_audit']=selection_audit
    equity.attrs['stop_updates']=stop_updates
    equity.attrs['breakout_reentry_watches']=reentry_watches
    equity.attrs['smc_reentry_watches']=smc_watches
    events = pd.DataFrame(trade_events,columns=["Date","Symbol","Event","Quantity","Price","Fee","Strategy","PnL","RiskPercent","InitialStop","TrailingActivationR","EntrySetup"])
    return equity,events,performance(equity, events, p.initial_cash)


def performance(equity: pd.DataFrame, events: pd.DataFrame, starting_cash:float) -> dict:
    daily = equity.Equity.pct_change().dropna()
    years = max(len(equity)/252, 1/252)
    final = float(equity.Equity.iloc[-1])
    drawdown = equity.Equity/equity.Equity.cummax()-1
    realized = events.loc[events.Event.str.startswith("SELL"),"PnL"].dropna() if len(events) else pd.Series(dtype=float)
    return dict(total_return_pct=round((final/starting_cash-1)*100,2),cagr_pct=round(((final/starting_cash)**(1/years)-1)*100,2),
                sharpe=round(float(np.sqrt(252)*daily.mean()/daily.std()),3) if len(daily)>2 and daily.std()>0 else np.nan,
                max_drawdown_pct=round(float(drawdown.min()*100),2),completed_trades=len(realized),
                win_rate_pct=round(float(100*(realized>0).mean()),2) if len(realized) else np.nan,
                ending_equity=round(final,2))


def buy_and_hold(frame: pd.DataFrame, p: TradePolicy):
    """Equal-weight cash buy-and-hold benchmark; no signal, stops or strategy risk cap.

    Buy at first session open, pay identical fees/slippage, hold to final close.
    This is a passive comparator, not a risk-matched active strategy.
    """
    f=frame.sort_values(['Date','Symbol']); first=f.Date.min()
    initial=f[f.Date==first]; allocation=p.initial_cash/len(initial)
    holdings={}; cash=float(p.initial_cash); rows=[]; marks={}
    for r in initial.itertuples():
        price=float(r.Open)*(1+p.slippage_bps/10000)
        qty=math.floor(allocation/(price*(1+p.fee_bps/10000)))
        holdings[r.Symbol]=qty
        cash-=qty*price*(1+p.fee_bps/10000)
    for when,bars in f.groupby('Date',sort=True):
        marks.update({r.Symbol:float(r.Close) for r in bars.itertuples()})
        rows.append({'Date':when,'Equity':cash+sum(q*marks[s] for s,q in holdings.items()),
                     'Cash':cash,'Positions':sum(q>0 for q in holdings.values()),'QueuedOrders':0})
    curve=pd.DataFrame(rows)
    events=pd.DataFrame(columns=['Event','PnL'])
    return curve,performance(curve,events,p.initial_cash)
