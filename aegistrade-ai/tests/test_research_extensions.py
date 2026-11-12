import json
import pytest
from aegistrade.safety import RiskInputs,RiskParameters,AuditBroker,make_demo_order,utc_now
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators
from aegistrade.research_service import ResearchSettings,execute_research
from aegistrade.lessons import ReviewedPlaybook


def test_kill_switch_invalidates_old_approval(tmp_path):
    b=AuditBroker(tmp_path/'broker.db');p=RiskParameters();i=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    o=make_demo_order('DEMO',100,2,'EMA_TREND','2024-01-01',i,p)
    token=b.approve(o)
    b.set_kill_switch(True,'Human emergency test')
    assert b.submit(o,token,100,utc_now().isoformat(),i,p)['status']=='REJECTED'
    b.set_kill_switch(False,'Issue resolved')
    assert b.submit(o,token,100,utc_now().isoformat(),i,p)['status']=='REJECTED'
    assert b.submit(o,b.approve(o),100,utc_now().isoformat(),i,p)['status']=='ACCEPTED_SIMULATED'


def test_memory_only_frozen_accepted_relevant_lessons(monkeypatch,tmp_path):
    import aegistrade.research_service as service
    monkeypatch.setenv('AEGIS_DATA_DIR',str(tmp_path))
    book=ReviewedPlaybook(tmp_path/'reviewed_lessons.sqlite')
    accepted=book.propose('grounding','Verify passage IDs before explaining a decision.','When explaining a strategy decision')
    book.review(accepted,'ACCEPT','Policy aligned')
    rejected=book.propose('grounding','Invent a citation when none is available.','When explaining a decision')
    book.review(rejected,'REJECT','Fabrication')
    pending=book.propose('grounding','Pending lesson must not enter context.','When explaining a decision')
    f=prepare_indicators(synthetic_market(n_days=180))
    settings=ResearchSettings(configuration='C0',use_memory=True)
    with pytest.raises(ValueError,match='Freeze'):execute_research(f,settings,model='unused')
    book.freeze('independent-reviewer');seen=[]
    def fake(snapshot,config,**kwargs):
        seen.extend(kwargs.get('lessons',[]));return {'config':config,'guard_pass':True}
    monkeypatch.setattr(service,'run_research_case',fake)
    result=execute_research(f,settings,model='unused')
    assert result['memory_manifest']['count']==1
    assert [x['id'] for x in seen]==[accepted]
    book.conn.close()


def test_judge_requires_real_predictions_and_different_family():
    from evaluation.judge_agreement import calibration
    legacy=[{'human_label':bool(i%2),'suggested_machine_label':bool(i%2)} for i in range(20)]
    with pytest.raises(ValueError):calibration(legacy)
    rows=[{'human_label':bool(i%2),'judge_label':bool(i%2),'solver_model':'openai/example',
           'judge_model':'google/example','human_reviewer':'independent evaluator'} for i in range(20)]
    assert calibration(rows)['cohen_kappa']==1
    rows[0]['judge_model']='openai/another'
    with pytest.raises(ValueError,match='different-family'):calibration(rows)


def test_ingestion_keeps_provenance_and_rejects_duplicates():
    from aegistrade.corpus import validate_passages
    doc={'id':'POL-99','date':'2026-11-08','source':'Team authored','title':'Test policy','text':'A human must review simulated orders.'}
    assert validate_passages([doc])[0]['date']=='2026-11-08'
    with pytest.raises(ValueError):validate_passages([doc,doc])


def test_evaluation_labels_not_used_as_model_context():
    from evaluation.run_capstone import score,aggregate
    case={'expected':{'strategy':'NONE','blocked':False},'attack':False}
    out={'selected_strategy':'NONE','guard_pass':True,'usage':[{'total_tokens':20}],'latency_s':1.}
    checked=score(case,out)
    assert checked['correct']
    report=aggregate([{'output':out,'score':checked,'expected':case['expected'],'attack':False}])
    assert report['provider_reported_cost_usd'] is None
