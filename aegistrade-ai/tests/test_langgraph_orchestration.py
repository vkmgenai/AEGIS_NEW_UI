"""Minimum-bar contracts for real LangGraph orchestration and persistence."""
from pathlib import Path

from aegistrade.agentic import c1_graph_mermaid,c2_graph_mermaid
from aegistrade.c2_portfolio import create_run,execute_run,portfolio_graph_mermaid,resume_portfolio_graph
from aegistrade.langgraph_runtime import checkpoint_path
from tests.test_c2_portfolio import history,settings,runner,prepare


def test_executable_graph_diagrams_have_required_edges():
    single=c1_graph_mermaid()
    research=c2_graph_mermaid()
    portfolio=portfolio_graph_mermaid()
    assert all(node in single for node in ('plan','single_agent'))
    assert all(node in research for node in ('market','strategy','validate_strategy','replan','critic'))
    assert all(node in portfolio for node in ('execute_sessions','human_gate','apply_human_resume'))


def test_new_portfolio_uses_sqlite_langgraph_checkpoint(completed_c2):
    frame=history(65);run_id=create_run(frame,settings(frame,review=60))
    result=execute_run(run_id,frame,researcher=runner(completed_c2),preparer=prepare)
    assert result['orchestration']=={
        'framework':'LangGraph','graph':'aegistrade-c2-portfolio',
        'thread_id':f'portfolio:{run_id}','checkpointer':'SQLite','native_human_interrupt':True}
    path=checkpoint_path()
    assert path.exists() and path.stat().st_size>0


def test_native_human_interrupt_resumes_with_command(completed_c2):
    frame=history(62);cfg=settings(frame,review=60).model_copy(update={'human_override_mode':True})
    def blocked(snapshot,*args,**kwargs):
        out=completed_c2(snapshot);out['guard_pass']=False
        out['model_errors']=['COMPANY_ASSESSMENT_BLOCKED: evidence coverage is insufficient; no concrete adverse event identified.']
        return out
    run_id=create_run(frame,cfg)
    paused=execute_run(run_id,frame,researcher=blocked,preparer=prepare)
    assert paused['status']=='PAUSED_HUMAN_OVERRIDE'
    pending=paused['pending_human_override']
    resumed=resume_portfolio_graph(run_id,frame,{'override_id':pending['override_id'],
        'decision':'APPROVE_OVERRIDE','reviewer':'KK','rationale':'Controlled LangGraph resume contract test.'})
    assert resumed['status'].startswith('COMPLETED')
    assert any(row.get('marker')=='HUMAN_EVIDENCE_OVERRIDE' for row in resumed['ledgers']['C2'])

