"""Verified NSE identifier continuity; no price/corporate-action adjustment."""
from pathlib import Path
from datetime import date,timedelta
from functools import lru_cache
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]/'config'/'universes'


@lru_cache(maxsize=1)
def metadata():
    tables={};sources={}
    for name in ('symbolchange','EQUITY_L'):
        path=ROOT/(name+'.csv');source=json.loads(path.with_suffix('.json').read_text())
        if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:raise ValueError('Frozen NSE security metadata checksum mismatch')
        table=pd.read_csv(path);table.columns=table.columns.str.strip();tables[name]=table;sources[name]=source
    return tables,sources


def segments(symbol,start,end,*,clip_listing=True):
    tables,_=metadata();changes=tables['symbolchange'];current=symbol;upper=end;pieces=[];seen=set()
    while True:
        if current in seen:raise ValueError('Cyclic official symbol-change history')
        seen.add(current);rows=changes[changes['NEW SYMBOL']==current]
        if len(rows)>1:raise ValueError('Ambiguous official symbol-change history')
        if rows.empty:
            lower=start
            if clip_listing and len(seen)==1:
                listing=tables['EQUITY_L'];listing=listing[listing.SYMBOL==symbol]
                if len(listing)==1:lower=max(lower,pd.to_datetime(listing.iloc[0]['DATE OF LISTING'],format='%d-%b-%Y').date())
            if lower<=upper:pieces.append((current,lower,upper))
            break
        row=rows.iloc[0];changed=pd.to_datetime(row['EFFECTIVE DATE'],format='%d-%b-%Y').date()
        lower=max(start,changed)
        if lower<=upper:pieces.append((current,lower,upper))
        if changed<=start:break
        upper=min(upper,changed-timedelta(days=1));current=row['OLD SYMBOL']
    return sorted(pieces,key=lambda item:item[1])
