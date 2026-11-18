from datetime import timedelta
from aegistrade.safety import (AuditBroker,RiskInputs,RiskParameters,make_demo_order,
                              validate_risk,payload_hash,utc_now,OrderProposal)


def setup(tmp_path):
    b=AuditBroker(tmp_path/"broker.sqlite")
    inputs=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    p=RiskParameters()
    o=make_demo_order("INFY",100,2,"EMA_TREND","2024-05-01",inputs,p)
    return b,inputs,p,o


def test_approval_hash_is_payload_specific(tmp_path):
    b,i,p,o=setup(tmp_path)
    token=b.approve(o)
    changed=o.model_copy(update={"quantity":o.quantity+1})
    blocked=b.submit(changed,token,100,utc_now().isoformat(),i,p)
    assert blocked["status"]=="REJECTED"
    assert "approval" in blocked["reason"]


def test_stale_quote_rejected(tmp_path):
    b,i,p,o=setup(tmp_path)
    token=b.approve(o)
    stale=(utc_now()-timedelta(minutes=5)).isoformat()
    assert b.submit(o,token,100,stale,i,p)["status"]=="REJECTED"
    assert b.reconcile(o.request_id)["status"]=="NOT_FOUND"


def test_timeout_after_commit_reconciles_without_double_submission(tmp_path):
    b,i,p,o=setup(tmp_path)
    token=b.approve(o)
    import pytest
    with pytest.raises(TimeoutError):
        b.submit(o,token,100,utc_now().isoformat(),i,p,simulate_timeout_after_commit=True)
    assert b.reconcile(o.request_id)["status"]=="ACCEPTED_SIMULATED"
    retry=b.submit(o,token,100,utc_now().isoformat(),i,p)
    assert retry["idempotent_replay"] is True
    count=b.conn.execute("SELECT count(*) FROM orders WHERE request_id=?",(o.request_id,)).fetchone()[0]
    assert count==1


def test_excessive_quantity_blocked(tmp_path):
    b,i,p,o=setup(tmp_path)
    huge=o.model_copy(update={"quantity":1000})
    assert not validate_risk(huge,i,p)["ok"]
