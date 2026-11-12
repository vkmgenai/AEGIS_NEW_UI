"""Resumable NSEPython OHLCV downloads with explicit universe/provenance metadata."""
from __future__ import annotations
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from io import StringIO
import hashlib,json,re,time
from urllib.parse import quote
import pandas as pd
import requests
from .market import validate_ohlcv

CONSTITUENT_URLS=[
    'https://archives.nseindia.com/content/indices/ind_nifty50list.csv',
    'https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv',
]
ALIASES=json.loads((Path(__file__).resolve().parents[1]/'config'/'nse_symbol_aliases.json').read_text())
RAW_COLUMNS={'CH_TIMESTAMP':'Date','CH_SYMBOL':'Symbol','CH_OPENING_PRICE':'Open',
    'CH_TRADE_HIGH_PRICE':'High','CH_TRADE_LOW_PRICE':'Low','CH_CLOSING_PRICE':'Close','CH_TOT_TRADED_QTY':'Volume'}


def normalize_nse_history(raw,symbol,*,allowed_aliases=()):
    if raw.empty:return pd.DataFrame(columns=['Date','Symbol','Open','High','Low','Close','Volume'])
    data=raw.rename(columns=RAW_COLUMNS).copy()
    required={'Date','Open','High','Low','Close','Volume'}
    if not required.issubset(data):raise ValueError('NSE history schema missing OHLCV fields')
    if 'Symbol' not in data:data['Symbol']=symbol
    allowed={symbol,*ALIASES.get(symbol,{}).get('previous_symbols',[]),*allowed_aliases}
    if not set(data.Symbol.astype(str).str.upper()).issubset(allowed):raise ValueError('Provider returned an unverified different symbol')
    data['Symbol']=symbol
    if 'CH_SERIES' in data:data=data[data.CH_SERIES=='EQ']
    # CH_TIMESTAMP is an exchange session date, not a UTC instant.
    data['Date']=pd.to_datetime(data.Date,format='mixed').dt.normalize()
    keys=['Date','Symbol','Open','High','Low','Close','Volume']
    data=data[keys].drop_duplicates()
    return validate_ohlcv(data)


def constituents(path=None,*,index="nifty50"):
    if path:
        result=pd.read_csv(path)
    else:
        errors=[]
        urls=CONSTITUENT_URLS if index=='nifty50' else [
            'https://archives.nseindia.com/content/indices/ind_nifty100list.csv',
            'https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv'] if index=='nifty100' else []
        if not urls:raise ValueError('Unsupported official index snapshot')
        for url in urls:
            try:
                response=requests.get(url,timeout=20);response.raise_for_status()
                result=pd.read_csv(StringIO(response.text));break
            except (requests.RequestException,ValueError):errors.append(url)
        else:raise RuntimeError('Official constituent CSV unavailable; supply a dated official snapshot file')
    if 'Symbol' not in result or result.Symbol.duplicated().any():raise ValueError('Invalid constituent CSV')
    result['Symbol']=result.Symbol.str.strip().str.upper()
    if not result.Symbol.str.fullmatch(r'[A-Z0-9][A-Z0-9_&-]{1,29}').all():raise ValueError('Invalid NSE symbol')
    return result


def fetch_symbol(symbol,start,end,cache_dir,*,fetcher=None,pause=.25,progress=print,identity=False):
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9_&-]{1,29}',symbol):raise ValueError('Invalid NSE symbol')
    if fetcher is None:
        from nsepython import equity_history
        fetcher=lambda symbol,series,start,end:equity_history(quote(symbol,safe=""),series,start,end)
    periods=[(symbol,start,end)]
    if identity:
        from .security_identity import segments
        periods=segments(symbol,start,end)
    cache_dir=Path(cache_dir)/(quote(symbol,safe='')+('__identity_v1' if identity else ''));cache_dir.mkdir(parents=True,exist_ok=True)
    frames=[];cursor=start
    while cursor<=end:
        finish=min(cursor+timedelta(days=38),end)  # <40 days: one library history request
        path=cache_dir/f'{cursor}_{finish}.csv'
        if path.exists():
            chunk=pd.read_csv(path,parse_dates=['Date'])
            if len(chunk):chunk=validate_ohlcv(chunk)
        else:
            pieces=[];made_request=False
            for requested,a,b in periods:
                left=max(cursor,a);right=min(finish,b)
                if left>right:continue
                made_request=True
                raw=fetcher(requested,'EQ',left.strftime('%d-%m-%Y'),right.strftime('%d-%m-%Y'))
                piece=normalize_nse_history(raw,symbol,allowed_aliases=[item[0] for item in periods])
                if len(piece) and (piece.Date.min().date()<left or piece.Date.max().date()>right):raise ValueError('Provider returned dates outside the verified symbol interval')
                if len(piece):pieces.append(piece)
            chunk=validate_ohlcv(pd.concat(pieces,ignore_index=True)) if pieces else pd.DataFrame(columns=['Date','Symbol','Open','High','Low','Close','Volume'])
            if len(chunk) and (chunk.Date.min().date()<cursor or chunk.Date.max().date()>finish):
                raise ValueError('Provider returned dates outside requested interval')
            temporary=path.with_suffix('.tmp');chunk.to_csv(temporary,index=False);temporary.replace(path)
            if pause and made_request:time.sleep(pause)
        frames.append(chunk);cursor=finish+timedelta(days=1)
    nonempty=[f for f in frames if len(f)]
    if not nonempty:return pd.DataFrame(columns=['Date','Symbol','Open','High','Low','Close','Volume'])
    return validate_ohlcv(pd.concat(nonempty,ignore_index=True).drop_duplicates())


