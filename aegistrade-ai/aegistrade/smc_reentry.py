"""Bounded SMC stop/recovery state. Recovery is checked AFTER company screening."""
from copy import deepcopy
import hashlib
import math
from datetime import date


def register_stop(watches,position,when,index,*,enabled=False,window=10):
    if not enabled or position['strategy']!='SMC' or not position.get('smc_context'):return None
    used=int(position.get('smc_reentry_count',0));symbol=position['symbol']
    identity=hashlib.sha256(f"{symbol}|{when}|{index}|{position['entry_date']}|{position.get('entry_research_id','')}".encode()).hexdigest()[:24]
    watches[symbol]={'id':identity,'symbol':symbol,'stop_date':str(when)[:10],'stop_index':int(index),
        'stop_level':float(position['stop']),'expires_index':int(index)+int(window),
        'original_entry_date':str(position['entry_date'])[:10],'smc_context':deepcopy(position['smc_context']),
        'attempts_used':used,'status':'WATCHING' if used<1 else 'EXHAUSTED'}
    return identity


def expire(watches,index):
    for watch in watches.values():
        if index>watch['expires_index']:watch['status']='EXPIRED'


def priority_symbols(watches):
    return [w['symbol'] for w in sorted(watches.values(),key=lambda w:(w['stop_index'],w['symbol'])) if w['status']=='WATCHING']


def context(watch):
    return deepcopy({k:v for k,v in watch.items() if k!='status'})


def recovery(row,watch,index):
    """Return (eligible, stage). Never treat an exhausted/cancelled watch as a new entry."""
    if watch['status']!='WATCHING':return False,'SMC_REENTRY_UNAVAILABLE'
    if index<=watch['stop_index']:return False,'SMC_REENTRY_SAME_SESSION'
    if index>watch['expires_index']:return False,'SMC_REENTRY_UNAVAILABLE'
    prior=float(getattr(row,'PriorHigh',float('nan')))
    good=bool(row.Ready) and row.Regime not in {'HIGH_VOL','WARMUP'} and math.isfinite(prior)
    good=good and row.Close>row.Open and row.Close>prior and row.Close>watch['stop_level'] and row.Close>watch['smc_context']['zone_high']
    return bool(good),'SMC_RECOVERY_CONFIRMED' if good else 'WAITING_SMC_RECOVERY'


def validate_stop_proof(watch,state,policy):
    if watch['status']!='WATCHING' or watch['attempts_used']!=0:raise ValueError('SMC re-entry watch is unavailable or exhausted')
    sales=[s for s in state['ledger'] if s.get('stop_watch_id')==watch['id'] and s.get('symbol')==watch['symbol'] and s.get('event') in {'SELL_STOP','SELL_TRAILING_STOP'}]
    if len(sales)!=1:raise ValueError('SMC re-entry lacks a unique recorded stop sale')
    sale=sales[0]
    if sale['strategy']!='SMC' or sale['date']!=watch['stop_date'] or sale['entry_date']!=watch['original_entry_date'] or sale['stop_price']!=watch['stop_level'] or sale.get('smc_context')!=watch['smc_context'] or sale.get('smc_reentry_count',0)!=watch['attempts_used']:
        raise ValueError('SMC re-entry watch differs from its stop sale')
    stop_index=state['dates'].index(watch['stop_date'])
    if stop_index!=watch['stop_index'] or watch['expires_index']!=stop_index+policy.smc_reentry_window_sessions:raise ValueError('SMC re-entry window changed')
    c=watch['smc_context']
    if not (date.fromisoformat(c['sweep_date'])<date.fromisoformat(c['structure_date'])<date.fromisoformat(watch['original_entry_date'])<=date.fromisoformat(watch['stop_date'])):raise ValueError('SMC stop context dates are inconsistent')
