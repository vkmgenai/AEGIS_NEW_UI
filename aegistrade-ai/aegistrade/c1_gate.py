"""Single-agent provenance checks; never presents C1 as independently critiqued C2."""
from .agent_tools import CaseEvidence,approved_route
from .llm_research import SingleJudgement
from .corpus import corpus_info,load_corpus
from .company_research import validate_current_company_pack,validate_company_assessment,digest


def validate_completed_c1(output,*,purpose='COMPANY_SCREEN'):
    if output.get('config')!='C1' or output.get('guard_pass') is not True or output.get('model_errors'):
        raise ValueError('Passing single-agent C1 research is required')
    if output.get('corpus_sha256')!=corpus_info()['sha256']:raise ValueError('C1 policy corpus changed')
    handoff=output.get('handoffs',{}).get('single',{})
    required={'market_snapshot','company_evidence','search_policy','check_strategy'}
    tools=set(handoff.get('evidence_tools',[]))
    if handoff.get('agent')!='single' or not required.issubset(tools) or not tools.issubset(required|{'search_dated_web'}):raise ValueError('C1 evidence tools are incomplete')
    decision=SingleJudgement.model_validate(handoff.get('payload',{}))
    snapshot=output['snapshot'];e=CaseEvidence.from_snapshot(snapshot)
    if e.research_purpose!=purpose or purpose not in {'COMPANY_SCREEN','HOLDING_REVIEW'}:raise ValueError('C1 portfolio research purpose mismatch')
    permitted={'SCREEN'} if purpose=='COMPANY_SCREEN' else {'HOLD','EXIT'}
    if decision.portfolio_action not in permitted or output.get('portfolio_action')!=decision.portfolio_action:raise ValueError('C1 action mismatch')
    if decision.strategy!=approved_route(e.regime) or decision.strategy!=snapshot['approved_candidate'] or decision.strategy!=output.get('selected_strategy'):raise ValueError('C1 route changed')
    if output.get('citations')!=decision.citations or output.get('company_assessment')!=decision.company.model_dump():raise ValueError('C1 hand-off changed')
    observed={d['id'] for t in output.get('tool_trace',[]) if t.get('tool')=='search_policy' and t.get('observation',{}).get('ok') for d in t['observation'].get('results',[])}
    policy={d['id'] for d in load_corpus() if d['authority']=='project_policy'}
    if not set(decision.citations).issubset(observed) or not policy.intersection(decision.citations):raise ValueError('C1 policy citations were not retrieved')
    pack=validate_current_company_pack(output.get('company_research',{}),allow_partial=True)
    if pack['symbol']!=e.symbol or pack['decision_at'][:10]!=e.date:raise ValueError('C1 company evidence belongs to a different date or symbol')
    validate_company_assessment(decision.company,pack,snapshot=snapshot,portfolio_action=decision.portfolio_action,
                               allow_review_required=purpose=='HOLDING_REVIEW' and decision.portfolio_action=='EXIT')
    seen=any(t.get('agent')=='single' and t.get('tool') in {'company_evidence','search_dated_web'} and digest(t.get('observation',{}).get('company_evidence',t.get('observation',{})))==digest(pack) for t in output.get('tool_trace',[]))
    if not seen:raise ValueError('C1 agent did not observe this company evidence')
    return {'validated_c1':True,'portfolio_action':decision.portfolio_action,'strategy':decision.strategy,
            'company_assessment':decision.company.model_dump(),'independent_critic':False}


def validate_smc_order(order,output,frame,policy):
    from .execution_policy import initial_stop_price
    from .agent_tools import SMCContext
    screen=validate_completed_c1(output,purpose='COMPANY_SCREEN')
    snapshot=output['snapshot']
    rows=frame[(frame.Symbol==order['symbol'])&(frame.Date.dt.strftime('%Y-%m-%d')==order['signal_date'])]
    if len(rows)!=1 or snapshot['date']!=order['signal_date'] or snapshot['symbol']!=order['symbol'] or order['strategy']!='SMC':raise ValueError('SMC order and dated screen differ')
    row=rows.iloc[0]
    if not bool(row.SMCSignal) or order.get('smc_context')!=row.SMCContext:raise ValueError('SMC setup proof changed')
    SMCContext.model_validate(order['smc_context'])
    if abs(order['stop']-initial_stop_price(row.Close,row.ATR14,policy))>1e-8:raise ValueError('SMC stop changed')
    return screen
