"""Reusable public-source catalogue contracts; no downloads or OCR in unit tests."""
from datetime import date
import json
import pytest
from aegistrade.evidence_library import atomic,archive_path,cached_announcements,fetch_archive,read_archive,prefetch_documents,VERSION
from aegistrade.company_research import digest,NSEArchive


def row(day='15-Jan-2024',kind='Financial Results',url='https://nsearchives.nseindia.com/corporate/DEMO.pdf'):
    return {'symbol':'DEMO','an_dt':day+' 10:00:00','desc':kind,'attchmntText':'Synthetic contract-test disclosure', 'attchmntFile':url}


def write(rows,windows):
    value={'version':VERSION,'symbol':'DEMO','rows':rows,'windows':windows}
    value['payload_sha256']=digest({'rows':rows,'windows':windows});atomic(archive_path('DEMO'),value)
    return value


def window(a='2024-01-01',b='2024-01-31',complete=True):return {'start':a,'end':b,'complete':complete}


def test_cache_requires_full_successful_coverage_and_filters_dates():
    write([row(),row('25-Jan-2024')],[window()])
    assert len(cached_announcements('DEMO',date(2024,1,1),date(2024,1,20)))==1
    write([row()],[window(b='2024-01-14'),window(a='2024-01-16')])
    assert cached_announcements('DEMO',date(2024,1,1),date(2024,1,31)) is None
    write([row()],[window(complete=False)])
    assert cached_announcements('DEMO',date(2024,1,1),date(2024,1,31)) is None


def test_cache_checksum_and_invalid_timestamps_do_not_create_clean_scans():
    value=write([row(),{**row(),'an_dt':'unknown'}],[window()])
    assert len(cached_announcements('DEMO',date(2024,1,1),date(2024,1,20)))==2
    value['rows'][0]['an_dt']='01-Jan-2020 10:00:00';atomic(archive_path('DEMO'),value)
    assert read_archive('DEMO') is None


def test_nse_provider_uses_verified_catalogue_without_network():
    write([row()],[window()])
    p=NSEArchive.__new__(NSEArchive)
    p._network_announcements=lambda *a:pytest.fail('Covered historical dates must not refetch metadata')
    assert p.announcements('DEMO',date(2024,1,1),date(2024,1,31))==[row()]


def test_truncated_window_is_split_and_failed_windows_are_not_certified():
    class Archive:
        def _network_announcements(self,symbol,left,right):
            if (right-left).days>10:raise ValueError('Unverified/truncated NSE announcement response')
            return []
    raw=fetch_archive('DEMO',date(2024,1,1),date(2024,1,31),Archive())
    assert raw and cached_announcements('DEMO',date(2024,1,1),date(2024,1,31))==[]
    class Failed:
        def _network_announcements(self,*a):raise RuntimeError('Public source unavailable')
    raw=fetch_archive('DEMO',date(2024,2,1),date(2024,2,29),Failed())
    assert any(not w['complete'] for w in raw['windows'])
    assert cached_announcements('DEMO',date(2024,2,1),date(2024,2,29)) is None


def test_out_of_range_api_rows_remain_a_coverage_gap():
    class Archive:
        def _network_announcements(self,*a):return [row('15-Feb-2024')]
    raw=fetch_archive('DEMO',date(2024,1,1),date(2024,1,31),Archive())
    assert raw['windows'][0]['out_of_range_rows']==1
    assert cached_announcements('DEMO',date(2024,1,1),date(2024,1,31)) is None


def test_prefetch_uses_fallback_financial_and_retains_explicit_ocr_failures():
    rows=[row('20-Jan-2024',url='https://nsearchives.nseindia.com/corporate/A.pdf'),
          row('15-Jan-2024',url='https://nsearchives.nseindia.com/corporate/B.pdf'),row('15-Feb-2024')]
    raw=write(rows,[window()])
    class Archive:
        def pdf_text(self,url):
            return ('Issuer cover letter with no financial table. '*12 if url.endswith('A.pdf') else 'Revenue 120.00; profit 20.00; cash flow 30.00; income 150.00. '*12),'a'*64
    def failed(url):raise RuntimeError('Local OCR unavailable')
    docs=prefetch_documents(raw,date(2024,1,31),Archive(),repair_financial=failed)['documents']
    assert len(docs)==2 and docs[0]['ocr_error']=='RuntimeError' and docs[1]['financial_content']
    assert all(d['available_at'][:10]<='2024-01-31' for d in docs)


