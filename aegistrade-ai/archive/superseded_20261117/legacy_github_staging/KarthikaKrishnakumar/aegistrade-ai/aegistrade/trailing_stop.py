"""Causal long-only trailing stops; arithmetic only, no broker or model calls."""
from __future__ import annotations
import math


def advance_trailing_stop(position,close,when,multiple=2.0,*,activation_r=0.0):
    """Ratchet at a completed close; caller activates the result next session.

    ATR is frozen from the entry signal so widening volatility cannot lower the
    stop. Reprocessing the same checkpoint cannot advance it twice.
    """
    if position.get('trailing_last_close')==when:return None
    atr=float(position['entry_signal_atr']);close=float(close);multiple=float(multiple)
    old=float(position['stop'])
    if not all(math.isfinite(v) and v>0 for v in (atr,close,multiple,old)):
        raise ValueError('Trailing stop requires positive finite close, ATR, distance and stop')
    previous_peak=position.get('highest_close')
    peak=close if previous_peak is None else max(float(previous_peak),close)
    initial=float(position.get('initial_stop',old))
    activation_r=float(activation_r)
    if not math.isfinite(activation_r) or not 0<=activation_r<=5:raise ValueError('Trailing activation must be 0–5 R')
    if activation_r>0:
        entry=float(position['entry_price']);risk=entry-initial
        if not math.isfinite(entry) or risk<=0:raise ValueError('Trailing activation requires positive original entry risk')
        activated=bool(position.get('trailing_activated')) or peak>=entry+activation_r*risk
        position.update(highest_close=peak,trailing_last_close=when,trailing_activation_r=activation_r,
            trailing_activated=activated)
        if not activated:return None
    new=max(old,peak-multiple*atr)
    position.update(initial_stop=initial,highest_close=peak,stop=new,
        trailing_distance=multiple*atr,trailing_last_close=when)
    if new<=old:return None
    position['stop_effective_after']=when
    return {'date':when,'old_stop':old,'new_stop':new,'highest_close':peak,
            'entry_signal_atr':atr,'distance':multiple*atr,'effective_after_close':when}


def stop_exit_reason(position):
    initial=float(position.get('initial_stop',position['stop']))
    return 'SELL_TRAILING_STOP' if float(position['stop'])>initial+1e-9 else 'SELL_STOP'
