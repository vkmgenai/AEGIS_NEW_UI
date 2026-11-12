"""Regression tests for lost financial headings/news bodies and attachment caching."""
import hashlib,json
from pathlib import Path
from io import BytesIO
from pypdf import PdfWriter
from aegistrade.company_excerpts import financial_excerpt,announcement_excerpt,VERSION
from aegistrade.company_research import NSEArchive,prepare_company_research,read_company_research,pack_path,upgrade_evidence_view,_persist_pack
from tests.company_fixtures import FakeArchive


def test_results_narrative_preserves_basis_period_units_and_risks():
    source='Cover letter\nTata Motors Consolidated Q2 FY24 Results\nQuarter ended September 30, 2023\nRevenue ₹105.1K Cr\nNet Profit ₹3.8K Cr\nOutlook: demand risks remain.\n'
    result=financial_excerpt(source)
    for value in ['Consolidated','September 30, 2023','₹105.1K Cr','₹3.8K Cr','demand risks']:assert value in result
    assert len(result)<=2400


def test_bank_table_is_selected_before_subsidiary_auditor_paragraph():
    source='Axis Bank Limited\n(₹ in crores)\nUNAUDITED STANDALONE FINANCIAL RESULTS\nFOR THE QUARTER ENDED September 30, 2023\nInterest earned 25,000.00\nTOTAL INCOME 30,000.00\nNet Profit 5,000.00\n'+'Other notes.\n'*250+'Subsidiary interim results reflect net profit of Rs. 17.00 lacs.'
    result=financial_excerpt(source)
    for value in ['STANDALONE','₹ in crores','September 30, 2023','Interest earned','Net Profit 5,000.00']:assert value in result
    assert '17.00 lacs' not in result


def test_attached_announcement_preserves_actual_transaction_not_stationery():
    source='Corporate Office: Example address\nWe enclose an announcement.\nEncl.: As above\nDecember 1, 2023\nSub: Acquisition of further stake\nPromoter acquired 1.35% through block deals for INR 8,301.73 Crores.\nRelated promoter holdings are disclosed below.\n'
    result=announcement_excerpt(source)
    assert '1.35%' in result and 'INR 8,301.73' in result and 'Related promoter' in result
    assert 'We enclose' not in result


def test_view_upgrade_archives_old_pack_and_changes_digest():
    p=prepare_company_research('TCS','2026-10-23',provider=FakeArchive());path=pack_path('TCS','2026-10-23')
    raw=json.loads(path.read_text());raw.pop('evidence_view_version');_persist_pack(path,raw)
    old=read_company_research('TCS','2026-10-23');source_texts=[d['text'] for d in raw['documents']]
    assert upgrade_evidence_view('TCS','2026-10-23')
    new=read_company_research('TCS','2026-10-23')
    assert new['evidence_view_version']==VERSION and new['pack_sha256']!=old['pack_sha256']
    assert source_texts==[d['text'] for d in json.loads(path.read_text())['documents']]
    assert not upgrade_evidence_view('TCS','2026-10-23')


def test_attachment_cache_reuses_validated_source_text_without_network(monkeypatch):
    from aegistrade.company_research import store_root
    url='https://nsearchives.nseindia.com/corporate/TEST_RESULTS.pdf';text='Exact cached public source text.'
    path=store_root()/'attachments'/(hashlib.sha256(url.encode()).hexdigest()+'.json');path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'source_url':url,'extraction_version':'pypdf-first35-v1','text':text,
        'archive_sha256':'a'*64,'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'retrieved_at':'2026-11-10T10:00:00+00:00'}))
    source=NSEArchive.__new__(NSEArchive);source.refresh=False
    class NoNetwork:
        def get(self,*a,**kw):raise AssertionError('Valid cached attachment must avoid network')
    source.session=NoNetwork()
    assert source.pdf_text(url)==(text,'a'*64)
    assert source.last_pdf_retrieved_at=='2026-11-10T10:00:00+00:00'


def test_compact_view_keeps_financial_context_and_lists_omissions():
    from types import SimpleNamespace
    from datetime import datetime,timezone
    from aegistrade.company_excerpts import compact_documents
    def doc(i,kind,text,status='readable',title='Quarterly financial results'):
        return SimpleNamespace(id=i,kind=kind,title=title,text=text,extraction_status=status,
            available_at=datetime(2023,11,1,tzinfo=timezone.utc),published_at=datetime(2023,11,1,tzinfo=timezone.utc),
            source_url='https://nsearchives.nseindia.com/corporate/'+i+'.pdf')
    documents=[doc('RESULT','financial_results','Consolidated Q2 results, quarter ended September 30, 2023.\nRevenue INR 100 crore\nNet profit INR 20 crore'),
        doc('NOTICE','financial_results','Conference call invitation'),doc('ANNUAL','annual_report','','unreadable')]
    visible,omitted=compact_documents(documents,lambda text:'Net profit' in text)
    assert [d['id'] for d in visible]==['RESULT']
    assert {d['id'] for d in omitted}=={'NOTICE','ANNUAL'}
    assert 'INR 100 crore' in visible[0]['excerpt'] and 'Consolidated' in visible[0]['excerpt']