@pytest.mark.parametrize('url',['http://nsearchives.nseindia.com/a.pdf','https://example.com/a.pdf','https://127.0.0.1/a.pdf','https://nsearchives.nseindia.com/a.pdf?token=x'])
def test_ocr_refuses_nonofficial_or_ambiguous_source_urls(url):
    from aegistrade.financial_ocr import repair_pdf
    with pytest.raises(ValueError):repair_pdf(url)


def test_library_status_reads_saved_report_without_network():
    from aegistrade.evidence_library import library_status
    from aegistrade.company_research import store_root
    assert library_status()['state']=='NOT_PREPARED'
    atomic(store_root()/'backfill_all_metadata.json',{'completed_symbols':1,'total_symbols':103,'updated_utc':'2026-11-13'})
    assert library_status()['state']=='PREPARING'
    atomic(store_root()/'library_status.json',{'unique_stocks':103,'totals':{},'stocks':[]})
    assert library_status()['report']['unique_stocks']==103


def test_dated_company_pack_from_library_excludes_after_close_disclosures():
    from datetime import timedelta
    from aegistrade.company_research import prepare_company_research
    cutoff=date(2024,1,15);start=cutoff-timedelta(days=180)
    old=row('14-Jan-2024',url='https://nsearchives.nseindia.com/corporate/ELIGIBLE.pdf')
    future={**row('15-Jan-2024',url='https://nsearchives.nseindia.com/corporate/AFTERCLOSE.pdf'),'an_dt':'15-Jan-2024 16:00:00'}
    write([old,future],[window(str(start),str(cutoff))])
    class Cached(NSEArchive):
        def __init__(self):pass
        def _network_announcements(self,*a):pytest.fail('Complete library must serve the dated pack offline')
        def pdf_text(self,url):
            assert url.endswith('ELIGIBLE.pdf')
            return 'Revenue 120.00 profit 20.00 cash flow 30.00 income 150.00. '*12,'a'*64
    pack=prepare_company_research('DEMO',str(cutoff),provider=Cached())
    assert pack['status']=='SUFFICIENT'
    assert all(d['source_url'].endswith('ELIGIBLE.pdf') for d in pack['documents'])


def test_verified_alias_empty_old_index_uses_current_symbol_history(monkeypatch):
    import aegistrade.security_identity as identity
    from types import SimpleNamespace
    calls=[]
    monkeypatch.setattr(identity,'segments',lambda symbol,start,end,**kw:[('OLD',start,end)])
    p=NSEArchive.__new__(NSEArchive);p._session_initialized=True
    class Session:
        def get(self,url,params=None,**kw):
            calls.append(params['symbol']);rows=[] if params['symbol']=='OLD' else [row()]
            return SimpleNamespace(raise_for_status=lambda:None,json=lambda:rows)
    p.session=Session()
    result=p._network_announcements('DEMO',date(2024,1,1),date(2024,1,31))
    assert calls==['OLD','DEMO'] and result[0]['symbol']=='DEMO'
    assert 'current-symbol historical archive index' in result[0]['identifier_normalization']


def test_transcripts_do_not_displace_actual_financial_statements():
    from aegistrade.company_research import classify
    assert classify('Updates — Transcript of earnings call on unaudited financial results')=='company_news'
    assert classify('Financial Result Updates — Quarterly financial results ended September 30')=='financial_results'


def test_refresh_of_unchanged_pdf_preserves_verified_ocr_text():
    import hashlib
    from types import SimpleNamespace
    from aegistrade.company_research import store_root
    url='https://nsearchives.nseindia.com/corporate/SCAN.pdf';raw=b'%PDF original scanned source bytes'
    text='MACHINE OCR SUPPLEMENT: Revenue 120.00 profit 20.00 cash flow 30.00 income 150.00. '*5
    value={'source_url':url,'extraction_version':'pypdf+apple-vision-financial-v2','text':text,'archive_sha256':hashlib.sha256(raw).hexdigest(),'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'retrieved_at':'2026-11-13T00:00:00+00:00'}
    atomic(store_root()/'attachments'/(hashlib.sha256(url.encode()).hexdigest()+'.json'),value)
    class Response:
        status_code=200
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def raise_for_status(self):pass
        def iter_content(self,*a):yield raw
    p=NSEArchive.__new__(NSEArchive);p.refresh=True;p.session=SimpleNamespace(get=lambda *a,**kw:Response())
    assert p.pdf_text(url)==(text,value['archive_sha256'])
