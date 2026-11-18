from app.backend_compat import compatible_backend,UI_API_CONTRACT


def test_patch_versions_share_an_explicit_contract():
    assert compatible_backend({'version':'0.16.0','ui_api_contract':UI_API_CONTRACT})
    assert compatible_backend({'version':'0.16.99','ui_api_contract':UI_API_CONTRACT})
    assert not compatible_backend({'version':'0.16.2','ui_api_contract':2})
    assert not compatible_backend({'version':'0.16.2','ui_api_contract':True})


def test_known_legacy_patch_versions_remain_usable():
    health={'version':'0.16.1','inference':{},'c2_required_before_order':True,'company_research_required':True}
    assert compatible_backend(health)
    assert not compatible_backend({**health,'company_research_required':False})
    assert not compatible_backend({**health,'version':'0.15.1'})
