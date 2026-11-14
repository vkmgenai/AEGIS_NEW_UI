from fastapi.testclient import TestClient


def test_grounded_c2_buy_review_is_authenticated_and_audited(monkeypatch,tmp_path):
    import app.api as api
    import aegistrade.research_gate as gate
    monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_broker',None)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','human-review-test-token')
    run_id='a'*32;case_id='DEMO-2024-01-02'
    monkeypatch.setattr(api,'research_experiments_result',lambda _: {'outputs':[{'config':'C2','case_id':case_id,'research_purpose':'ENTRY'}]})
    monkeypatch.setattr(gate,'validate_completed_c2',lambda output,purpose='ENTRY':{
        'portfolio_action':'ENTER','symbol':'DEMO','date':'2024-01-02','strategy':'BREAKOUT',
        'result_digest':'result-sha','company_pack_sha256':'company-sha'})
    client=TestClient(api.app);body={'run_id':run_id,'case_id':case_id,'decision':'APPROVE','rationale':'Evidence and critic checks passed.','reviewer':'KK'}
    assert client.post('/research/experiments/review',json=body).status_code==403
    response=client.post('/research/experiments/review',json=body,headers={'x-reviewer-token':'human-review-test-token'})
    assert response.status_code==200,response.text
    assert response.json()['action']=='BUY' and response.json()['decision']=='APPROVE'
    reviews=client.get('/research/experiments/reviews').json()['reviews']
    assert reviews[-1]['result_digest']=='result-sha'
    assert any(event['event']=='HUMAN_APPROVE_BUY' for event in client.get('/audit/events').json())


def test_hold_c2_result_does_not_request_human_approval(monkeypatch,tmp_path):
    import app.api as api
    import aegistrade.research_gate as gate
    monkeypatch.setattr(api,'DATA',tmp_path);monkeypatch.setattr(api,'_broker',None)
    monkeypatch.setenv('AEGIS_REVIEWER_TOKEN','human-review-test-token')
    monkeypatch.setattr(api,'research_experiments_result',lambda _: {'outputs':[{'config':'C2','case_id':'DEMO-2024-01-02','research_purpose':'HOLDING_REVIEW'}]})
    monkeypatch.setattr(gate,'validate_completed_c2',lambda output,purpose='ENTRY':{
        'portfolio_action':'HOLD','symbol':'DEMO','date':'2024-01-02','strategy':'EMA_TREND',
        'result_digest':'result-sha','company_pack_sha256':'company-sha'})
    response=TestClient(api.app).post('/research/experiments/review',json={'run_id':'a'*32,'case_id':'DEMO-2024-01-02',
        'decision':'APPROVE','rationale':'No position change is required.','reviewer':'KK'},headers={'x-reviewer-token':'human-review-test-token'})
    assert response.status_code==422 and 'HOLD' in response.json()['detail']
