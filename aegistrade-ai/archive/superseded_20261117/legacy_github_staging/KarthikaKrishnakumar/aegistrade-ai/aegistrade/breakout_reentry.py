"""Portfolio-owned breakout stop/bounce state, shared by both replay engines."""
WINDOW_SESSIONS=10


def register_breakout_stop(watches,position,when,index,enabled=True):
    if not enabled or position['strategy']!='BREAKOUT':return
    used=int(position.get('breakout_reentry_count',0))
    watches[position['symbol']]={'symbol':position['symbol'],'stop_date':when,'stop_index':index,
        'stop_level':float(position['stop']),'expires_index':index+WINDOW_SESSIONS,
        'original_entry_date':position.get('entry_date'),'attempts_used':used,
        'status':'WATCHING' if used<1 else 'EXHAUSTED'}


def reentry_candidates(daily,watches,index):
    """Past stop plus completed-close rebound; never use future bars or same-day bounce."""
    result=daily.copy()
    for symbol,watch in list(watches.items()):
        if index>watch['expires_index']:
            del watches[symbol];continue
        mask=result.Symbol==symbol
        for row_index,row in result[mask].iterrows():
            qualifies=(watch['status']=='WATCHING' and index>watch['stop_index'] and bool(row.Ready)
                and row.Regime not in {'HIGH_VOL','WARMUP'} and row.ADX14>=18 and
                row.Close>watch['stop_level'] and row.Close>row.EMA20 and
                row.Close>getattr(row,'PriorHigh',float('inf')))
            result.loc[row_index,'Regime']='BREAKOUT_BOUNCE' if qualifies else 'UNCERTAIN'
            result.loc[row_index,'RoutedStrategy']='BREAKOUT' if qualifies else 'NONE'
    return result


def reentry_context(watch):
    return {k:watch[k] for k in ('stop_date','stop_level','original_entry_date')}
