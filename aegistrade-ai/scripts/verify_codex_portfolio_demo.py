"""One tiny genuine Codex historical portfolio; existing archives only.

Explicit plan-use consent required. Missing cached packs are blocked, never
fabricated or downloaded by this verification. The UI can additionally prepare
missing public archives. No mocked generation, sizing, tools, fills or validators.
"""
import argparse,json,os
from pathlib import Path
from scripts.launch_local import read_env


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--consent-plan-usage',action='store_true',required=True)
    p.parse_args()
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    os.environ['AEGIS_LLM_BACKEND']='codex_cli'
    from aegistrade.llm_backend import require_backend_ready
    require_backend_ready()
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.company_research import read_company_research
    from aegistrade.c2_portfolio import C2PortfolioSettings,create_run,execute_run
    f=prepare_indicators(load_configured_market())
    cfg=C2PortfolioSettings(start_date='2023-03-31',end_date='2023-04-03',initial_capital=200000,
        max_model_calls=16,consent_to_paid_calls=True,approve_historical_rules=True)
    rid=create_run(f,cfg,source='nsepython',provenance={'requested_start':'2021-11-08','requested_end':'2026-11-08'})
    result=execute_run(rid,f,preparer=read_company_research)
    report={'generation':'GENUINE Codex CLI using ChatGPT sign-in; no mocked generation',
        'archive_policy':'Existing actual dated cache only; absent coverage blocks. UI may prepare additional archives.',
        'run_id':rid,'status':result['status'],'inference':result['inference'],'model_usage':result['model_usage'],
        'ledger':result['ledgers']['C2'],'open_holdings':result['open_holdings'],
        'accounting':result['accounting'],'decisions':result['decisions'],'metrics':result['metrics']}
    (root/'reports'/'codex_c2_portfolio_demo.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return 0 if result['status'].startswith('COMPLETED') and result['ledgers']['C2'] else 1

if __name__=='__main__':raise SystemExit(main())
