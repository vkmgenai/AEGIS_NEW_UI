"""Explicitly authorized real Codex C2 smoke; never prints account credentials.

Run --consent-plan-usage for ONE HINDUNILVR 2023-03-31 case (at most 8 CLI
invocations). Saves a genuine UI-loadable research result, not a mocked result.
"""
import argparse,json,os
from pathlib import Path
from scripts.launch_local import read_env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consent-plan-usage',action='store_true',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];os.environ.update(read_env(root/'.env'))
    os.environ['AEGIS_LLM_BACKEND']='codex_cli'
    from aegistrade.llm_backend import require_backend_ready
    require_backend_ready()
    from aegistrade.market import load_configured_market
    from aegistrade.strategies import prepare_indicators
    from aegistrade.research_service import ResearchSettings,execute_research
    from aegistrade.research_gate import validate_completed_c2
    f=prepare_indicators(load_configured_market())
    result=execute_research(f,ResearchSettings(configuration='C2',cases=1,start_date='2023-03-31',end_date='2023-03-31',
        automatic_stock_selection=True,consent_to_paid_calls=args.consent_plan_usage,use_memory=False),save_dir=root/'data'/'research_runs')
    output=result['outputs'][0]
    valid=False
    if output['guard_pass']:valid=validate_completed_c2(output)['validated_c2']
    report={'generation':'GENUINE Codex CLI using existing ChatGPT login; no mocked generation',
        'run_id':result['run_id'],'case_id':output['case_id'],'inference':result['inference'],
        'summary':result['summary'],'guard_pass':output['guard_pass'],'research_gate_pass':valid,
        'tool_transport':output.get('tool_transport'),'tools_observed':output.get('tools_observed'),
        'tool_calls':output.get('tool_calls'),'errors':output.get('model_errors'),
        'usage':output.get('usage'),'company_assessment':output.get('company_assessment')}
    (root/'reports'/'codex_c2_demo.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return 0 if valid else 1

if __name__=='__main__':raise SystemExit(main())
