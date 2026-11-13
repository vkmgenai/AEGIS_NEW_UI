"""Daily-bar execution rules; no future-bar decisions or model arithmetic."""
from .fees import BUY_FEE_BPS, SELL_FEE_BPS, FEE_MODEL
from datetime import date
from dataclasses import replace


def policy_for_strategy(policy,strategy):
    if strategy!='BREAKOUT':return policy
    return replace(policy,risk_per_trade=policy.breakout_risk_per_trade,
        stop_loss_mode=policy.breakout_stop_loss_mode,stop_loss_percent=policy.breakout_stop_loss_percent,
        atr_stop_multiple=policy.breakout_atr_stop_multiple,
        trailing_atr_multiple=policy.breakout_trailing_atr_multiple,
        trailing_activation_r=policy.breakout_trailing_activation_r)


def position_policy_record(policy):
    return {'risk_percent':policy.risk_per_trade*100,'stop_loss_mode':policy.stop_loss_mode,
        'stop_loss_percent':policy.stop_loss_percent,'initial_stop_atr_multiple':policy.atr_stop_multiple,
        'trailing_atr_multiple':policy.trailing_atr_multiple,'trailing_activation_r':policy.trailing_activation_r}


def strategy_policy_records(policy):
    from .strategies import STRATEGIES
    return {s:position_policy_record(policy_for_strategy(policy,s)) for s in STRATEGIES}


def defer_entry_review(day,next_day):
    """Friday candidates wait even for a special Saturday trading session."""
    a=date.fromisoformat(str(day)[:10]);b=date.fromisoformat(str(next_day)[:10])
    return a.weekday()==4 or (b-a).days>1


def take_profit_reference(position,policy):
    if policy.take_profit_percent<=0:return None
    cost=position['quantity']*position['entry_price']+position['entry_fee']
    return cost*(1+policy.take_profit_percent/100)/(position['quantity']*(1-SELL_FEE_BPS/10000)*(1-policy.slippage_bps/10000))


def protective_exit(position,bar,policy):
    """Opening events precede intraday events; ambiguous bars use stop first."""
    from .trailing_stop import stop_exit_reason
    opening=float(bar.Open);stop=position['stop'];target=take_profit_reference(position,policy)
    if opening<=stop:return stop_exit_reason(position),opening
    if target is not None and opening>=target:return 'SELL_TAKE_PROFIT',opening
    if float(bar.Low)<=stop:return stop_exit_reason(position),stop
    if target is not None and float(bar.High)>=target:return 'SELL_TAKE_PROFIT',target
    return None


def initial_stop_price(close,atr,policy):
    """Freeze a price from the completed signal, never a future fill or bar."""
    import math
    close=float(close);atr=float(atr)
    if not math.isfinite(close) or close<=0:raise ValueError('Initial stop needs a positive finite signal close')
    if policy.stop_loss_mode=='PERCENT':
        percent=float(policy.stop_loss_percent)
        if not math.isfinite(percent) or not .1<=percent<=50:raise ValueError('Stop loss percentage must be 0.1–50')
        return close*(1-percent/100)
    if policy.stop_loss_mode!='ATR':raise ValueError('Initial stop method must be ATR or PERCENT')
    multiple=float(policy.atr_stop_multiple)
    if not math.isfinite(atr) or atr<=0 or not math.isfinite(multiple) or not .5<=multiple<=10:
        raise ValueError('Initial ATR stop requires positive ATR and a multiple of 0.5–10')
    return close-multiple*atr


def initial_stop_settings(policy):
    return {'mode':policy.stop_loss_mode,'atr_multiple':policy.atr_stop_multiple,
        'percent':policy.stop_loss_percent,'basis':'Completed signal close; fixed before later-open fill. Percentage is before fees, slippage and gaps.',
        'trailing_relationship':'Trailing stop can tighten the initial stop from subsequent eligible sessions; it never lowers it.'}


def smc_policy_record(policy):
    return {**position_policy_record(policy),'reentry_enabled':policy.smc_reentry_enabled,
            'reentry_window_sessions':policy.smc_reentry_window_sessions,'max_recovery_fills_per_setup':1}
