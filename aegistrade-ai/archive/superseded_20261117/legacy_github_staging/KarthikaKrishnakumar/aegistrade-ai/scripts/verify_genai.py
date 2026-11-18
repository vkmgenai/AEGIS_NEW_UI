"""One explicitly authorized, bounded C2 smoke run; never prints secrets."""
import json
import os
from pathlib import Path
from scripts.launch_local import read_env
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators
from aegistrade.research_service import ResearchSettings, execute_research


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--consent-paid',action='store_true',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    os.environ.update(read_env(root/'.env'))
    result=execute_research(prepare_indicators(synthetic_market(n_days=230)),
        ResearchSettings(configuration='C2',cases=1,consent_to_paid_calls=args.consent_paid,
                         max_output_tokens_per_case=4800),
        model=__import__('aegistrade.llm_backend',fromlist=['model_name']).model_name(),save_dir=root/'data'/'research_runs')
    print(json.dumps({'run_id':result['run_id'],'summary':result['summary'],
                      'errors':[x['model_errors'] for x in result['outputs']],
                      'tools':[x.get('tools_observed') for x in result['outputs']]},indent=2))
    return 0 if all(x['guard_pass'] for x in result['outputs']) else 1


if __name__=='__main__':raise SystemExit(main())
