"""Point-in-time company evidence. Public NSE archive; no paid generation or browser agent.

The decision cutoff is the selected daily close (15:30 Asia/Kolkata). Documents
are immutable local snapshots; missing coverage never means a clean company.
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
import hashlib,json,os,re,uuid
import requests
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator

IST=ZoneInfo('Asia/Kolkata')
VERSION='company-research-v1'
from .company_excerpts import VERSION as EVIDENCE_VIEW_VERSION,excerpt as context_excerpt,compact_documents
RISK_SCAN_VERSION='adverse-scan-v2-routine-notices'
ADVERSE_TERMS=re.compile(r'\b(default|fraud|insolvency|bankrupt|downgrade|penalt|litigation|resign|fire|accident|cyber|seizure|recall|closure|disruption|regulatory action|material event)',re.I)


def potential_adverse(title,*,recent=False):
    # A trading window closes for insiders before routine results; it is not an operating closure.
    routine=bool(re.search(r'trading\s+window|window\s+.*(?:insider|trading)',title,re.I))
    explicit=re.search(r'fraud|default|insolven|penalt|litigation|investigat|plant\s+closure|operat.*restriction|cyber|fire\b|accident',title,re.I)
    if routine and not explicit:return False
    return bool(ADVERSE_TERMS.search(title) or (recent and re.search(r'regulation.?30|reg.?30|material|disclosure|credit.rating',title,re.I)))
MAX_PDF_BYTES=32_000_000
NSE_PAGE='https://www.nseindia.com/companies-listing/corporate-filings-announcements'
NSE_API='https://www.nseindia.com/api/corporate-announcements'
ARCHIVE_HOSTS={'nsearchives.nseindia.com','archives.nseindia.com'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def cutoff_for(symbol,day):
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9_&-]{1,29}',symbol):raise ValueError('Invalid company symbol')
    return datetime.combine(date.fromisoformat(day),time(15,30),IST)


class CompanyDocument(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:str
    symbol:str
    kind:str
    title:str=Field(min_length=3,max_length=1500)
    text:str=Field(max_length=100000)
    source_url:str
    publisher:str
    published_at:datetime
    available_at:datetime
    retrieved_at:datetime
    content_sha256:str
    archive_sha256:str|None=None
    timestamp_basis:str
    extraction_status:str

    @field_validator('published_at','available_at','retrieved_at')
    @classmethod
    def aware(cls,v):
        if v.tzinfo is None:raise ValueError('Company evidence requires timezone-aware timestamps')
        return v

    @field_validator('source_url')
    @classmethod
    def public_url(cls,v):
        u=urlparse(v)
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.port not in (None,443):
            raise ValueError('Expected a public HTTPS source URL')
        return v

    @model_validator(mode='after')
    def dates_and_content(self):
        if self.available_at<self.published_at:raise ValueError('Availability precedes publication')
        if hashlib.sha256(self.text.encode()).hexdigest()!=self.content_sha256:raise ValueError('Document text checksum mismatch')
        return self


def store_root():return Path(os.getenv('AEGIS_DATA_DIR','data'))/'company_research'
def pack_path(symbol,day):
    cutoff_for(symbol,day)
    return store_root()/'packs'/f'{symbol}_{day}.json'


def _persist_pack(path,pack):
    """Retain old/new content-addressed snapshots before atomically moving current."""
    archive=store_root()/'snapshots';archive.mkdir(parents=True,exist_ok=True)
    versions=([json.loads(path.read_text())] if path.exists() else [])+[pack]
    for version in versions:
        target=archive/(digest(version)+'.json')
        if not target.exists():target.write_text(json.dumps(version,indent=2))
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_text(json.dumps(pack,indent=2));temp.replace(path)
    finally:temp.unlink(missing_ok=True)


def classify(title):
    s=title.lower()
    if ('financial result' in s or 'audited result' in s or 'unaudited result' in s) and not any(x in s for x in ('intimation','prior intimation','meeting scheduled')):
        return 'financial_results'
    if 'annual report' in s:return 'annual_report'
    if any(x in s for x in ('press release','media release','news release')):return 'company_news'
    return 'announcement'


def _stamp(value):
    return datetime.strptime(value,'%d-%b-%Y %H:%M:%S').replace(tzinfo=IST)


def normalize_announcement(row,symbol,cutoff):
    if str(row.get('symbol','')).upper()!=symbol:return None
    published=_stamp(row['an_dt'])
    available=max(published,_stamp(row['exchdisstime'])) if row.get('exchdisstime') else published
    if available>cutoff:return None
    url=str(row.get('attchmntFile') or '')
    u=urlparse(url)
    if u.scheme!='https' or u.hostname not in ARCHIVE_HOSTS or not u.path.lower().endswith('.pdf') or u.query or u.username or u.password or u.port not in (None,443):return None
    title=(str(row.get('desc') or '')+' — '+str(row.get('attchmntText') or '')).strip()[:1500]
    return {'symbol':symbol,'kind':classify(title),'title':title,'source_url':url,
            'published_at':published.isoformat(),'available_at':available.isoformat(),
            'timestamp_basis':'NSE an_dt and exchange dissemination timestamp (Asia/Kolkata)'+('; '+row['identifier_normalization'] if row.get('identifier_normalization') else '')}


class NSEArchive:
    def __init__(self):
        self.refresh=False
        self.session=requests.Session()
        self.session.headers.update({'User-Agent':'Mozilla/5.0','Accept':'application/json', 'Referer':NSE_PAGE})
        # Normal public session; no credentials, proxy bypass or anti-bot evasion.
        # The public landing page can be denied while the archive API is available.
        # Its cookies are optional; API/PDF responses still must pass status checks.
        try:self.session.get('https://www.nseindia.com',timeout=15)
        except requests.RequestException:pass

    def announcements(self,symbol,start,end):
        from .security_identity import segments
        result=[]
        for requested,left,right in segments(symbol,start,end,clip_listing=False):
            r=self.session.get(NSE_API,params={'index':'equities','symbol':requested,
                        'from_date':left.strftime('%d-%m-%Y'),'to_date':right.strftime('%d-%m-%Y')},timeout=20)
            r.raise_for_status();rows=r.json()
            if not isinstance(rows,list) or len(rows)>=500:raise ValueError('Unverified/truncated NSE announcement response')
            for row in rows:
                if str(row.get('symbol','')).upper() not in {requested,symbol}:raise ValueError('Announcement response belongs to another security')
                normalized=dict(row)
                if requested!=symbol:
                    normalized['identifier_normalization']=requested+' → '+symbol+' via frozen official NSE symbol-change history'
                    normalized['symbol']=symbol
                result.append(normalized)
        return result

    def pdf_text(self,url):
        # Only archive PDFs accepted by normalize_announcement; redirects refused.
        u=urlparse(url)
        if u.scheme!='https' or u.hostname not in ARCHIVE_HOSTS or u.username or u.password or u.port not in (None,443):raise ValueError('Archive URL outside allowlist')
        cache=store_root()/'attachments'/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if cache.exists() and not self.refresh:
            try:
                saved=json.loads(cache.read_text())
                if (saved['source_url']==url and saved['extraction_version']=='pypdf-first35-v1'
                    and len(saved['text'])<=100000 and saved['content_sha256']==hashlib.sha256(saved['text'].encode()).hexdigest()
                    and re.fullmatch(r'[0-9a-f]{64}',saved['archive_sha256'])):
                    self.last_pdf_retrieved_at=saved['retrieved_at']
                    return saved['text'],saved['archive_sha256']
            except (ValueError,KeyError,TypeError):pass
        with self.session.get(url,timeout=25,stream=True,allow_redirects=False) as r:
            r.raise_for_status()
            if r.status_code!=200:raise ValueError('Archive redirect refused')
            chunks=[];size=0
            for part in r.iter_content(65536):
                size+=len(part)
                if size>MAX_PDF_BYTES:raise ValueError('PDF exceeds 32MB download bound')
                chunks.append(part)
        raw=b''.join(chunks)
        if not raw.startswith(b'%PDF'):raise ValueError('Archive did not return PDF')
        from pypdf import PdfReader
        reader=PdfReader(BytesIO(raw))
        if len(reader.pages)>250:raise ValueError('PDF page bound exceeded')
        text='\n'.join((p.extract_text() or '') for p in reader.pages[:35])[:100000]
        archive_sha=hashlib.sha256(raw).hexdigest();self.last_pdf_retrieved_at=datetime.now(timezone.utc).isoformat()
        saved={'source_url':url,'extraction_version':'pypdf-first35-v1','text':text,'archive_sha256':archive_sha,
            'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'retrieved_at':self.last_pdf_retrieved_at}
        cache.parent.mkdir(parents=True,exist_ok=True);temp=cache.with_name(cache.name+'.'+uuid.uuid4().hex+'.tmp')
        try:temp.write_text(json.dumps(saved));temp.replace(cache)
        finally:temp.unlink(missing_ok=True)
        return text,archive_sha


def prepare_company_research(symbol,day,*,provider=None,refresh=False,progress=None):
    cutoff=cutoff_for(symbol,day);path=pack_path(symbol,day)
    if path.exists() and not refresh and json.loads(path.read_text()).get('risk_scan_version')==RISK_SCAN_VERSION:
        upgrade_evidence_view(symbol,day)
        return read_company_research(symbol,day)
    provider=provider or NSEArchive()
    provider.refresh=refresh
    start=cutoff.date()-timedelta(days=180)
    rows=[];cursor=start
    while cursor<=cutoff.date():
        end=min(cursor+timedelta(days=29),cutoff.date())
        if progress:progress(f'{symbol}: announcement window {cursor} to {end}')
        batch=provider.announcements(symbol,cursor,end)
        rows.extend(batch);cursor=end+timedelta(days=1)
    candidates={};invalid=0
    for row in rows:
        try:item=normalize_announcement(row,symbol,cutoff)
        except (ValueError,KeyError,TypeError):invalid+=1;continue
        if item and datetime.fromisoformat(item['available_at']).date()>=start:candidates[item['source_url']]=item
    ordered=sorted(candidates.values(),key=lambda d:d['available_at'],reverse=True)
    # Reserve room for results and issuer news; do not download every routine notice.
    selected=[]
    for kind,limit in [('financial_results',2),('annual_report',1),('company_news',2),('announcement',1)]:
        selected.extend([d for d in ordered if d['kind']==kind][:limit])
    risk_items=[d for d in ordered if potential_adverse(d['title'],recent=(cutoff-datetime.fromisoformat(d['available_at'])).days<=7)]
    seen={d['source_url'] for d in selected}
    selected.extend(d for d in risk_items[:8] if d['source_url'] not in seen)
    docs=[];errors=[];now=datetime.now(timezone.utc).isoformat()
    for item in selected:
        retrieved_at=now
        if progress:progress(f"{symbol}: extract {item['kind']} {item['source_url']}")
        try:
            text,raw_sha=provider.pdf_text(item['source_url'])
            retrieved_at=getattr(provider,'last_pdf_retrieved_at',now)
            status='readable' if len(text.strip())>=300 else 'unreadable'
        except Exception as exc:
            text='';raw_sha=None;status='unreadable';errors.append(type(exc).__name__)
        doc={**item,'id':'CMP-'+digest([symbol,item['source_url'],item['available_at']])[:16],
            'publisher':'NSE-disclosed company filing','text':text,'retrieved_at':retrieved_at,
            'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'archive_sha256':raw_sha,'extraction_status':status}
        CompanyDocument.model_validate(doc)
        docs.append(doc)
    pack={'version':VERSION,'risk_scan_version':RISK_SCAN_VERSION,
        'risk_scan':{'candidate_count':len(risk_items),'selected_urls':[d['source_url'] for d in risk_items[:8]],'metadata_sha256':digest(ordered),'bounded_limit':8},'evidence_view_version':EVIDENCE_VIEW_VERSION,'symbol':symbol,'decision_at':cutoff.isoformat(),'window_start':start.isoformat(),
        'prepared_at':now,'coverage':{'exchange_scan_complete':invalid==0,'invalid_timestamp_rows':invalid,
            'metadata_rows':len(rows),'eligible_announcements':len(ordered),'downloaded_documents':len(docs),
            'source':NSE_PAGE,'selected_documents_only':True},'documents':docs,'errors':errors,
        'limitations':['Selected official filings and issuer news, not comprehensive independent press coverage.',
        'PDF extraction limited to first 35 pages; financial figures are not independently normalized.',
            'Archive retrieved now; exchange disclosure timestamp is the availability evidence, not a certified historical content-version chain.']}
    _persist_pack(path,pack)
    return read_company_research(symbol,day)


def adverse_news_watch(symbol,day,previous_day,*,provider=None):
    """Cheap dated issuer-metadata watch, not an LLM conclusion or complete news feed."""
    cutoff=cutoff_for(symbol,day);start=date.fromisoformat(previous_day)
    if start>cutoff.date():raise ValueError('News watch cannot look backwards')
    # Include the prior checked day: post-close releases must be seen next session.
    path=store_root()/'news_watch'/f'{symbol}_{previous_day}_{day}.json'
    if path.exists():return json.loads(path.read_text())
    result={'symbol':symbol,'date':day,'decision_at':cutoff.isoformat(),'from_date':previous_day,
        'status':'UNAVAILABLE','candidates':[],'scope':'Bounded official issuer metadata; candidates require C2 source/critic validation. Not comprehensive independent news.'}
    try:
        provider=provider or NSEArchive();rows=provider.announcements(symbol,start,cutoff.date())
        candidates=[];invalid=0
        for row in rows:
            try:item=normalize_announcement(row,symbol,cutoff)
            except (ValueError,KeyError,TypeError):invalid+=1;continue
            if item and cutoff_for(symbol,previous_day)<datetime.fromisoformat(item['available_at'])<=cutoff and potential_adverse(item['title'],recent=True):candidates.append(item)
        result.update(status='CHECKED' if not invalid else 'PARTIAL',candidates=candidates[:20],
            invalid_rows=invalid,truncated=len(candidates)>20)
    except Exception as exc:result['error']=type(exc).__name__
    result['checked_at']=datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(result));tmp.replace(path)
    return result


def _has_financial_content(text):
    labels=set(x.lower() for x in re.findall(r'revenue|total income|profit|cash flow|balance sheet|earnings per share',text,re.I))
    return len(labels)>=2 and len(re.findall(r'\d[\d,]*\.\d+|\d{1,3}(?:,\d{3})+',text))>=4


def _excerpt(text,limit=1400):
    # Deterministic extractive context; preserve full snapshot for review, no model call.
    lines=[' '.join(x.split()) for x in text.splitlines() if x.strip()]
    # Prefer actual financial rows over a cover letter or auditor's generic prose.
    windows=[]
    for pattern in [r'revenue from operations',r'profit for the period',r'profit after tax']:
        match=re.search(pattern,text,re.I)
        if match:windows.append(' '.join(text[max(0,match.start()-180):match.start()+360].split()))
    if windows:
        return ('EXTRACTED TABLE WINDOWS; confirm units, column periods and consolidated/standalone basis in original.\n'+'\n'.join(windows))[:limit]
    relevant=[x for x in lines if re.search(r'revenue|profit|income|debt|cash flow|quarter|crore|million|billion|risk|growth|dividend',x,re.I)]
    return ('\n'.join(lines[:4]+relevant+lines[-2:]))[:limit]


def upgrade_evidence_view(symbol,day):
    """Version a new extractive view; original source text and archived versions stay intact."""
    path=pack_path(symbol,day)
    if not path.exists():return False
    raw=json.loads(path.read_text())
    if raw.get('evidence_view_version')==EVIDENCE_VIEW_VERSION:return False
    raw['evidence_view_version']=EVIDENCE_VIEW_VERSION
    _persist_pack(path,raw)
    return True


def read_company_research(symbol,day):
    cutoff=cutoff_for(symbol,day);path=pack_path(symbol,day)
    if not path.exists():
        return {'ok':True,'status':'INSUFFICIENT_EVIDENCE','symbol':symbol,'decision_at':cutoff.isoformat(),
                'documents':[],'pack_sha256':None,'reasons':['Historical company pack not prepared; no assumption of clean fundamentals.']}
    raw=json.loads(path.read_text())
    if raw.get('version')!=VERSION or raw.get('symbol')!=symbol or raw.get('decision_at')!=cutoff.isoformat():raise ValueError('Company evidence pack identity mismatch')
    docs=[CompanyDocument.model_validate(d) for d in raw['documents']]
    if any(d.symbol!=symbol or d.available_at>cutoff for d in docs):raise ValueError('Future/wrong-company evidence in pack')
    financial=[d for d in docs if d.kind in {'financial_results','annual_report'} and d.extraction_status=='readable' and _has_financial_content(d.text)
               and (cutoff-d.available_at).days<=180]
    reasons=[]
    if not raw['coverage'].get('exchange_scan_complete'):reasons.append('Exchange announcement scan incomplete/unverified timestamps')
    if not financial:reasons.append('No readable financial results/annual filing within 180 days')
    modern=raw.get('evidence_view_version') in {'company-view-v2','company-view-v3','company-view-v4-materiality',EVIDENCE_VIEW_VERSION}
    result={'ok':True,'status':'SUFFICIENT' if not reasons else 'INSUFFICIENT_EVIDENCE','symbol':symbol,
        'decision_at':cutoff.isoformat(),'pack_sha256':digest(raw),'coverage':raw['coverage'],'reasons':reasons,
        'limitations':raw['limitations'],'documents':[{**d.model_dump(mode='json',exclude={'text'}),
            'financial_content_detected':_has_financial_content(d.text) if d.kind in {'financial_results','annual_report'} else False,
            'excerpt':context_excerpt(d.text,d.kind) if modern else _excerpt(d.text)} for d in docs]}
    if modern:result['evidence_view_version']=raw['evidence_view_version']
    if raw.get('evidence_view_version')==EVIDENCE_VIEW_VERSION:
        result['documents'],result['omitted_documents']=compact_documents(docs,_has_financial_content)
        result['limitations']=result['limitations']+['Model view prioritizes one recent substantive financial source; secondary excerpts are shorter and unavailable/non-financial attachments are listed separately. Full source text and metadata remain in the hashed pack.']
    scan=raw.get('risk_scan',{});urls=set(scan.get('selected_urls',[]))
    ready=(raw.get('risk_scan_version')==RISK_SCAN_VERSION and raw['coverage'].get('exchange_scan_complete')
        and scan.get('candidate_count',999)<=scan.get('bounded_limit',0)
        and all(any(d.source_url==url and d.extraction_status=='readable' for d in docs) for url in urls))
    result['adverse_scan']={'ready':bool(ready),'version':raw.get('risk_scan_version'),
        'citation_id':'SCAN-'+digest([raw.get('risk_scan'),raw['decision_at'],raw['symbol']])[:16],
        'matched_document_ids':[d.id for d in docs if d.source_url in urls],
        'candidate_count':scan.get('candidate_count'),'window_start':raw['window_start'],
        'decision_at':raw['decision_at'],'source_url':NSE_PAGE,
        'scope':'Bounded official NSE issuer-disclosure metadata search plus readable matched attachments; not exhaustive press or proof of no adverse information.'}
    # Risk-matched attachments must remain visible even when compact financial selection omitted them.
    visible={d['id'] for d in result['documents']}
    for d in docs:
        if d.source_url in urls and d.extraction_status=='readable' and d.id not in visible:
            result['documents'].append({**d.model_dump(mode='json',exclude={'text'}),
                'financial_content_detected':_has_financial_content(d.text),'excerpt':context_excerpt(d.text,'announcement')})
    if raw.get('evidence_view_version')==EVIDENCE_VIEW_VERSION:
        from .company_excerpts import materiality_fields
        source_docs={d.id:d for d in docs}
        for item in result['documents']:
            if item['id'] in result['adverse_scan']['matched_document_ids']:
                item['materiality']=materiality_fields(source_docs[item['id']].text)
    if raw.get('web_search'):
        web=raw['web_search'];accepted=set(web.get('accepted_document_ids',[]))
        safe=web.get('decision_at')==cutoff.isoformat() and len(web.get('queries',[]))==2 and all(q.get('status')=='searched' for q in web['queries'])
        safe=safe and bool(accepted) and accepted.issubset({d.id for d in docs if d.extraction_status=='readable'})
        result['web_scan']={k:web.get(k) for k in ('version','citation_id','decision_at','scope','source_url','status','accepted_document_ids')}
        result['web_scan']['attempted_queries']=len(web.get('queries',[])) if web.get('decision_at')==cutoff.isoformat() else 0
        result['web_scan']['ready']=bool(web.get('ready') and safe)
    return result


def effective_scan(pack):
    official=pack.get('adverse_scan',{})
    return official if official.get('ready') else pack.get('web_scan',{}) if pack.get('web_scan',{}).get('ready') else official


def company_pack_researchable(pack):
    return bool(pack.get('pack_sha256') and (pack.get('status')=='SUFFICIENT' or effective_scan(pack).get('ready')))


def validate_company_assessment(assessment,pack,*,allow_review_required=False,snapshot=None,portfolio_action=None):
    from .signal_evidence import coverage_signal,coverage_reviewed,require_adverse_exit,ADVERSE_FINDINGS
    reducing=allow_review_required and assessment.status=='REVIEW_REQUIRED'
    limited=assessment.adverse_risk=='COVERAGE_LIMITED'
    if portfolio_action:require_adverse_exit(assessment,snapshot or {},portfolio_action)
    if limited:
        if (assessment.status!='LIMITED' or not coverage_signal(snapshot or {}) or
            not coverage_reviewed(pack) or assessment.event_risks):
            raise ValueError('Coverage-only entry requires a strong trend/reversion, attempted dated research and no unresolved event risk')
    if not company_pack_researchable(pack) and not ((limited or reducing) and pack.get('pack_sha256')):raise ValueError('Insufficient company evidence')
    if assessment.status not in {'SUFFICIENT','LIMITED'} and not reducing:
        raise ValueError('Company research requires review or has insufficient evidence')
    docs={d['id']:d for d in pack.get('documents',[]) if d.get('extraction_status')=='readable'}
    scan=effective_scan(pack);scan_id=scan.get('citation_id')
    web=pack.get('web_scan',{})
    permitted=set(docs)|({scan_id} if scan.get('ready') else set())
    if limited and web.get('attempted_queries')==2:permitted.add(web.get('citation_id'))
    if reducing:
        permitted.update(x for x in (pack.get('adverse_scan',{}).get('citation_id'),web.get('citation_id')) if x)
    if not assessment.citations or not set(assessment.citations).issubset(permitted):raise ValueError('Company citation not observed/readable')
    if assessment.adverse_risk in ADVERSE_FINDINGS and (not assessment.event_risks or not any(x in docs for x in assessment.citations)):
        raise ValueError('Adverse finding requires readable cited event evidence')
    if limited:return True
    if reducing:
        if not any(x in docs for x in assessment.citations):raise ValueError('Risk-reducing exit requires readable cited evidence')
        return True
    if not reducing and not scan.get('ready'):raise ValueError('Adverse disclosure coverage is incomplete')
    if not reducing and assessment.adverse_risk!='NO_MATERIAL_ADVERSE_FOUND':
        raise ValueError('Adverse event risk is material or remains unknown')
    if assessment.status=='LIMITED' or pack.get('status')!='SUFFICIENT':
        if assessment.status!='LIMITED' and not reducing:raise ValueError('Limited financial coverage must be disclosed as LIMITED')
        if not scan.get('ready') or scan_id not in assessment.citations:raise ValueError('A completed cited adverse-disclosure scan is required')
    elif not any(docs[x]['kind'] in {'financial_results','annual_report'} and docs[x].get('financial_content_detected') for x in assessment.citations if x in docs):
        raise ValueError('A financial filing with financial content is required')
    if reducing and not any(x in docs for x in assessment.citations):raise ValueError('Risk-reducing exit requires readable cited evidence')
    if (snapshot or {}).get('regime')=='BREAKOUT' and (snapshot or {}).get('research_purpose','ENTRY')=='ENTRY':
        if not assessment.breakout_support or not any(x in docs for x in assessment.citations):
            raise ValueError('Breakout entry requires readable dated corroboration and breakout_support')
    return True


def validate_current_company_pack(pack,*,allow_partial=False):
    current=read_company_research(pack['symbol'],date.fromisoformat(pack['decision_at'][:10]).isoformat())
    if not current.get('pack_sha256') or current['pack_sha256']!=pack.get('pack_sha256') or (not allow_partial and not company_pack_researchable(current)):raise ValueError('Company evidence changed; rerun C2 and approval')
    return current


def import_archived_news(symbol,day,jsonl_path,reviewer):
    """Import up to two licensed excerpts with independently verified original dates.

    No arbitrary-URL fetch. Imported news cannot replace an official financial
    filing or satisfy a failed exchange scan. Date-only publication is delayed
    until the following local midnight, never assumed known at that day's close.
    """
    if not reviewer or len(reviewer.strip())<3:raise ValueError('Named source/date reviewer required')
    cutoff=cutoff_for(symbol,day);path=pack_path(symbol,day)
    read_company_research(symbol,day)
    if not path.exists():raise ValueError('Prepare the official exchange pack first')
    raw=json.loads(path.read_text());incoming=[]
    for line in Path(jsonl_path).read_text().splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if row.get('kind') not in {'news','newsletter'} or row.get('symbol')!=symbol or row.get('original_publication_verified') is not True:
            raise ValueError('Only reviewed company news/newsletters with verified original publication are accepted')
        published=row['published_at'];date_only=len(published)==10
        pub=datetime.combine(date.fromisoformat(published),time.min,IST) if date_only else datetime.fromisoformat(published.replace('Z','+00:00'))
        if pub.tzinfo is None:raise ValueError('Original publication timestamp needs a timezone')
        available=pub+timedelta(days=1) if date_only else pub
        if row.get('available_at'):
            specified=datetime.fromisoformat(row['available_at'].replace('Z','+00:00'))
            if specified.tzinfo is None:raise ValueError('Availability timestamp needs a timezone')
            available=max(available,specified)
        if available>cutoff or available<cutoff-timedelta(days=180):raise ValueError('Imported news outside point-in-time window')
        text=row['text']
        if not 100<=len(text)<=4000:raise ValueError('Import a licensed 100–4000 character excerpt, not a whole publication')
        doc={'id':'CMP-'+digest([symbol,row['source_url'],available.isoformat(),text])[:16],
            'symbol':symbol,'kind':row['kind'],'title':row['title'],'text':text,
            'source_url':row['source_url'],'publisher':row['publisher'],'published_at':pub.isoformat(),
            'available_at':available.isoformat(),'retrieved_at':datetime.now(timezone.utc).isoformat(),
            'content_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'timestamp_basis':'Original publisher date verified by '+reviewer+('; date-only available next midnight' if date_only else ''),
            'extraction_status':'readable'}
        incoming.append(CompanyDocument.model_validate(doc).model_dump(mode='json'))
    if not 1<=len(incoming)<=2:raise ValueError('Import one or two source-backed excerpts per pack')
    raw['documents']=[d for d in raw['documents'] if d['kind'] not in {'news','newsletter'}]+incoming
    raw['limitations'].append('Supplementary press/newsletter dates are reviewer-attested; web search does not independently certify them.')
    _persist_pack(path,raw)
    return read_company_research(symbol,day)
