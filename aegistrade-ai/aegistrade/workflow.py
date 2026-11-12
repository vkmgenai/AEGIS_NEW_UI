"""LangGraph supervisor + 3+ specialists with exact-payload human interrupt.

Completed C2 research is mandatory; this graph reuses its explanation without new LLM calls.
Market data snapshot is historical REPLAY, not a live quote. Execution is simulated.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import TypedDict
import uuid
import math
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from .strategies import entry_signal, chosen_strategy
from .safety import (OrderProposal, RiskInputs, RiskParameters, AuditBroker, utc_now,
                     make_demo_order, validate_risk, payload_hash)
from .knowledge import PolicyRetriever
from .openrouter import BudgetedExplainer

class TradeState(TypedDict, total=False):
    symbol: str
    signal_date: str
    plan: list[str]
    market: dict
    regime: str
    strategy: str
    citations: list[str]
    explanation: str
    proposal: dict
    payload_hash: str
    risk: dict
    status: str
    approval_token: str
    reviewer_action: str
    edit_count: int
    execution: dict
    trace: list[str]


def build_trade_graph(frame:pd.DataFrame, broker:AuditBroker, risk_inputs:RiskInputs,
                      policy:RiskParameters, retriever:PolicyRetriever,
                      explainer:BudgetedExplainer, checkpointer, quote_price:float | None=None,
                      quote_observed_utc:str | None=None, inject_timeout:bool=False, research_context:dict|None=None):
    """Compiles a small resumable graph. All external-style writes occur AFTER interrupt()."""
    context = {"quote_price":quote_price, "quote_time":quote_observed_utc,
               "inject_timeout": inject_timeout}

    def supervisor_plan(s:TradeState):
        if not research_context or research_context.get('validated_c2') is not True or research_context.get('critic_accept') is not True:
            return {'status':'BLOCKED','trace':['C2_RESEARCH_REQUIRED_BEFORE_PROPOSAL']}
        return {"plan":["Validate historical replay bar", "Classify regime and candidate strategy",
                        "Create structured order", "Run deterministic risk+critic", "Human approval",
                        "Recheck quote and submit ONLY to simulator"],"trace":["PLAN_CREATED"]}

    def market_agent(s:TradeState):
        if s.get("status")=="BLOCKED":return {}
        f=frame[(frame.Symbol==s["symbol"]) & (frame.Date==pd.Timestamp(s["signal_date"]))]
        if len(f)!=1:
            return {"status":"BLOCKED", "trace":s["trace"]+["MISSING_MARKET_SNAPSHOT"]}
        row=f.iloc[0]
        snapshot=research_context.get('snapshot',{})
        if (snapshot.get('regime')!=str(row.Regime) or any(
            k not in snapshot or not math.isfinite(float(row[k])) or abs(float(row[k])-float(snapshot[k]))>1e-8
            for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14'))):
            return {'status':'BLOCKED','trace':s['trace']+['C2_MARKET_EVIDENCE_CHANGED']}
        if not row.Ready:
            return {"status":"BLOCKED", "trace":s["trace"]+["INSUFFICIENT_HISTORY"]}
        market={k:float(row[k]) for k in ["Open","High","Low","Close","Volume","EMA20","EMA50","RSI14","ATR14","ADX14","Prior20High","RealizedVol20"]}
        market["regime"]=str(row.Regime)
        return {"market":market,"regime":str(row.Regime),"status":"MARKET_READY","trace":s["trace"]+["MARKET_AGENT_OK"]}

    def strategy_agent(s:TradeState):
        if s.get("status")=="BLOCKED":
            return {}
        f=frame[(frame.Symbol==s["symbol"]) & (frame.Date==pd.Timestamp(s["signal_date"]))]
        row=f.iloc[0]
        strategy=chosen_strategy(row,"ROUTER")
        if strategy=="NONE" or not entry_signal(row,strategy):
            return {"strategy":strategy,"status":"NO_BUY_SIGNAL", "trace":s["trace"]+["STRATEGY_ABSTAIN"]}
        if (research_context['symbol']!=s['symbol'] or research_context['date']!=s['signal_date']
            or research_context['strategy']!=strategy):
            return {'status':'BLOCKED','trace':s['trace']+['RESEARCH_PROVENANCE_MISMATCH']}
        explanation=research_context['explanation']
        citations=research_context['citations']
        return {"strategy":strategy,"citations":citations,"explanation":explanation,
                "status":"STRATEGY_SELECTED","trace":s["trace"]+["STRATEGY_AGENT_OK"]}

    def proposal_agent(s:TradeState):
        m=s["market"]
        try:
            order=make_demo_order(s["symbol"],m["Close"],m["ATR14"],s["strategy"],
                                  s["signal_date"],risk_inputs,policy)
        except ValueError as e:
            return {"status":"BLOCKED","trace":s["trace"]+["PROPOSAL_ERROR:"+str(e)]}
        return {"proposal":order.model_dump(mode="json"),"payload_hash":payload_hash(order),
                "status":"PROPOSED","trace":s["trace"]+["ORDER_PROPOSED"]}

    def risk_agent(s:TradeState):
        order=OrderProposal.model_validate(s["proposal"])
        rv=validate_risk(order,risk_inputs,policy)
        return {"risk":rv,"status":"RISK_PASSED" if rv["ok"] else "BLOCKED",
                "payload_hash":payload_hash(order),"trace":s["trace"]+["RISK_PASS" if rv["ok"] else "RISK_BLOCK"]}

    def critic_agent(s:TradeState):
        if s["status"]!="RISK_PASSED":
            return {}
        o=OrderProposal.model_validate(s["proposal"])
        if (o.symbol!=s["symbol"] or o.strategy!=s["strategy"] or o.signal_date!=s["signal_date"]
            or abs(o.reference_price/s["market"]["Close"]-1)>policy.max_price_deviation_fraction):
            return {"status":"BLOCKED", "trace":s["trace"]+["CRITIC_REJECTS_CHANGED_EVIDENCE"]}
        return {"status":"CRITIC_PASSED","trace":s["trace"]+["CRITIC_PASS"]}

    def approval_gate(s:TradeState):
        if not research_context or research_context.get('validated_c2') is not True:
            return {'status':'BLOCKED','trace':s.get('trace',[])+['C2_RESEARCH_REQUIRED_BEFORE_APPROVAL']}
        # This node contains no side effects BEFORE interrupt: on resume LangGraph restarts the node.
        reply=interrupt({"question":"Human: approve, edit, or reject this exact simulated order?",
                         "order":s["proposal"],"payload_hash":s["payload_hash"],
                         "research":research_context,"explanation":s.get("explanation"),"citations":s.get("citations",[]),
                         "instructions":"Approve with {'decision':'approve','payload_hash':'...'}; edits require fresh risk check and re-approval."})
        if not isinstance(reply,dict):
            return {"status":"REJECTED", "trace":s["trace"]+["INVALID_REVIEW_RESPONSE"]}
        decision=reply.get("decision")
        if decision=="reject":
            return {"status":"REJECTED","reviewer_action":"reject","trace":s["trace"]+["HUMAN_REJECTED"]}
        if decision=="edit":
            if int(s.get("edit_count",0))>=2:
                return {"status":"REJECTED","trace":s["trace"]+["EDIT_LOOP_LIMIT"]}
            edits=reply.get("changes",{})
            if not isinstance(edits,dict) or not edits or not set(edits).issubset({"quantity","reference_price","stop_loss_price"}):
                return {"status":"REJECTED","trace":s["trace"]+["INVALID_EDIT_FIELDS"]}
            edited=dict(s["proposal"])
            edited.update(edits)
            edited["request_id"]=f"DEMO-{uuid.uuid4().hex[:12].upper()}"
            edited["expires_at_utc"]=(utc_now()+timedelta(minutes=10)).isoformat()
            try:
                typed=OrderProposal.model_validate(edited)
            except Exception as e:
                return {"status":"REJECTED","trace":s["trace"]+["EDIT_VALIDATION_FAILED"]}
            return {"proposal":typed.model_dump(mode="json"),"payload_hash":payload_hash(typed),
                    "status":"EDITED_REQUIRES_NEW_APPROVAL","reviewer_action":"edit",
                    "edit_count":int(s.get("edit_count",0))+1,
                    "trace":s["trace"]+["HUMAN_EDIT_INVALIDATED_PREVIOUS_HASH"]}
        if decision!="approve" or reply.get("payload_hash")!=s["payload_hash"]:
            return {"status":"REJECTED","trace":s["trace"]+["APPROVAL_HASH_MISMATCH"]}
        order=OrderProposal.model_validate(s["proposal"])
        # Demo human response isn't authenticated. Backend only trusts this graph node for issuing a token.
        token=broker.approve(order, reviewer="notebook-human")
        return {"approval_token":token,"reviewer_action":"approve","status":"APPROVED",
                "trace":s["trace"]+["EXACT_PAYLOAD_APPROVED"]}

    def execution_agent(s:TradeState):
        if not research_context or research_context.get('validated_c2') is not True:
            return {'status':'BLOCKED','trace':s.get('trace',[])+['C2_RESEARCH_REQUIRED_BEFORE_EXECUTION']}
        order=OrderProposal.model_validate(s["proposal"])
        # Fail closed without an explicit quote snapshot; never fabricate a fresh quote at execution.
        if context["quote_price"] is None or context["quote_time"] is None:
            return {"status":"BLOCKED_NO_FRESH_QUOTE", "trace":s["trace"]+["MISSING_VERIFIED_SIMULATED_QUOTE"]}
        qprice = context["quote_price"]
        qtime = context["quote_time"]
        try:
            result=broker.submit(order,s["approval_token"],float(qprice),str(qtime),risk_inputs,policy,
                                 simulate_timeout_after_commit=context["inject_timeout"])
        except TimeoutError:
            reconciled=broker.reconcile(order.request_id)
            return {"execution":reconciled,"status":"RECOVERED_FROM_TIMEOUT" if reconciled["status"]=="ACCEPTED_SIMULATED" else "UNRESOLVED",
                    "trace":s["trace"]+["BROKER_TIMEOUT_RECONCILED"]}
        return {"execution":result,"status":result["status"],"trace":s["trace"]+["SIMULATED_ORDER_RESULT"]}

    def after_strategy(s:TradeState):
        return "propose" if s.get("status")=="STRATEGY_SELECTED" else END
    def after_critic(s:TradeState):
        return "approval" if s.get("status")=="CRITIC_PASSED" else END
    def after_approval(s:TradeState):
        if s.get("status")=="APPROVED":return "execute"
        if s.get("status")=="EDITED_REQUIRES_NEW_APPROVAL":return "risk"
        return END

    g=StateGraph(TradeState)
    for name,fn in (("plan",supervisor_plan),("market",market_agent),("strategy",strategy_agent),
                    ("propose",proposal_agent),("risk",risk_agent),("critic",critic_agent),
                    ("approval",approval_gate),("execute",execution_agent)):
        g.add_node(name,fn)
    g.add_edge(START,"plan")
    g.add_edge("plan","market")
    g.add_edge("market","strategy")
    g.add_conditional_edges("strategy",after_strategy,{"propose":"propose",END:END})
    g.add_edge("propose","risk")
    g.add_edge("risk","critic")
    g.add_conditional_edges("critic",after_critic,{"approval":"approval",END:END})
    g.add_conditional_edges("approval",after_approval,{"execute":"execute","risk":"risk",END:END})
    g.add_edge("execute",END)
    return g.compile(checkpointer=checkpointer)
