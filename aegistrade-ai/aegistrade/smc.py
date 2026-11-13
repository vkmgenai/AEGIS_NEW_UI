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
        rows=list(f.itertuples())
        for i,b in enumerate(rows):
            record={'SMCSignal':False,'SMCContext':None};close=float(b.Close)
            if not b.Ready or b.Regime=='HIGH_VOL':
                sweep=zone=None;records.append(record);continue
            # A zone is available only after its completed structure-break candle.
            if zone:
                if i-zone['bos_index']>10 or close<zone['zone_low']:zone=None
                elif i>zone['bos_index'] and b.Low<=zone['zone_high'] and b.High>=zone['zone_low'] and close>zone['zone_high'] and close>b.Open:
                    record={'SMCSignal':True,'SMCContext':{k:v for k,v in zone.items() if k!='bos_index'}}
                    zone=None;sweep=None
            if sweep and not zone and not record['SMCSignal']:
                if i-sweep['index']>10 or close<sweep['low']:sweep=None
                elif i>sweep['index'] and close>sweep['structure_level'] and close>b.Open and close-b.Open>=.5*b.ATR14:
                    bearish=[r for r in rows[max(0,sweep['index']-3):i] if r.Close<r.Open]
                    if bearish:
                        ob=bearish[-1]
                        zone={'sweep_date':sweep['date'],'structure_date':str(b.Date.date()),
                            'sweep_level':sweep['level'],'structure_level':sweep['structure_level'],
                            'zone_low':float(ob.Low),'zone_high':float(ob.Open),'bos_index':i}
                        sweep=None
            if i>=20 and not zone and not record['SMCSignal']:
                level=min(float(r.Low) for r in rows[i-20:i])
                if b.Low<level and close>level:
                    sweep={'index':i,'date':str(b.Date.date()),'low':float(b.Low),'level':level,
                           'structure_level':max(float(r.High) for r in rows[i-5:i])}
            records.append(record)
        f['SMCSignal']=[r['SMCSignal'] for r in records];f['SMCContext']=[r['SMCContext'] for r in records]
        f['Regime']=['SMC' if r['SMCSignal'] else ('HIGH_VOL' if b.Regime=='HIGH_VOL' else 'UNCERTAIN' if b.Ready else 'WARMUP') for b,r in zip(rows,records)]
        f['RoutedStrategy']=f.SMCSignal.map({True:'SMC',False:'NONE'})
        parts.append(f)
    return pd.concat(parts,ignore_index=True).sort_values(['Date','Symbol']).reset_index(drop=True)


def screening_candidates(daily,held,index,limit=3):
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
        offset=(index*limit)%len(eligible);rotated=eligible[offset:]+eligible[:offset]
        for rank,r in enumerate(rotated[:limit],1):r.update(selected=True,rank=rank)
    return audit
