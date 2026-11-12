"""Named research datasets; profile labels are UI metadata, never company evidence."""
from pathlib import Path
from datetime import date
import json,hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PROFILES={
 'nifty20':{'name':'Existing Nifty 50 — frozen top 20','directory':'nse_nifty20','count':20,'selection':'top_liquidity','index':'nifty50',
     'description':'Retained pre-period liquidity-selected subset; original data and results are preserved.'},
 'nifty100':{'name':'Nifty 100 — frozen constituent snapshot','directory':'nse_nifty100','count':100,'selection':'all_members','index':'nifty100',
     'description':'All members of a frozen official Nifty 100 snapshot; current membership applied backwards has survivorship bias.'},
 'research30':{'name':'Diversified research — frozen 30','directory':'nse_research30','count':30,'selection':'all_members','index':None,
     'description':'21 established-company, 6 cyclical and 3 event-research cases. Purpose-built selection, not 70% guaranteed winners or an exact historical Nifty 100 reconstruction.'}}


def profile(key):
    if key not in PROFILES:raise ValueError('Unknown universe; choose nifty20, nifty100 or research30')
    return {'id':key,**PROFILES[key]}


def folder(data_root,key,legacy=None):
    p=profile(key)
    return Path(legacy) if key=='nifty20' and legacy else Path(data_root)/p['directory']


def curated_members():
    rows=pd.read_csv(ROOT/'config/universes/research30.csv')
    counts=rows.ResearchGroup.value_counts().to_dict()
    if len(rows)!=30 or rows.Symbol.duplicated().any() or counts!={'established':21,'cyclical':6,'event_research':3}:
        raise ValueError('Frozen research30 definition must contain 21/6/3 distinct symbols')
    return rows


def official_members():
    path=ROOT/'config/universes/nifty100_snapshot.csv'
    meta=json.loads(path.with_suffix('.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Official frozen Nifty 100 snapshot checksum mismatch')
    rows=pd.read_csv(path)
    if len(rows)!=100 or rows.Symbol.duplicated().any():raise ValueError('Official frozen snapshot must contain 100 distinct symbols')
    return rows,meta


def definition_hash(key):
    value=profile(key)
    if key=='research30':value['members']=curated_members().to_dict('records')
    if key=='nifty100':value['snapshot_sha256']=official_members()[1]['sha256']
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def catalogue(data_root,active_folder,*,legacy=None):
    result=[]
    for key in PROFILES:
        p=profile(key);path=folder(data_root,key,legacy);manifest_file=path/'manifest.json'
        manifest=json.loads(manifest_file.read_text()) if manifest_file.exists() else None
        result.append({**p,'active':path.resolve()==Path(active_folder).resolve(),
            'available':bool(manifest and manifest.get('status')=='complete'),
            'manifest':manifest,'members':curated_members().to_dict('records') if key=='research30' else official_members()[0].to_dict('records') if key=='nifty100' else [],
            'cached_chunks':sum(1 for _ in (path/'chunks').glob('*/*.csv')) if path.exists() else 0})
    return result


def validate_manifest(key,manifest):
    if key=='nifty20':return
    expected=curated_members().Symbol if key=='research30' else official_members()[0].Symbol
    if manifest.get('universe_id')!=key or set(manifest.get('symbols',[]))!=set(expected):
        raise ValueError('Prepared dataset does not match the selected frozen universe')
    if manifest.get('definition_sha256')!=definition_hash(key):raise ValueError('Frozen universe definition hash differs from prepared data')
