"""One genuine previously failing BHARTIARTL case; at most 8 inference units.

Requires explicit consent. Uses the existing dated archive without refreshing.
Does not rerun or rewrite the paused portfolio.
"""
import argparse,json,os
from pathlib import Path
from scripts.launch_local import read_env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consent-plan-usage',action='store_true',required=True)
    parser.parse_args()
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.research_service import ResearchSettings,execute_research
    from aegistrade.research_gate import validate_completed_c2
    f=prepare_indicators(load_configured_market())
    f=f[(f.Symbol=='BHARTIARTL')&(f.Date.astype(str)=='2023-08-01')]
    result=execute_research(f,ResearchSettings(configuration='C2',cases=1,start_date='2023-08-01',end_date='2023-08-01',
        automatic_stock_selection=False,use_memory=False,consent_to_paid_calls=True),save_dir=root/'data'/'research_runs')
    out=result['outputs'][0]
    gate=False
    if out['guard_pass']:gate=validate_completed_c2(out)['validated_c2']
    report={'source_version':'0.16.1','generation':'GENUINE selected backend; no mocked inference',
        'run_id':result['run_id'],'case_id':out['case_id'],'inference':result['inference'],
        'prompt_version':out['prompt_version'],'guard_pass':out['guard_pass'],'research_gate_pass':gate,
        'llm_calls':out['llm_calls'],'tool_calls':out.get('tool_calls'),'model_errors':out['model_errors'],
        'failure':out.get('failure'),'company_assessment':out.get('company_assessment'),
        'validation_events':[e for e in out.get('trajectory',[]) if e['event']=='validation_failed'],
        'usage':out['usage'],'original_portfolio_modified':False}
    (root/'reports'/'field_validation_fix.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return 0 if not any(e.get('code')=='OUTPUT_SCHEMA_INVALID' for e in report['validation_events']) else 1

if __name__=='__main__':raise SystemExit(main())
