"""Run exact-hash/stale/timeout simulations without LangGraph/OpenRouter.

Full graph approval demo remains in Colab or FastAPI. This isolated deterministic
smoke test is NOT a substitute for LangGraph's human interrupt and resume trace.
"""
from __future__ import annotations
import json,tempfile
from pathlib import Path
from datetime import timedelta
from aegistrade.safety import (RiskParameters,RiskInputs,AuditBroker,make_demo_order,
                               utc_now,validate_risk,payload_hash)

def main():
    now=utc_now();pol=RiskParameters(max_quote_age_seconds=90)
    risk=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    with tempfile.TemporaryDirectory() as d:
        b=AuditBroker(Path(d)/'orders.sqlite')
        o=make_demo_order('RELIANCE',100,2,'EMA_TREND','2024-01-05',risk,pol,now)
        print('Prepared synthetic order:',o.model_dump_json(indent=2))
        print('Risk checks:',json.dumps(validate_risk(o,risk,pol),indent=2))
        print('Payload SHA256:',payload_hash(o))
        print('Unapproved submission:',b.submit(o,'invalid',100,now.isoformat(),risk,pol,now))
        tok=b.approve(o,reviewer='CLI_SIMULATED_HUMAN_ACTION')
        print('Stale quote:',b.submit(o,tok,100,(now-timedelta(seconds=1000)).isoformat(),risk,pol,now))
        print('Fresh quote submit with injected timeout after commit:')
        try:b.submit(o,tok,100,now.isoformat(),risk,pol,now,simulate_timeout_after_commit=True)
        except TimeoutError:print('Transport timeout injected; reconciling by request ID:',b.reconcile(o.request_id))
        print('Retry same request safely:',b.submit(o,tok,100,now.isoformat(),risk,pol,now))
        print('Number of accepted simulated orders:',b.conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0])
        assert b.conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]==1
if __name__=='__main__':main()
