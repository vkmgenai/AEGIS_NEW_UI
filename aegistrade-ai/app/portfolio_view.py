"""Keep displayed C1/C2/technical runs separate; restoration performs GETs only."""


def flow_of(result):
    return result.get('research_flow','C2') if result and 'model_usage' in result else 'TECHNICAL'


def remember_result(session,result):
    flow=flow_of(result)
    results=dict(session.get('portfolio_results',{}));results[flow]=result
    session['portfolio_results']=results;session['simulation_result']=result
    return result


def restore_flow(session,flow,fetch):
    legacy=session.get('simulation_result')
    if legacy:remember_result(session,legacy)
    result=session.get('portfolio_results',{}).get(flow)
    if result is not None and flow in {'C1','C2'}:
        candidate=fetch('/simulation/'+flow.lower()+'/status/'+result['run_id'])
        if flow_of(candidate)!=flow or candidate.get('run_id')!=result['run_id']:raise ValueError('Status belongs to another flow/run')
        result=remember_result(session,candidate)
    if result is None and flow in {'C1','C2'}:
        runs=fetch('/simulation/'+flow.lower()+'/recent').get('runs',[])
        matching=[r for r in runs if r.get('settings',{}).get('research_flow','C2')==flow]
        if matching:
            candidate=fetch('/simulation/'+flow.lower()+'/status/'+matching[0]['run_id'])
            if flow_of(candidate)!=flow:raise ValueError('Saved run belongs to another flow')
            result=remember_result(session,candidate)
    if result is None:session.pop('simulation_result',None)
    else:session['simulation_result']=result
    return result
