"""Mandatory completed C2 provenance for supervised proposals; no model calls here."""
from __future__ import annotations
import hashlib,json
from .agent_tools import CaseEvidence
from .llm_research import MarketJudgement,StrategyJudgement,CriticJudgement


def evidence_digest(snapshot):
    return hashlib.sha256(json.dumps(snapshot,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def validate_completed_c2(output:dict,*,purpose='ENTRY') -> dict:
    if output.get('config')!='C2' or output.get('guard_pass') is not True or output.get('critic_accept') is not True or output.get('model_errors'):
        raise ValueError('Completed C2 research with accepted critic and passing code checks is required')
    if not output.get('corpus_sha256'):
        raise ValueError('C2 result lacks knowledge-corpus provenance; rerun current C2 research')
    if output.get('corpus_sha256'):
        from .corpus import corpus_info
        if output['corpus_sha256']!=corpus_info()['sha256']:
            raise ValueError('Knowledge corpus changed; rerun C2 before preparing or approving an order')
    handoffs=output.get('handoffs',{})
    parsed={}
    for role,schema,tools in [('market',MarketJudgement,{'market_snapshot','company_evidence'}),
                              ('strategy',StrategyJudgement,{'search_policy','check_strategy'}),
                              ('critic',CriticJudgement,{'search_policy','check_strategy','company_evidence'})]:
        h=handoffs.get(role,{})
        observed=set(h.get('evidence_tools',[]));optional={'search_dated_web'} if role in {'market','critic'} else set()
        if h.get('agent')!=role or not tools.issubset(observed) or not observed.issubset(tools|optional):
            raise ValueError('C2 specialist evidence is incomplete; run current C2 research first')
        parsed[role]=schema.model_validate(h.get('payload',{}))
    snapshot=output.get('snapshot',{})
    evidence=CaseEvidence.from_snapshot(snapshot)
    memory=output.get('portfolio_memory') or {}
    if memory.get('manifest'):
        from .portfolio_memory import validate_binding
        book=validate_binding(memory['manifest'],evidence.date)
        ids=memory.get('lesson_ids',[])
        if len(ids)>3 or len(ids)!=len(set(ids)) or not set(ids).issubset({l['id'] for l in book['lessons']}):
            raise ValueError('Portfolio lesson selection is not from the pinned reviewed version')
    if evidence.research_purpose!=purpose:raise ValueError('Research purpose does not match requested action')
    strategy=parsed['strategy']
    action=strategy.portfolio_action
    if (purpose=='ENTRY' and action!='ENTER') or (purpose=='HOLDING_REVIEW' and action not in {'HOLD','EXIT'}):raise ValueError('Invalid portfolio action')
    if output.get('portfolio_action',action)!=action:raise ValueError('Portfolio action hand-off changed')
    if (not parsed['critic'].accept or parsed['market'].regime!=evidence.regime
        or strategy.strategy!=output.get('selected_strategy') or strategy.citations!=output.get('citations')
        or strategy.strategy!=snapshot.get('approved_candidate')):
        raise ValueError('C2 hand-offs disagree with the saved result')
    retrieved={d['id'] for t in output.get('tool_trace',[]) if t.get('tool')=='search_policy'
               and t.get('observation',{}).get('ok') is True for d in t['observation'].get('results',[])}
    if not set(strategy.citations).issubset(retrieved):raise ValueError('C2 citations lack retrieved policy evidence')
    from .corpus import load_corpus
    policy_ids={d['id'] for d in load_corpus() if d['authority']=='project_policy'}
    if not policy_ids.intersection(strategy.citations):raise ValueError('A project-policy citation is required; public background alone cannot support route approval')
    from .company_research import validate_current_company_pack,validate_company_assessment,digest
    company=validate_current_company_pack(output.get('company_research',{}),allow_partial=True)
    if company['symbol']!=evidence.symbol or company['decision_at'][:10]!=evidence.date:
        raise ValueError('Company research belongs to a different case')
    validate_company_assessment(parsed['market'].company,company,allow_review_required=purpose=='HOLDING_REVIEW' and action=='EXIT',snapshot=snapshot,portfolio_action=action)
    from .breakout_evidence import validate_breakout_critic
    validate_breakout_critic(parsed['market'].company,parsed['critic'],company,snapshot)
    if output.get('company_assessment')!=parsed['market'].company.model_dump():raise ValueError('Company hand-off changed')
    seen={t['agent'] for t in output.get('tool_trace',[]) if t.get('tool') in {'company_evidence','search_dated_web'}
          and digest(t.get('observation',{}).get('company_evidence',t.get('observation',{})))==digest(company)}
    if not {'market','critic'}.issubset(seen):raise ValueError('Company evidence was not observed by market and critic')
    sources=[{k:d[k] for k in ('id','title','source_url','available_at')} for d in company['documents'] if d['id'] in parsed['market'].company.citations]
    from .company_research import effective_scan
    for scan in [company.get('adverse_scan',{}),company.get('web_scan',{})]:
        if scan.get('citation_id') in parsed['market'].company.citations:
            sources.append({'id':scan['citation_id'],'title':'Bounded research check; inspect readiness and scope, not proof of safety',
                'source_url':scan['source_url'],'available_at':scan['decision_at']})
    return {'validated_c2':True,'corpus_sha256':output['corpus_sha256'],'result_digest':evidence_digest(output),
            'snapshot':snapshot,'explanation':strategy.explanation,'citations':strategy.citations,
            'strategy':strategy.strategy,'symbol':evidence.symbol,'date':evidence.date,
            'critic_accept':True,'company_assessment':parsed['market'].company.model_dump(),
            'portfolio_action':action,'research_purpose':purpose,
            'company_pack_sha256':company['pack_sha256'],'decision_at':company['decision_at'],
            'company_sources':sources}


def human_review_candidates(outputs:list[dict]) -> list[dict]:
    """Return only C2 actions that pass the same authoritative gate used at review time.

    The annotations let the UI explain why a superficially successful result is
    not reviewable, without changing model-error accounting or making a model call.
    """
    candidates=[]
    for output in outputs:
        output.pop('human_review_gate_error',None)
        output['human_review_eligible']=False
        if output.get('config')!='C2' or output.get('portfolio_action') not in {'ENTER','EXIT'}:
            continue
        purpose=output.get('research_purpose') or output.get('snapshot',{}).get('research_purpose','ENTRY')
        try:validated=validate_completed_c2(output,purpose=purpose)
        except (ValueError,KeyError,TypeError) as exc:
            output['human_review_gate_error']=str(exc)
            continue
        output['human_review_eligible']=True
        candidates.append({'case_id':output['case_id'],'portfolio_action':validated['portfolio_action'],
                           'action':'BUY' if validated['portfolio_action']=='ENTER' else 'SELL'})
    return candidates
