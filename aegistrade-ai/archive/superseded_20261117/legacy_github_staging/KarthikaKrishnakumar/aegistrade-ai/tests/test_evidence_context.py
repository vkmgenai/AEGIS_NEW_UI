"""Lossless cross-tool company context packing and fail-closed size limits."""
from copy import deepcopy
import pytest
from aegistrade.evidence_context import (CompanyEvidenceConversation,projection_patch,
    apply_projection_patch,model_observation,compact_json)
from aegistrade.company_research import digest


@pytest.mark.parametrize('before,after',[
    ({'a/b':{'x~y':None},'gone':7},{'a/b':{'x~y':'Unknown risk'},'new':[1,2]}),
    ({'items':[{'id':'A','risk':'UNKNOWN'},2,3]},{'items':[{'id':'B','risk':'MATERIAL_ADVERSE'}]}),
    ({'items':[1]},{'items':[2,3,4]}),
    ({'value':'Issuer reports Nil'},{'value':None}),
    ([1,2],{'now':'a dictionary'}),
])
def test_projection_update_reconstructs_exactly_without_mutating_base(before,after):
    original=deepcopy(before);patch=projection_patch(before,after)
    assert apply_projection_patch(before,patch)==after
    assert before==original


def pack():
    return {'ok':True,'symbol':'TCS','decision_at':'2024-01-03T15:30:00+05:30','status':'SUFFICIENT',
        'pack_sha256':'a'*64,'limitations':['Bounded sources, not exhaustive press coverage.'],
        'adverse_scan':{'ready':True,'citation_id':'SCAN-A','matched_document_ids':[]},
        'documents':[{'id':f'CMP-{i}','kind':'news','title':'Dated source '+str(i),
            'available_at':'2023-12-29T10:00:00+05:30','excerpt':('Exact source text '+str(i)+'; ')*65} for i in range(13)]}


def decode(base,rendered):
    update=rendered['company_evidence_update']
    assert digest(base)==update['base_projection_sha256']
    out=apply_projection_patch(base,update['patch'])
    assert digest(out)==update['projection_sha256']
    return out


def test_same_pack_from_web_uses_reference_and_preserves_all_13_documents():
    source=pack();original=deepcopy(source);conversation=CompanyEvidenceConversation()
    first=conversation.render('company_evidence',source,'company-1')
    web={'ok':True,'company_evidence':source,'search_audit':{'status':'SEARCHED_BUT_INSUFFICIENT'},'cached':True}
    second=conversation.render('search_dated_web',web,'web-1')
    assert second['company_evidence']['company_evidence_update']['patch']==[]
    assert decode(first,second['company_evidence'])==first
    assert len(compact_json(second))<1000
    assert 4800+len(compact_json(first))+len(compact_json(second))<36000
    assert source==original and len(first['documents'])==13


def test_enrichment_keeps_every_changed_financial_fact_and_adverse_risk():
    conversation=CompanyEvidenceConversation();source=pack()
    first=conversation.render('company_evidence',source,'company-1')
    enriched=deepcopy(source);enriched['pack_sha256']='b'*64
    enriched['documents'][0]['excerpt']='Issuer reports INR 8 crore exposure. Impact UNKNOWN.'
    enriched['documents'].append({'id':'WEB-1','kind':'news','excerpt':'Operating restriction remains unresolved.'})
    enriched['web_scan']={'ready':False,'citation_id':'WEBSCAN-1','status':'SEARCHED_BUT_INSUFFICIENT'}
    result=conversation.render('company_evidence',enriched,'company-2')
    assert decode(first,result)==model_observation('company_evidence',enriched)
    patch_text=compact_json(result)
    assert 'INR 8 crore' in patch_text and 'Operating restriction' in patch_text and 'UNKNOWN' in patch_text
    # A third observation refers to the second reconstructed projection, not a discarded state.
    third=conversation.render('company_evidence',enriched,'company-3')
    assert third['company_evidence_update']['base_tool_call_id']=='company-2'
    assert decode(model_observation('company_evidence',enriched),third)==model_observation('company_evidence',enriched)


def test_each_specialist_gets_its_own_complete_first_company_projection():
    source=pack()
    first=CompanyEvidenceConversation().render('company_evidence',source,'market-company')
    critic=CompanyEvidenceConversation().render('company_evidence',source,'critic-company')
    assert first==critic==model_observation('company_evidence',source)
    assert 'company_evidence_update' not in critic


def test_large_new_projection_is_never_truncated_to_force_a_fit():
    conversation=CompanyEvidenceConversation();conversation.render('company_evidence',pack(),'first')
    replacement=pack();replacement['documents']=[{'id':'NEW','excerpt':'UNRESOLVED RISK. '*4000}]
    result=conversation.render('company_evidence',replacement,'second')
    if 'company_evidence_update' in result:result=decode(model_observation('company_evidence',pack()),result)
    assert result==model_observation('company_evidence',replacement)
    assert len(result['documents'][0]['excerpt'])==len(replacement['documents'][0]['excerpt'])


def test_genuinely_oversize_context_stops_before_the_next_model_call(monkeypatch):
    from aegistrade.agentic import run_agentic_case,CONFIG
    from aegistrade.llm_research import RouterClient
    from tests.test_agentic import LocalTools,SNAPSHOT,fake_team
    class OversizeTools(LocalTools):
        async def call(self,name,args):
            out=await super().call(name,args)
            if name=='market_snapshot':out['diagnostic_padding']=['x'*12001]*3
            return out
    monkeypatch.setattr(RouterClient,'chat',fake_team)
    result=run_agentic_case(SNAPSHOT,tools_factory=OversizeTools)
    assert result['failure']['code']=='CONTEXT_BUDGET_EXCEEDED'
    assert result['failure']['observed_characters']>result['failure']['limit']==CONFIG['max_context_chars']
    assert result['llm_calls']==1 and not result['guard_pass']
    saved=next(t['observation'] for t in result['tool_trace'] if t['tool']=='market_snapshot')
    assert sum(map(len,saved['diagnostic_padding']))==36003
