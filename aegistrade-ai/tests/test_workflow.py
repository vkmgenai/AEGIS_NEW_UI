import sqlite3
import uuid
import pytest
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators,entry_signal
from aegistrade.safety import AuditBroker,RiskInputs,RiskParameters
from aegistrade.knowledge import PolicyRetriever
from aegistrade.openrouter import BudgetedExplainer


def test_human_approval_interrupt_and_resume(tmp_path,researched_context):
    pytest.importorskip("langgraph")
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command
    from aegistrade.workflow import build_trade_graph
    f=prepare_indicators(synthetic_market())
    row=next(r for r in f.itertuples(index=False) if r.RoutedStrategy!="NONE" and entry_signal(r,r.RoutedStrategy))
    broker=AuditBroker(tmp_path/"mock.sqlite")
    graph=build_trade_graph(f,broker,RiskInputs(equity=100000,available_cash=100000,current_positions=0),
                            RiskParameters(),PolicyRetriever(),BudgetedExplainer(),InMemorySaver(),
                            research_context=researched_context(row),quote_price=float(row.Close),quote_observed_utc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())
    cfg={"configurable":{"thread_id":"test-"+uuid.uuid4().hex}}
    paused=graph.invoke({"symbol":row.Symbol,"signal_date":row.Date.strftime("%Y-%m-%d")},cfg)
    assert "__interrupt__" in paused
    review=paused["__interrupt__"][0].value
    assert review["order"]["quantity"]>0
    completed=graph.invoke(Command(resume={"decision":"approve","payload_hash":review["payload_hash"]}),cfg)
    assert completed["status"]=="ACCEPTED_SIMULATED"
    assert broker.reconcile(review["order"]["request_id"])["status"]=="ACCEPTED_SIMULATED"
