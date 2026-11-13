import json
from pathlib import Path
import numpy as np
import pytest
from aegistrade.corpus import load_corpus,corpus_info,validate_passages
from aegistrade.knowledge import PolicyRetriever


def test_corpus_is_scoped_versioned_and_sources_traceable():
    docs=load_corpus();info=corpus_info()
    assert len(docs)==85 and info['project_policy_passages']==76 and info['external_reference_passages']==9
    assert len({d['id'] for d in docs})==len(docs)
    refs=[d for d in docs if d['authority']=='external_reference']
    assert all(d['source_url'].startswith('https://') and d['date_kind']=='retrieved' for d in refs)
    assert all(d.get('review_status') for d in docs)
    assert all('future_return' not in d and 'future_price' not in d for d in docs)


def test_ingestion_rejects_untraceable_or_unsafe_source_links():
    base={'id':'REF-TEST-01','date':'2026-11-09','source':'External example','title':'Background information',
          'text':'A source reference never authorizes an order.','authority':'external_reference'}
    with pytest.raises(ValueError):validate_passages([base])
    with pytest.raises(ValueError):validate_passages([{**base,'source_url':'javascript:example'}])
    assert validate_passages([{**base,'source_url':'https://example.com/reference'}])[0]['authority']=='external_reference'


def test_new_strategy_data_is_retrieved_and_unknown_content_abstains():
    r=PolicyRetriever()
    assert 'POL-27' in {x['id'] for x in r.search('RSI entry threshold 42',5)}
    assert 'POL-57' in {x['id'] for x in r.search('raw prices splits bonus demerger adjustment',5)}
    assert r.search('xyzfootball worldcup goalkeeper')==[]
    out=r.search('approval payload',5)
    assert all(x['corpus_sha256']==corpus_info()['sha256'] for x in out)


def test_retrieval_query_ids_are_unique_and_labels_are_candidates():
    rows=[json.loads(line) for line in Path('evaluation/retrieval/queries_expanded_dev.jsonl').read_text().splitlines()]
    ids={d['id'] for d in load_corpus()}
    assert len(rows)==101 and len({r['id'] for r in rows})==101
    assert all(set(r['relevant_ids'])<=ids and 'review' in r['label_origin'] for r in rows)


def test_c2_gate_binds_current_rag_corpus(completed_c2):
    from aegistrade.research_gate import validate_completed_c2
    snap={'symbol':'DEMO','date':'2024-01-01','regime':'TREND','approved_candidate':'EMA_TREND',
          'Close':100.,'RSI14':55.,'ADX14':25.,'EMA20':99.,'EMA50':95.,'ATR14':2.}
    out=completed_c2(snap);assert validate_completed_c2(out)['validated_c2']
    out['corpus_sha256']='0'*64
    with pytest.raises(ValueError,match='Knowledge corpus changed'):validate_completed_c2(out)
    out.pop('corpus_sha256')
    with pytest.raises(ValueError,match='lacks knowledge-corpus'):validate_completed_c2(out)


def test_chroma_index_round_trip_without_model_download(tmp_path):
    pytest.importorskip('chromadb')
    from aegistrade.vector_store import ChromaIndex
    docs=load_corpus()[:2];vectors=np.array([[1.,0.,0.],[0.,1.,0.]],dtype=np.float32)
    first=ChromaIndex(tmp_path,docs,vectors,'contract-test-embedding')
    assert first.scores(vectors[0])[0]>first.scores(vectors[0])[1]
    second=ChromaIndex(tmp_path,docs,vectors,'contract-test-embedding')
    assert first.name==second.name and second.collection.count()==2
    assert second.collection.get(ids=[docs[0]['id']])['documents']==[docs[0]['text']]


def test_external_reference_dates_do_not_leak_into_old_cases():
    r=PolicyRetriever()
    before=r.search('ZOMATO ETERNAL symbol notice',top_k=12,as_of='2024-01-01')
    assert all(d['authority']=='project_policy' or (d.get('published_date') or d.get('retrieved_date') or d['date'])<='2024-01-01' for d in before)
    assert 'REF-ALIAS-01' not in {d['id'] for d in before}
    after=r.search('ZOMATO ETERNAL symbol notice',top_k=5,as_of='2025-05-01')
    assert 'REF-ALIAS-01' in {d['id'] for d in after}


def test_public_background_alone_cannot_ground_route_approval(completed_c2):
    from aegistrade.research_gate import validate_completed_c2
    snap={'symbol':'DEMO','date':'2024-01-01','regime':'TREND','approved_candidate':'EMA_TREND',
          'Close':100.,'RSI14':55.,'ADX14':25.,'EMA20':99.,'EMA50':95.,'ATR14':2.}
    out=completed_c2(snap)
    out['citations']=['REF-NSE50-01'];out['handoffs']['strategy']['payload']['citations']=out['citations']
    out['tool_trace'][0]['observation']['results']=[{'id':'REF-NSE50-01'}]
    with pytest.raises(ValueError,match='project-policy citation'):validate_completed_c2(out)
