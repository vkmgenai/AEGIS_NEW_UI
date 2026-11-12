from datetime import date,datetime
import json
import pytest
from aegistrade.company_research import (cutoff_for,normalize_announcement,prepare_company_research,
    read_company_research,pack_path,import_archived_news,validate_company_assessment)
from tests.company_fixtures import FakeArchive,pack_for,assessment
from aegistrade.llm_research import CompanyAssessment,RouterClient


def test_exchange_disclosure_after_close_is_not_known():
    row={'symbol':'TCS','an_dt':'23-Oct-2026 15:29:00','exchdisstime':'23-Oct-2026 15:31:00',
         'desc':'Financial Results','attchmntFile':'https://nsearchives.nseindia.com/corporate/TEST.pdf'}
    assert normalize_announcement(row,'TCS',cutoff_for('TCS','2026-10-23')) is None
    assert normalize_announcement(row,'TCS',cutoff_for('TCS','2026-10-24'))['available_at'].endswith('+05:30')
    row['an_dt']='24-Oct-2026 10:00:00'
    assert normalize_announcement(row,'TCS',cutoff_for('TCS','2026-10-23')) is None

@pytest.mark.parametrize('url',['http://127.0.0.1/private.pdf','https://evil.example/filing.pdf','https://nsearchives.nseindia.com@evil.example/x.pdf','https://nsearchives.nseindia.com:444/x.pdf'])
def test_only_official_pdf_downloads_are_allowed(url):
    row={'symbol':'TCS','an_dt':'22-Oct-2026 10:00:00','desc':'Financial Results','attchmntFile':url}
    assert normalize_announcement(row,'TCS',cutoff_for('TCS','2026-10-23')) is None


def test_read_is_no_network_stable_and_missing_is_explicit(monkeypatch):
    missing=read_company_research('TCS','2026-10-23')
    assert missing['status']=='INSUFFICIENT_EVIDENCE' and not missing['pack_sha256']
    p=prepare_company_research('TCS','2026-10-23',provider=FakeArchive())
    monkeypatch.setattr('aegistrade.company_research.NSEArchive',lambda:pytest.fail('Cached read must not use network'))
    assert p['status']=='SUFFICIENT' and prepare_company_research('TCS','2026-10-23')==p
    assert all(d['available_at']<=p['decision_at'] for d in p['documents'])


def test_unreadable_financial_filing_blocks():
    class Scanned(FakeArchive):
        def pdf_text(self,url):return '',None
    p=prepare_company_research('TCS','2026-10-23',provider=Scanned())
    assert p['status']=='INSUFFICIENT_EVIDENCE'
    with pytest.raises(ValueError):validate_company_assessment(CompanyAssessment.model_validate(assessment({**p,'documents':p.get('omitted_documents',p['documents'])})),p)


def test_invalid_timestamp_prevents_claim_of_complete_scan():
    class Broken(FakeArchive):
        def announcements(self,*a):return [{**super().announcements(*a)[0],'exchdisstime':'unknown'}]
    p=prepare_company_research('TCS','2026-10-23',provider=Broken())
    assert p['status']=='INSUFFICIENT_EVIDENCE' and p['coverage']['invalid_timestamp_rows']>0


def test_date_only_news_is_delayed_and_requires_verified_original(tmp_path):
    prepare_company_research('TCS','2026-10-23',provider=FakeArchive())
    p=tmp_path/'news.jsonl'
    row={'symbol':'TCS','kind':'newsletter','title':'Archived test newsletter','publisher':'Test source',
         'published_at':'2026-10-23','source_url':'https://publisher.example/archive/item','text':'Synthetic licensed excerpt. '*8,
         'original_publication_verified':True}
    p.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='point-in-time'):import_archived_news('TCS','2026-10-23',p,'Test reviewer')
    row['published_at']='2026-10-22';p.write_text(json.dumps(row))
    result=import_archived_news('TCS','2026-10-23',p,'Test reviewer')
    from aegistrade.company_research import store_root
    assert len(list((store_root()/'snapshots').glob('*.json')))>=2
    news=next(d for d in result['documents'] if d['kind']=='newsletter')
    assert news['available_at']=='2026-10-23T00:00:00+05:30'
    row['original_publication_verified']=False;p.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='verified'):import_archived_news('TCS','2026-10-23',p,'Test reviewer')


def test_missing_company_evidence_blocks_before_paid_generation(monkeypatch):
    from aegistrade.research_service import ResearchSettings,execute_research
    from aegistrade.market import synthetic_market
    from aegistrade.strategies import prepare_indicators
    monkeypatch.setenv('OPENROUTER_API_KEY','TEST_ONLY');monkeypatch.setenv('AEGIS_ENABLE_LLM_EXPERIMENTS','true')
    monkeypatch.setattr('aegistrade.company_research.prepare_company_research',lambda *a,**kw:{'status':'INSUFFICIENT_EVIDENCE'})
    monkeypatch.setattr(RouterClient,'chat',lambda *a,**kw:pytest.fail('No paid calls on missing company evidence'))
    with pytest.raises(ValueError,match='no paid model call'):
        execute_research(prepare_indicators(synthetic_market(n_days=180)),ResearchSettings(configuration='C2',consent_to_paid_calls=True),model='unused')


def test_unobserved_company_citation_is_blocked(monkeypatch):
    from tests.test_agentic import fake_team,LocalTools,SNAPSHOT
    from aegistrade.agentic import run_agentic_case
    def fake(self,messages,**kw):
        m=fake_team(self,messages,**kw)
        if m.get('content') and 'Role: market ' in messages[0]['content']:
            value=json.loads(m['content']);value['company']['citations']=['CMP-NOT-OBSERVED'];m['content']=json.dumps(value)
        return m
    monkeypatch.setattr(RouterClient,'chat',fake)
    result=run_agentic_case(SNAPSHOT,tools_factory=LocalTools)
    assert not result['guard_pass'] and 'market' not in result['handoffs']
