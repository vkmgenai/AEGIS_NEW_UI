"""Explicit daily-bar SMC approximation: sweep, structure break, order-block retest.

All windows use completed bars only. This does not infer institutional orders.
"""
import math
import pandas as pd

VERSION='smc-daily-sweep-bos-ob-v1'


def prepare_smc(frame):
    parts=[]
    for _,part in frame.groupby('Symbol',sort=False):
        f=part.sort_values('Date').copy();sweep=None;zone=None;records=[]
        if 'PriorHigh' not in f:f['PriorHigh']=f.High.shift(1)
        rows=list(f.itertuples())
        for i,b in enumerate(rows):
            record={'SMCSignal':False,'SMCContext':None,'SMCStage':'WAITING_SWEEP'};close=float(b.Close)
            if not b.Ready or b.Regime=='HIGH_VOL':
                sweep=zone=None;record['SMCStage']='HIGH_VOL' if b.Regime=='HIGH_VOL' else 'WARMUP';records.append(record);continue
            # A zone is available only after its completed structure-break candle.
            if zone:
                record['SMCStage']='WAITING_RETEST'
                if i-zone['bos_index']>10 or close<zone['zone_low']:
                    record['SMCStage']='SETUP_EXPIRED' if i-zone['bos_index']>10 else 'ZONE_INVALIDATED';zone=None
                elif i>zone['bos_index'] and b.Low<=zone['zone_high'] and b.High>=zone['zone_low'] and close>zone['zone_high'] and close>b.Open:
                    record={'SMCSignal':True,'SMCContext':{k:v for k,v in zone.items() if k!='bos_index'},'SMCStage':'ENTRY_CONFIRMED'}
                    zone=None;sweep=None
            if sweep and not zone and not record['SMCSignal']:
                record['SMCStage']='WAITING_STRUCTURE_BREAK'
                if i-sweep['index']>10 or close<sweep['low']:
                    record['SMCStage']='SWEEP_EXPIRED' if i-sweep['index']>10 else 'SWEEP_INVALIDATED';sweep=None
                elif i>sweep['index'] and close>sweep['structure_level'] and close>b.Open and close-b.Open>=.5*b.ATR14:
                    bearish=[r for r in rows[max(0,sweep['index']-3):i] if r.Close<r.Open]
                    if bearish:
                        ob=bearish[-1]
                        zone={'sweep_date':sweep['date'],'structure_date':str(b.Date.date()),
                            'sweep_level':sweep['level'],'structure_level':sweep['structure_level'],
                            'zone_low':float(ob.Low),'zone_high':float(ob.Open),'bos_index':i}
                        sweep=None;record['SMCStage']='STRUCTURE_BREAK_CONFIRMED'
            if i>=20 and not zone and not record['SMCSignal']:
                level=min(float(r.Low) for r in rows[i-20:i])
                if b.Low<level and close>level:
                    record['SMCStage']='LIQUIDITY_SWEEP_FOUND'
                    sweep={'index':i,'date':str(b.Date.date()),'low':float(b.Low),'level':level,
                           'structure_level':max(float(r.High) for r in rows[i-5:i])}
            records.append(record)
        f['SMCStage']=[r['SMCStage'] for r in records]
        f['SMCSignal']=[r['SMCSignal'] for r in records];f['SMCContext']=[r['SMCContext'] for r in records]
        f['Regime']=['SMC' if r['SMCSignal'] else ('HIGH_VOL' if b.Regime=='HIGH_VOL' else 'UNCERTAIN' if b.Ready else 'WARMUP') for b,r in zip(rows,records)]
        f['RoutedStrategy']=f.SMCSignal.map({True:'SMC',False:'NONE'})
        parts.append(f)
    return pd.concat(parts,ignore_index=True).sort_values(['Date','Symbol']).reset_index(drop=True)


def screening_candidates(daily,held,index,limit=3,*,priority_symbols=()):
    """Liquidity/history screen only: do not inspect SMC signals or future returns."""
    eligible=[];audit=[]
    for b in daily.itertuples():
        reasons=[]
        if b.Symbol in held:reasons.append('ALREADY_HELD_OR_PENDING')
        if not b.Ready or b.HistorySessions<60:reasons.append('INSUFFICIENT_HISTORY')
        if not math.isfinite(b.AverageTurnover20) or b.AverageTurnover20<10_000_000:reasons.append('LOW_LIQUIDITY')
        if b.Regime=='HIGH_VOL' or b.ATR14<=0 or b.ATR14/b.Close>.065:reasons.append('VOLATILITY_LIMIT')
        if b.RecentDiscontinuity:reasons.append('UNREVIEWED_PRICE_DISCONTINUITY')
        r={'symbol':str(b.Symbol),'date':str(b.Date.date()),'strategy':'NONE','regime':'UNASSESSED',
           'eligible':not reasons,'selected':False,'reasons':reasons,'score':0.,'rank':None,
           'average_turnover_20_inr':float(b.AverageTurnover20) if math.isfinite(b.AverageTurnover20) else None,
           'research_order':'EVIDENCE_BEFORE_SIGNAL'}
        audit.append(r)
        if not reasons:eligible.append(r)
    eligible.sort(key=lambda r:(-r['average_turnover_20_inr'],r['symbol']))
    if eligible:
        priority=set(priority_symbols)
        watched=[r for r in eligible if r['symbol'] in priority]
        if watched:
            offset=index%len(watched);watched=watched[offset:]+watched[:offset]
        others=[r for r in eligible if r['symbol'] not in priority]
        if others:
            offset=(index*limit)%len(others);others=others[offset:]+others[:offset]
        for rank,r in enumerate((watched+others)[:limit],1):r.update(selected=True,rank=rank)
    return audit


SMC_REASONS={
    'SMC_RECOVERY_CONFIRMED':'After the recorded stop, a later bullish close reclaimed the stop and original order-block upper level above the prior session high.',
    'WAITING_SMC_RECOVERY':'Stopped SMC position: waiting for a later bullish recovery above the stop, original zone and previous high.',
    'SMC_REENTRY_SAME_SESSION':'A stop sale occurred this session; same-session SMC re-entry is not permitted.',
    'SMC_REENTRY_UNAVAILABLE':'The SMC recovery attempt is exhausted, expired or cancelled by adverse evidence.',
    'WAITING_SWEEP':'No qualifying liquidity sweep yet.',
    'LIQUIDITY_SWEEP_FOUND':'Liquidity sweep found; a later bullish structure break is still required.',
    'WAITING_STRUCTURE_BREAK':'Prior sweep found; waiting for the bullish displacement close above structure.',
    'STRUCTURE_BREAK_CONFIRMED':'Structure break confirmed; waiting for a later order-block retest.',
    'WAITING_RETEST':'Order-block zone is active; no qualifying bullish retest close yet.',
    'ENTRY_CONFIRMED':'Sweep, later structure break and subsequent bullish zone retest confirmed.',
    'SWEEP_EXPIRED':'The prior sweep expired without a later qualifying structure break.',
    'SWEEP_INVALIDATED':'Price closed below the sweep low before a qualifying structure break.',
    'SETUP_EXPIRED':'The previous order-block setup expired before a qualifying retest.',
    'ZONE_INVALIDATED':'A close below the order-block zone invalidated that setup.',
    'HIGH_VOL':'High-volatility exclusion; no entry eligibility.',
    'WARMUP':'Insufficient completed indicator history.'}
