"""Genuine two-session, automatically selected C2 portfolio demo, capped at32 units.

Only existing prepared historical evidence is used by this verification. The UI
can prepare missing packs automatically. No mocked inference, fills or validators.
"""
import argparse,json,os
from pathlib import Path
from scripts.launch_local import read_env


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--consent-plan-usage',action='store_true',required=True);p.parse_args()
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    from aegistrade.llm_backend import require_backend_ready
    require_backend_ready()
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.c2_portfolio import create_run,execute_run,C2PortfolioSettings
    from aegistrade.company_research import read_company_research
    frame=prepare_indicators(load_configured_market())
    cfg=C2PortfolioSettings(initial_capital=200000,start_date='2023-12-01',end_date='2023-12-04',
        risk_percent=1,fee_bps=5,slippage_bps=5,max_model_calls=32,holding_review_sessions=5,
        consent_to_paid_calls=True,approve_historical_rules=True)
    rid=create_run(frame,cfg,source='nsepython',provenance={'requested_start':'2021-11-08','requested_end':'2026-11-08'})
    print('Starting bounded portfolio job '+rid,flush=True)
    result=execute_run(rid,frame,preparer=read_company_research)
    report={'source_version':'0.16.2','generation':'GENUINE Codex CLI; no mocked generation, MCP, fills or validators',
        'archive_policy':'Existing prepared actual dated evidence only; missing sources block',
        'run_id':rid,'status':result['status'],'settings':result['settings'],'inference':result['inference'],
        'model_usage':result['model_usage'],'progress':result['progress'],'metrics':result['metrics'],
        'ledger':result['ledgers']['C2'],'open_holdings':result['open_holdings'],'decisions':result['decisions'],
        'accounting':result['accounting'],'last_error':result['last_error']}
    (root/'reports'/'portfolio_demo_verified.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    return 0 if result['status'].startswith('COMPLETED') and result['ledgers']['C2'] else 1

if __name__=='__main__':raise SystemExit(main())
