"""Safe local smoke test for capital/date simulation and zero-token C0; run with API started."""
from __future__ import annotations
import json
import os
import sys
import requests

BASE = os.getenv("AEGIS_API_URL", "http://127.0.0.1:8000").rstrip("/")


def main():
    try:
        health=requests.get(BASE+"/health",timeout=10);health.raise_for_status()
        universe=requests.get(BASE+"/market/universe",timeout=10);universe.raise_for_status()
        info=universe.json()
        end=info['last_date']
        first=info['first_date']
        sim=requests.post(BASE+"/simulation/run",json={
            "initial_capital":200000,"start_date":first,"end_date":end,
            "mode":"ALL","risk_percent":1.0},timeout=90)
        sim.raise_for_status()
        c0=requests.post(BASE+"/research/experiments/run",json={"configuration":"C0","cases":1},timeout=45)
        c0.raise_for_status()
        sj=sim.json();rj=c0.json()
        print(json.dumps({"api_health":health.json(),"capital":sj['settings']['initial_capital'],
            "simulation_id":sj['run_id'],"strategies":[m['mode'] for m in sj['metrics']],
            "period":sj['period'],"C0_calls":rj['summary'][0]['model_calls'],
            "c0_run_id":rj['run_id']},indent=2))
        return 0
    except requests.RequestException as exc:
        print("Local smoke check failed:",str(exc)[:600],file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
