"""Versioned, point-in-time stock screening. All arithmetic stays in code."""
from dataclasses import dataclass,asdict
import math
import numpy as np
import pandas as pd
from .strategies import chosen_strategy,entry_signal
from .engine import TradePolicy,allowable_shares
from .execution_policy import initial_stop_price,policy_for_strategy

@dataclass(frozen=True)
class SelectionPolicy:
    min_history_sessions:int=60
    min_average_turnover_inr:float=10_000_000  # research setting: Rs 1 crore/day
    max_atr_fraction:float=.065
    max_relative_gap:float=.30
    version:str='selection-v2-pullback-breakout-risk'


def prepare_selection_features(frame):
    parts=[]
    for _,f in frame.groupby('Symbol',sort=False):
        f=f.sort_values('Date').copy()
        f['HistorySessions']=np.arange(1,len(f)+1)
        f['AverageTurnover20']=(f.Close*f.Volume).rolling(20,min_periods=20).mean()
        f['RelativeVolume20']=f.Volume/f.Volume.rolling(20,min_periods=20).mean()
        f['Momentum20']=f.Close.pct_change(20,fill_method=None)
        # Quarantine unexplained raw-price discontinuities; this is not a corporate-action adjustment.
        f['RecentDiscontinuity']=f.Close.pct_change(fill_method=None).abs().gt(.30).rolling(20,min_periods=1).max().astype(bool)
        parts.append(f)
    return pd.concat(parts,ignore_index=True).sort_values(['Date','Symbol']).reset_index(drop=True)


def rank_candidates(daily,mode='ROUTER',*,equity,cash,trade_policy=None,selection_policy=None,held_symbols=(),available_slots=None):
    p=trade_policy or TradePolicy();s=selection_policy or SelectionPolicy()
    held=set(held_symbols);slots=p.max_positions-len(held) if available_slots is None else available_slots
    rows=[]
    liquidity_rank=daily.AverageTurnover20.rank(pct=True).to_dict()
    for index,bar in daily.iterrows():
        strategy=chosen_strategy(bar,mode);reasons=[];quantity=0;score=0.
        if bar.Symbol in held:reasons.append('ALREADY_HELD')
        if not bar.Ready or bar.HistorySessions<s.min_history_sessions:reasons.append('INSUFFICIENT_HISTORY')
        if not np.isfinite(bar.AverageTurnover20) or bar.AverageTurnover20<s.min_average_turnover_inr:reasons.append('LOW_LIQUIDITY')
        if bar.Regime in {'HIGH_VOL','UNCERTAIN','WARMUP'}:reasons.append('REGIME_ABSTAIN')
        if not np.isfinite(bar.ATR14) or bar.ATR14<=0 or bar.ATR14/bar.Close>s.max_atr_fraction:reasons.append('VOLATILITY_LIMIT')
        if bool(bar.RecentDiscontinuity):reasons.append('UNREVIEWED_PRICE_DISCONTINUITY')
        if strategy=='NONE' or not entry_signal(bar,strategy):reasons.append('NO_ENTRY_SIGNAL')
        if not reasons:
            active_policy=policy_for_strategy(p,strategy)
            quantity=allowable_shares(float(bar.Close),initial_stop_price(bar.Close,bar.ATR14,active_policy),cash,equity,active_policy)
            if quantity<1:reasons.append('CAPITAL_OR_RISK_LIMIT')
            if slots<=0:reasons.append('POSITION_LIMIT')
            if strategy in {'EMA_TREND','EMA_PULLBACK'}:
                strength=.6*min(bar.ADX14/40,1)+.4*min(max(bar.Momentum20,0)/.10,1)
            elif strategy=='RSI_REVERSION':strength=min(max((42-bar.RSI14)/22,0),1)
            else:strength=.6*min(max(bar.Close/bar.Prior20High-1,0)/.03,1)+.4*min(bar.RelativeVolume20/2,1)
            score=100*(.7*strength+.2*liquidity_rank[index]+.1*(1-min(bar.ATR14/bar.Close/s.max_atr_fraction,1)))
        rows.append({'symbol':str(bar.Symbol),'date':bar.Date.date().isoformat(),'strategy':strategy,
                     'regime':str(bar.Regime),'eligible':not reasons,'score':round(float(score),5),
                     'average_turnover_20_inr':round(float(bar.AverageTurnover20),2) if np.isfinite(bar.AverageTurnover20) else None,
                     'atr_fraction':float(bar.ATR14/bar.Close) if np.isfinite(bar.ATR14) else None,
                     'estimated_quantity_at_signal_close':quantity,'reasons':reasons,'selected':False,'rank':None})
    eligible=sorted([r for r in rows if r['eligible']],key=lambda r:(-r['score'],r['symbol']))
    for i,row in enumerate(eligible,1):row.update(rank=i,selected=i<=slots)
    return eligible+sorted([r for r in rows if not r['eligible']],key=lambda r:r['symbol'])