def rank_universe(history,selection_date,limit=20,min_sessions=20):
    """Freeze a liquid universe using ONLY sessions before the evaluation start."""
    f=history[history.Date.dt.date<selection_date].copy()
    f['Turnover']=f.Close*f.Volume
    rows=[]
    for symbol,bars in f.sort_values('Date').groupby('Symbol'):
        bars=bars.tail(60)
        if len(bars)<min_sessions:continue
        rows.append({'symbol':symbol,'history_sessions':len(bars),
                     'average_daily_turnover_inr':float(bars.Turnover.mean()),
                     'last_selection_session':bars.Date.max().date().isoformat()})
    rows=sorted(rows,key=lambda r:(-r['average_daily_turnover_inr'],r['symbol']))
    for index,row in enumerate(rows,1):row['rank']=index;row['selected']=index<=limit
    if len(rows)<limit:raise ValueError(f'Only {len(rows)} symbols have sufficient pre-period history for top {limit}')
    return rows


def build_dataset(output_dir,start,end,*,top_n=20,constituent_path=None,membership_asof=None,progress=print,fetcher=None,selection_mode='top_liquidity',index='nifty50',universe_id=None,reuse_dirs=(),snapshot_date=None):
    if start>=end:raise ValueError('start must precede end')
    if not 1<=top_n<=100:raise ValueError('Choose 1–100 universe stocks')
    if selection_mode not in {'top_liquidity','all_members'}:raise ValueError('Invalid universe selection mode')
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    members=constituents(constituent_path,index=index)
    if membership_asof and membership_asof>=start:raise ValueError('Historical membership snapshot must predate the simulation start')
    warmup=start-timedelta(days=130)
    members.to_csv(output_dir/'constituents.csv',index=False)
    meta={'status':'downloading','provider':'nsepython','series':'EQ','price_adjustment':'unadjusted',
          'requested_start':start.isoformat(),'requested_end':end.isoformat(),'warmup_start':warmup.isoformat(),
          'membership_mode':'dated_start_snapshot' if membership_asof else 'current_constituents',
          'membership_asof':membership_asof.isoformat() if membership_asof else snapshot_date.isoformat() if snapshot_date else datetime.now(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat(),
          'survivorship_bias':not bool(membership_asof),
          'universe_selection':'Top pre-period 60-session average Close × Volume, at least 20 sessions; fixed for run',
          'created_utc':datetime.now(timezone.utc).isoformat(),'errors':[],'symbol_aliases':ALIASES}
    manifest=output_dir/'manifest.json'
    def save():
        temporary=manifest.with_suffix('.tmp');temporary.write_text(json.dumps(meta,indent=2,allow_nan=False));temporary.replace(manifest)
    save();selection=[];exclusions=[]
    if selection_mode=='top_liquidity':
        for i,symbol in enumerate(members.Symbol,1):
            progress(f'Universe screening {i}/{len(members)}: {symbol}')
            try:
                f=fetch_symbol(symbol,warmup,start-timedelta(days=1),output_dir/'chunks',fetcher=fetcher)
                if len(f):selection.append(f)
                if len(f)<20:exclusions.append({'symbol':symbol,'reason':'INSUFFICIENT_PRE_PERIOD_HISTORY','sessions':len(f)})
            except Exception as exc:
                meta['errors'].append({'stage':'screening','symbol':symbol,'type':type(exc).__name__});save()
                # Incomplete candidate coverage could bias the top-20 ranking; do not silently shrink the universe.
                raise RuntimeError(f'Screening failed for {symbol}; resume after resolving provider error') from exc
        ranks=rank_universe(pd.concat(selection,ignore_index=True),start,top_n)
        meta['universe_exclusions']=exclusions;meta['universe_ranking']=ranks;meta['symbols']=[r['symbol'] for r in ranks if r['selected']];save()
    else:
        meta['symbols']=members.Symbol.tolist();meta['universe_ranking']=[];meta['universe_exclusions']=[]
        meta['universe_selection']='All symbols in the frozen snapshot; no ranking by subsequent returns'
        meta['coverage_policy']='observed_listing_span'
        meta['history_availability_note']='Late starts or early ends are disclosed observed spans, not independently verified listing/delisting dates. New stocks need indicator warm-up; missing histories are never fabricated.'
        if universe_id=='research30':
            meta.update(membership_mode='curated_research_snapshot',survivorship_bias=True,
                research_groups=members.to_dict('records'),group_counts=members.ResearchGroup.value_counts().to_dict(),
                selection_bias='Deliberately selected event cases; not representative random market sampling or verified historical index membership')
        save()
    meta.update(universe_id=universe_id or 'nifty20',selection_mode=selection_mode,
        constituents_sha256=hashlib.sha256((output_dir/'constituents.csv').read_bytes()).hexdigest())
    reused={}
    for source in reuse_dirs:
        try:
            data,previous=load_dataset(source)
            if date.fromisoformat(previous['warmup_start'])>warmup or date.fromisoformat(previous['requested_end'])<end:continue
            for symbol,bars in data.groupby('Symbol'):
                reused.setdefault(symbol,(bars[(bars.Date.dt.date>=warmup)&(bars.Date.dt.date<=end)].copy(),previous['sha256']))
        except (ValueError,FileNotFoundError,KeyError):continue
    meta['reused_symbols']=[]
    if selection_mode=='all_members':
        from .security_identity import metadata
        meta['identifier_metadata']=metadata()[1]
    save()
    frames=[];coverage=[]
    for i,symbol in enumerate(meta['symbols'],1):
        progress(f'History {i}/{len(meta["symbols"])}: {symbol}')
        try:
            if symbol in reused:
                f,source_sha=reused[symbol];meta['reused_symbols'].append({'symbol':symbol,'source_sha256':source_sha})
            else:f=fetch_symbol(symbol,warmup,end,output_dir/'chunks',fetcher=fetcher,**({'identity':True} if selection_mode=='all_members' else {}))
        except Exception as exc:
            meta['errors'].append({'stage':'history','symbol':symbol,'type':type(exc).__name__});save();raise
        if f.empty:raise ValueError(f'No data for selected symbol {symbol}')
        frames.append(f);coverage.append({'symbol':symbol,'rows':len(f),
            'first_date':f.Date.min().date().isoformat(),'last_date':f.Date.max().date().isoformat()})
    combined=validate_ohlcv(pd.concat(frames,ignore_index=True))
    data_path=output_dir/'ohlcv.csv';temporary=data_path.with_suffix('.tmp');combined.to_csv(temporary,index=False);temporary.replace(data_path)
    meta.update(status='complete',coverage=coverage,rows=len(combined),
                sha256=hashlib.sha256(data_path.read_bytes()).hexdigest(),
                limitation='Raw NSE prices; corporate-action adjustments and historical constituent provenance require review. No synthetic/Yahoo fallback.')
    save()
    if selection_mode=='all_members':
        try:load_dataset(output_dir)
        except ValueError:
            meta['status']='incomplete';save();raise
    return meta


def load_dataset(path):
    path=Path(path);manifest=json.loads((path/'manifest.json').read_text())
    if manifest.get('status')!='complete':raise ValueError('NSE download is incomplete; resume the download first')
    file=path/'ohlcv.csv'
    if hashlib.sha256(file.read_bytes()).hexdigest()!=manifest['sha256']:raise ValueError('NSE dataset checksum mismatch')
    frame=validate_ohlcv(pd.read_csv(file))
    if set(frame.Symbol)!=set(manifest['symbols']):raise ValueError('Dataset universe does not match manifest')
    if manifest.get('requested_start') and manifest.get('requested_end'):
        start=pd.Timestamp(manifest['requested_start']);end=pd.Timestamp(manifest['requested_end'])
        weekdays=len(pd.bdate_range(start,end))
        for symbol,bars in frame.groupby('Symbol'):
            count=len(bars[(bars.Date>=start)&(bars.Date<=end)])
            if manifest.get('coverage_policy')=='observed_listing_span':
                first=max(start,bars.Date.min());last=min(end,bars.Date.max())
                expected=len(pd.bdate_range(first,last)) if first<=last else 0
                if not expected or count<.8*expected:raise ValueError(f'Insufficient observed-span coverage for {symbol}')
            elif count<.8*weekdays:raise ValueError(f'Insufficient five-year session coverage for {symbol}')
    return frame,manifest
