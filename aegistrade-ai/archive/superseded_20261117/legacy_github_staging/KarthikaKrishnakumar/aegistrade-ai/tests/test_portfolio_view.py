from copy import deepcopy
import pytest
from app.portfolio_view import restore_flow,remember_result


def job(flow,id):return {'run_id':id,'research_flow':flow,'model_usage':{}}


def test_switching_flows_restores_matching_result_and_never_starts_jobs():
    technical={'run_id':'technical'};s={'simulation_result':technical};reads=[]
    c1=job('C1','one');c2=job('C2','two')
    def fetch(path):
        reads.append(path)
        if path.endswith('/recent'):
            return {'runs':[{'run_id':'two','settings':{}},{'run_id':'one','settings':{'research_flow':'C1'}}]}
        return c1 if path.endswith('/one') else c2
    assert restore_flow(s,'C1',fetch)==c1
    assert restore_flow(s,'C2',fetch)==c2
    assert restore_flow(s,'TECHNICAL',fetch)==technical
    before=len(reads)
    assert restore_flow(s,'C1',fetch)==c1 and len(reads)==before+1
    assert not any('/run' in p or '/resume' in p for p in reads)
    remember_result(s,{**c1,'status':'PAUSED_BUDGET'})
    assert s['portfolio_results']['C2']==c2


def test_no_matching_saved_flow_never_displays_the_other_flow():
    s={'simulation_result':job('C2','two')}
    assert restore_flow(s,'C1',lambda _: {'runs':[{'run_id':'two','settings':{}}]}) is None
    assert 'simulation_result' not in s and 'C2' in s['portfolio_results']


def test_mismatched_status_flow_is_rejected():
    def fetch(path):
        return {'runs':[{'run_id':'one','settings':{'research_flow':'C1'}}]} if path.endswith('/recent') else job('C2','one')
    with pytest.raises(ValueError):restore_flow({},'C1',fetch)


def test_new_session_can_suppress_automatic_saved_run_restore():
    reads=[]
    result=restore_flow({},'C2',lambda path:reads.append(path) or {'runs':[]},auto_restore_saved=False)
    assert result is None and reads==[]
