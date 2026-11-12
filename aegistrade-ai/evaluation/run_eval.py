"""Deterministic safety/retrieval/routing evaluation, no LLM call or broker access.

Do not modify held-out labels based on these results; if you inspect and tune them,
reclassify those cases as development and collect new genuinely held-out cases.
"""
from __future__ import annotations
from datetime import timedelta
import argparse, tempfile, json,sys
from pathlib import Path
from collections import defaultdict
from aegistrade.knowledge import PolicyRetriever,evaluate_retrieval
from aegistrade.security import scan_untrusted_text
from aegistrade.safety import (RiskInputs,RiskParameters,OrderProposal,
                               AuditBroker,make_demo_order,validate_risk,utc_now)

HERE=Path(__file__).resolve().parent

def jsonl(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

def run_cases(cases):
    errors=[]; successes=0
    for case in cases:
        kind=case['kind'];inp=case['input'];expected=case['expected']
        got=None
        if kind=='route':
            got={'TREND':'EMA_TREND','RANGE':'RSI_REVERSION','BREAKOUT':'BREAKOUT'}.get(inp['regime'],'NONE')
        elif kind=='risk':
            now=utc_now()
            order=make_demo_order('RELIANCE',100,2,'EMA_TREND','2024-01-05',
                                  RiskInputs(equity=100000,available_cash=100000,current_positions=0),RiskParameters(),now)
            p=order.model_dump()
            if inp['fault']=='stop_above':p['stop_loss_price']=101+inp['variant']
            order=OrderProposal.model_validate(p)
            cash=1 if inp['fault']=='cash_exceeded' else 100000
            positions=5 if inp['fault']=='position_count' else 0
            got=validate_risk(order,RiskInputs(equity=100000,available_cash=cash,current_positions=positions),RiskParameters())['ok']
        elif kind=='broker':
            now=utc_now()
            r=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
            policy=RiskParameters(max_quote_age_seconds=90)
            order=make_demo_order('RELIANCE',100,2,'EMA_TREND','2024-01-05',r,policy,now)
            with tempfile.TemporaryDirectory() as tmp:
                b=AuditBroker(Path(tmp)/'broker.sqlite')
                token=b.approve(order)
                quote=100 if inp['fault']!='price_move' else 120
                quote_time=now-timedelta(seconds=1000 if inp['fault']=='stale_quote' else 0)
                if inp['fault']=='approval_mismatch':token='not-a-valid-token'
                response=b.submit(order,token,quote,quote_time.isoformat(),r,policy,now)
                if inp['fault']=='duplicate':
                    again=b.submit(order,token,quote,quote_time.isoformat(),r,policy,now)
                    assert again.get('idempotent_replay') is True
                got=response['status']
        else:raise ValueError(kind)
        if got==expected:successes+=1
        else:errors.append({'id':case['id'],'expected':expected,'actual':got})
    return {'count':len(cases),'correct':successes,'accuracy':round(successes/max(len(cases),1),3),'errors':errors}

def security_eval():
    attacks=jsonl(HERE/'redteam'/'attacks_32.jsonl')
    clean=jsonl(HERE/'redteam'/'clean_10.jsonl')
    blocked=sum(not scan_untrusted_text(c['payload'])['ok'] for c in attacks)
    false=sum(not scan_untrusted_text(c['payload'])['ok'] for c in clean)
    return {'attacks':len(attacks),'scanner_detection_rate':round(blocked/len(attacks),3),
            'model_attack_success_rate':None,
            'false_blocks':false,'clean_total':len(clean),
            'warning':'Deterministic prompt-scan proxy; not a real LLM jailbreak success rate.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--split',choices=['dev','heldout','both'],default='dev')
    parser.add_argument('--retrieval-mode',choices=['offline','neural'],default='offline')
    parser.add_argument('--demo-failure',action='store_true',help='Deliberately corrupt one development expectation to demonstrate the CI gate')
    parser.add_argument('--output',default='reports/eval_latest.json')
    args=parser.parse_args()
    paths={'dev':[HERE/'golden'/'development.jsonl'],
           'heldout':[HERE/'golden'/'heldout'/'heldout.jsonl'],
           'both':[HERE/'golden'/'development.jsonl',HERE/'golden'/'heldout'/'heldout.jsonl']}
    selected=sum([jsonl(p) for p in paths[args.split]],[])
    if args.demo_failure:
        if args.split!='dev':raise ValueError('Failure demonstration is development-only')
        selected=[dict(c,expected='INTENTIONAL_CI_FAILURE_DEMO') if i<3 else c for i,c in enumerate(selected)]
    baseline=PolicyRetriever(mode=args.retrieval_mode)
    queries=jsonl(HERE/'retrieval'/'queries_36.jsonl')
    r0=evaluate_retrieval(baseline,queries,5,rewrite=False)
    r1=evaluate_retrieval(baseline,queries,5,rewrite=True)
    result={'intentional_failure_demo':args.demo_failure,'run_type':'synthetic_reference_checks','split':args.split,'case_results':run_cases(selected),
           'retrieval_before':{'queries':r0['queries'],'hit_at_5':r0['hit_at_k'],'recall_at_5':r0['recall_at_k']},
           'retrieval_after':{'queries':r1['queries'],'hit_at_5':r1['hit_at_k'],'recall_at_5':r1['recall_at_k']},
           'retrieval_mode':args.retrieval_mode,'security':security_eval(),
           'limitations':['Labels generated as candidate references; require independent team review',
                          'Retrieval labels author-assigned; neural mode must be run for full course bar',
                          'No measured multi-agent vs single-agent LLM outcomes in this report',
                          'No human-labelled judge Cohen kappa yet',
                          'Red team guard result is a scanner proxy, not live model attack success']}
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    return 0 if result['case_results']['accuracy']>=0.90 else 1
if __name__=='__main__':sys.exit(main())
