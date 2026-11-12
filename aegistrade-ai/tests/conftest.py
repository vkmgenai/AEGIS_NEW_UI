import pytest

@pytest.fixture
def completed_c2():
    """Explicit synthetic completed-research record; never a real provider result."""
    def make(snapshot):
        from tests.company_fixtures import pack_for,assessment
        pack=pack_for(snapshot);company=assessment(pack)
        market={'regime':snapshot['regime'],'explanation':'Test-only market evidence interpretation.','company':company}
        strategy={'strategy':snapshot['approved_candidate'],'citations':['POL-06'],
                  'explanation':'Contract-test research explanation; no provider request.'}
        critic={'accept':True,'reason':'Test-only accepted research review.'}
        from aegistrade.corpus import corpus_info
        return {'corpus_sha256':corpus_info()['sha256'],'config':'C2','snapshot':snapshot,'selected_strategy':strategy['strategy'],'market_regime':market['regime'],
            'guard_pass':True,'critic_accept':True,'model_errors':[],'citations':strategy['citations'],
            'explanation':strategy['explanation'],'llm_calls':6,'company_research':pack,'company_assessment':company,
            'handoffs':{role:{'agent':role,'payload':payload,'evidence_tools':tools} for role,payload,tools in
                [('market',market,['market_snapshot','company_evidence']),('strategy',strategy,['search_policy','check_strategy']),
                 ('critic',critic,['search_policy','check_strategy','company_evidence'])]},
            'tool_trace':[{'tool':'search_policy','observation':{'ok':True,'results':[{'id':'POL-06'}]}},
                          *[{'agent':role,'tool':'company_evidence','observation':pack} for role in ('market','critic')]]}
    return make

@pytest.fixture
def researched_context(completed_c2):
    def make(row):
        from aegistrade.research_gate import validate_completed_c2
        snapshot={'symbol':row.Symbol,'date':str(row.Date.date()),'regime':row.Regime,'approved_candidate':row.RoutedStrategy,
                  **{k:float(getattr(row,k)) for k in ('Close','RSI14','ADX14','EMA20','EMA50','ATR14')}}
        return validate_completed_c2(completed_c2(snapshot))
    return make


@pytest.fixture(autouse=True)
def isolate_runtime_market_configuration(monkeypatch,tmp_path):
    """Tests must not depend on or mutate the user's active downloaded dataset."""
    import sys
    monkeypatch.setenv('AEGIS_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('AEGIS_LLM_BACKEND','openrouter')
    monkeypatch.delenv('AEGIS_LLM_MODEL',raising=False)
    monkeypatch.setenv('AEGIS_DATA_SOURCE','synthetic')
    monkeypatch.setenv('AEGIS_RETRIEVAL_MODE','offline')
    monkeypatch.setenv('AEGIS_NSE_DATASET_DIR',str(tmp_path/'nse_nifty20'))
    if 'app.api' in sys.modules:
        from pathlib import Path
        api=sys.modules['app.api']
        monkeypatch.setattr(api,'DATA',tmp_path)
        for name in ('_frame','_broker','_runs_db','_checkpointer','_lessons'):
            monkeypatch.setattr(api,name,None)
