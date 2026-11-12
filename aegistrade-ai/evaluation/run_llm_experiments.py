"""Explicitly opt-in selectable-backend experiments on selected precomputed research snapshots.

Use --cases 1 before increasing. Do not tune held-out scenarios after inspection.
"""
from __future__ import annotations
import argparse,os,sys,json,statistics,time
from pathlib import Path
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators
from aegistrade.llm_research import run_research_case
from aegistrade.llm_backend import model_name,require_backend_ready,identity

def main():
    from scripts.launch_local import read_env
    os.environ.update(read_env(Path(__file__).resolve().parents[1]/'.env'))
    p=argparse.ArgumentParser()
    p.add_argument('--cases',type=int,default=1)
    p.add_argument('--config',choices=['C0','C1','C2','all'],default='all')
    p.add_argument('--model',default=model_name())
    p.add_argument('--output',default='reports/llm_experiments.json')
    p.add_argument('--max-calls',type=int,default=8)
    p.add_argument('--consent-paid',action='store_true')
    p.add_argument('--max-paid-calls',type=int,default=24)
    p.add_argument('--max-output-tokens',type=int,default=4800)
    a=p.parse_args()
    if not 1<=a.cases<=60:raise ValueError('Use 1..60')
    maximum=a.cases*(0 if a.config=='C0' else min(8,a.max_calls)*(2 if a.config=='all' else 1))
    if maximum>a.max_paid_calls:raise ValueError(f'Run may attempt {maximum} requests; increase explicit --max-paid-calls or reduce cases')
    if a.config!='C0' and (not a.consent_paid or os.getenv('AEGIS_ENABLE_LLM_EXPERIMENTS','false').lower()!='true'):
        raise ValueError('Explicit --consent-paid and AEGIS_ENABLE_LLM_EXPERIMENTS=true are required')
    if a.config!='C0':require_backend_ready()
    f=prepare_indicators(synthetic_market(n_days=180))
    samples=f[f.Ready].groupby('Symbol').tail(20).head(a.cases)
    outputs=[]
    for row in samples.itertuples():
        snap={'symbol':row.Symbol,'date':str(row.Date.date()),'regime':row.Regime,
              'approved_candidate':row.RoutedStrategy,'Close':float(row.Close),
              'RSI14':float(row.RSI14),'ADX14':float(row.ADX14),'EMA20':float(row.EMA20),
              'EMA50':float(row.EMA50),'ATR14':float(row.ATR14)}
        configs=['C0','C1','C2'] if a.config=='all' else [a.config]
        for config in configs:
            result=run_research_case(snap,config,a.model,a.max_calls,a.max_output_tokens)
            outputs.append({'case_id':f"{row.Symbol}-{row.Date.date()}",**result})
            print(config, outputs[-1]['case_id'], 'guard=',result['guard_pass'], 'calls=',result.get('llm_calls',0))
    report={'mode':'explicit_opt_in_research','inference':identity(model=a.model),'cases':len(samples),'model':a.model,
        'outputs':outputs,'warnings':['Small synthetic research sample; not statistically representative',
        'An output matching the code reference does not establish profitable strategy selection',
        'Use same model, evidence, available tools, and budgets for fair comparison',
        'Record prompt and completion usage and actual billed cost where returned']}
    dest=Path(a.output);dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(json.dumps(report,indent=2))
    print('Report written to',dest)
    return 0 if all(x['guard_pass'] for x in outputs) else 1
if __name__=='__main__':sys.exit(main())
