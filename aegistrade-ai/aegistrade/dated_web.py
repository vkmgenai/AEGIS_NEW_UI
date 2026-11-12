"""Bounded dated web evidence via public HTML search. No LLM or broker calls."""
from datetime import datetime,date,time as daytime,timedelta,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,parse_qs,urljoin
from io import BytesIO
import hashlib,ipaddress,json,os,re,socket,time,uuid
import requests
from .security import scan_untrusted_text

VERSION='dated-web-v1'
ENGINE='https://html.duckduckgo.com/html/'
SOURCES=json.loads((Path(__file__).resolve().parents[1]/'config/dated_web_sources.json').read_text())
MAX_SEARCHES=2;MAX_PAGES=4;MAX_ACCEPTED=2;MAX_BYTES=8_000_000;DEADLINE_SECONDS=40


def enabled():return os.getenv('AEGIS_DATED_WEB_SEARCH','true').lower()=='true'


def eligible(snapshot):
    if not enabled():return False
    from .agent_tools import CaseEvidence
    try:e=CaseEvidence.from_snapshot(snapshot)
    except ValueError:return False
    if e.research_purpose=='HOLDING_REVIEW':return True
    if e.ATR14<=0:return False
    if e.regime in {'TREND','PULLBACK'}:return e.ADX14>=22 and e.Close>e.EMA20>e.EMA50
    if e.regime=='RANGE':return e.RSI14<42 and e.Close>.88*e.EMA50
    return e.regime in {'BREAKOUT','BREAKOUT_BOUNCE'} and e.ADX14>=18


def needed(pack,assessment=None):
    if assessment:
        return assessment.get('adverse_risk') in {'UNKNOWN','COVERAGE_LIMITED'} or assessment.get('status')=='INSUFFICIENT_EVIDENCE'
    from .company_research import effective_scan,company_pack_researchable
    return not company_pack_researchable(pack) or not effective_scan(pack).get('ready')


def trusted(url,symbol):
    p=urlparse(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443):return None
    host=p.hostname.lower().rstrip('.')
    try:ipaddress.ip_address(host);return None
    except ValueError:pass
    def matches(domains):return any(host==d or host.endswith('.'+d) for d in domains)
    if matches(SOURCES['primary_domains']+SOURCES['issuers'].get(symbol,[])):return 'primary'
    if matches(SOURCES['secondary_domains']):return 'secondary'
    return None


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.meta={};self.parts=[];self.title=[];self.links=[];self.jsonld=[]
        self.skip=0;self.in_title=False;self.ld=False;self.buffer=[];self.anchor=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.meta.setdefault(a.get('property') or a.get('name') or a.get('itemprop'),[]).append(a.get('content',''))
        if tag=='title':self.in_title=True
        if tag in {'script','style','nav','footer'}:
            self.skip+=1
            if tag=='script' and a.get('type')=='application/ld+json':self.ld=True;self.buffer=[]
        if tag=='a' and 'result__a' in a.get('class','').split():self.anchor={'url':a.get('href',''),'title':''}
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script' and self.ld:self.jsonld.append(''.join(self.buffer));self.ld=False
        if tag in {'script','style','nav','footer'}:self.skip=max(0,self.skip-1)
        if tag=='a' and self.anchor:self.links.append(self.anchor);self.anchor=None
    def handle_data(self,text):
        if self.ld:self.buffer.append(text)
        if self.in_title:self.title.append(text)
        if self.anchor:self.anchor['title']+=text
        if not self.skip and not self.in_title:self.parts.append(text)


def timestamp(raw):
    from .company_research import IST
    value=str(raw).strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        published=datetime.combine(date.fromisoformat(value),daytime.min,timezone.utc)
        return published,published+timedelta(days=2),'Publisher date only; conservative 48-hour availability delay'
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None:raise ValueError('UNVERIFIED_PUBLICATION_TIMEZONE')
    return parsed,parsed,'Publisher timezone-aware publication metadata'


def publication(page):
    values=[];modified=[]
    for key in ('article:published_time','datePublished','datepublished','pubdate'):
        values.extend(page.meta.get(key,[]))
    for key in ('article:modified_time','dateModified','datemodified'):modified.extend(page.meta.get(key,[]))
    def visit(item):
        if isinstance(item,dict):
            kind=item.get('@type',[]);kind=[kind] if isinstance(kind,str) else kind
            if set(kind)&{'Article','NewsArticle','BlogPosting','Report','ScholarlyArticle','PressRelease'}:
                if item.get('datePublished'):values.append(item['datePublished'])
                if item.get('dateModified'):modified.append(item['dateModified'])
            for child in item.values():visit(child)
        elif isinstance(item,list):
            for child in item:visit(child)
    for raw in page.jsonld:
        try:visit(json.loads(raw))
        except (ValueError,TypeError):pass
    if not values:raise ValueError('NO_VERIFIABLE_PUBLICATION_METADATA')
    stamps=[timestamp(v) for v in values]
    if len({p[0] for p in stamps})!=1:raise ValueError('CONFLICTING_PUBLICATION_DATES')
    return stamps[0], [timestamp(v)[1] for v in modified]


class PublicWeb:
    def __init__(self):
        self.deadline=time.monotonic()+DEADLINE_SECONDS
        self.session=requests.Session();self.session.trust_env=False
        self.session.headers.update({'User-Agent':'Mozilla/5.0 (compatible; AegisTradeResearch/0.21)'})
    def _get(self,url,*,params=None,search=False,symbol=None):
        if not search and not trusted(url,symbol):raise ValueError('UNTRUSTED_SOURCE_DOMAIN')
        host=urlparse(url).hostname
        for addr in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM):
            if not ipaddress.ip_address(addr[4][0]).is_global:raise ValueError('NONPUBLIC_SOURCE_ADDRESS')
        remaining=self.deadline-time.monotonic()
        if remaining<=0:raise ValueError('WEB_SEARCH_DEADLINE')
        with self.session.get(url,params=params,timeout=min(8,remaining),allow_redirects=False,stream=True) as response:
            response.raise_for_status()
            if 300<=response.status_code<400:raise ValueError('REDIRECT_REQUIRES_SOURCE_REVIEW')
            body=bytearray()
            for chunk in response.iter_content(32768):
                if time.monotonic()>self.deadline:raise ValueError('WEB_SEARCH_DEADLINE')
                body.extend(chunk)
                if len(body)>MAX_BYTES:raise ValueError('WEB_SOURCE_SIZE_LIMIT')
            return bytes(body),response.headers.get('Content-Type','')
    def search(self,query):
        raw,_=self._get(ENGINE,params={'q':query},search=True);page=Page();page.feed(raw.decode('utf-8',errors='replace'))
        if not page.links:
            if 'no results' in ' '.join(page.parts).lower():return []
            raise ValueError('SEARCH_UNAVAILABLE_OR_CHALLENGED')
        links=[]
        for row in page.links[:8]:
            url=urljoin(ENGINE,row['url'])
            if urlparse(url).hostname in {'duckduckgo.com','html.duckduckgo.com'}:url=parse_qs(urlparse(url).query).get('uddg',[url])[0]
            links.append({'url':url,'title':row['title'].strip()})
        return links
    def fetch(self,url,symbol):
        from .company_research import store_root
        if not trusted(url,symbol):raise ValueError('UNTRUSTED_SOURCE_DOMAIN')
        key=hashlib.sha256(url.encode()).hexdigest();root=store_root()/'web_pages';meta_path=root/(key+'.json')
        if meta_path.exists():
            info=json.loads(meta_path.read_text());sha=info.get('sha256','')
            if not re.fullmatch(r'[0-9a-f]{64}',sha):raise ValueError('WEB_CACHE_INTEGRITY')
            body=(root/(key+'.'+sha+'.body')).read_bytes()
            if info.get('source_url')!=url or hashlib.sha256(body).hexdigest()!=sha or len(body)>MAX_BYTES:raise ValueError('WEB_CACHE_INTEGRITY')
            self.last_retrieved_at=info['retrieved_at'];return body,info['content_type']
        body,kind=self._get(url,symbol=symbol);self.last_retrieved_at=datetime.now(timezone.utc).isoformat()
        root.mkdir(parents=True,exist_ok=True);sha=hashlib.sha256(body).hexdigest();body_path=root/(key+'.'+sha+'.body')
        temporary=body_path.with_suffix('.'+uuid.uuid4().hex+'.tmp');temporary.write_bytes(body);temporary.replace(body_path)
        tmp=meta_path.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps({'source_url':url,'sha256':sha,'content_type':kind,'retrieved_at':self.last_retrieved_at}));tmp.replace(meta_path)
        return body,kind


def identity(symbol):
    from .security_identity import metadata,segments
    tables,_=metadata();master=tables['EQUITY_L'];row=master[master.SYMBOL==symbol]
    name=str(row.iloc[0]['NAME OF COMPANY']) if len(row)==1 else symbol
    aliases={symbol}
    try:aliases.update(item[0] for item in segments(symbol,date(2000,1,1),date.today(),clip_listing=False))
    except ValueError:pass
    return name,aliases


def extract_source(hit,symbol,cutoff,backend,known):
    from .company_research import CompanyDocument,classify,_has_financial_content,IST
    url=hit['url'];authority=trusted(url,symbol)
    if not authority:raise ValueError('UNTRUSTED_SOURCE_DOMAIN')
    raw,kind=backend.fetch(url,symbol);title=hit.get('title','')
    if 'pdf' in kind.lower() or raw.startswith(b'%PDF'):
        if url not in known:raise ValueError('PDF_PUBLICATION_NOT_VERIFIED')
        from pypdf import PdfReader
        reader=PdfReader(BytesIO(raw),strict=False)
        text='\n'.join(p.extract_text() or '' for p in reader.pages[:35])[:100000]
        original=known[url];published=datetime.fromisoformat(original['published_at']);available=datetime.fromisoformat(original['available_at'])
        basis='Known exchange disclosure timestamp for exact source URL; retrieved again by dated web fallback'
    else:
        if 'html' not in kind.lower():raise ValueError('UNSUPPORTED_SOURCE_CONTENT_TYPE')
        page=Page();page.feed(raw.decode('utf-8',errors='replace'))
        (published,available,basis),modified=publication(page)
        if any(value>cutoff for value in modified):raise ValueError('PAGE_UPDATED_AFTER_DECISION')
        title=' '.join(page.title).strip() or title;text=' '.join(' '.join(page.parts).split())[:100000]
    if published>cutoff or available>cutoff:raise ValueError('SOURCE_AFTER_DECISION')
    if available<cutoff-timedelta(days=180):raise ValueError('SOURCE_OUTSIDE_LOOKBACK')
    if len(text)<300:raise ValueError('INSUFFICIENT_READABLE_SOURCE_TEXT')
    if not scan_untrusted_text(text)['ok']:raise ValueError('UNTRUSTED_SOURCE_INSTRUCTIONS')
    name,aliases=identity(symbol)
    simplified=re.sub(r'[^a-z0-9]+',' ',text.lower())
    company=re.sub(r'\b(limited|ltd|private)\b','',name.lower());company=' '.join(re.sub(r'[^a-z0-9]+',' ',company).split())
    if not ((len(company)>4 and company in simplified) or any(re.search(r'(?<!\w)'+re.escape(a)+r'(?!\w)',text,re.I) for a in aliases)):
        raise ValueError('WRONG_COMPANY_SOURCE')
    from .company_research import digest
    document_kind=classify(title)
    if document_kind in {'financial_results','annual_report'} and (authority!='primary' or not _has_financial_content(text)):document_kind='news'
    return {'id':'WEB-'+digest([symbol,url,available.isoformat()])[:16],'symbol':symbol,'kind':document_kind,
        'title':title[:1500] or 'Dated company source','source_url':url,'publisher':authority+' source: '+urlparse(url).hostname,
        'published_at':published.isoformat(),'available_at':available.isoformat(),'retrieved_at':getattr(backend,'last_retrieved_at',datetime.now(timezone.utc).isoformat()),
        'text':text,'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'archive_sha256':hashlib.sha256(raw).hexdigest(),
        'timestamp_basis':basis,'extraction_status':'readable'}


def search_and_enrich(snapshot,*,backend=None):
    """Exactly one cached attempt per symbol/cutoff; failed attempts are not automatic retries."""
    from .company_research import cutoff_for,pack_path,read_company_research,_persist_pack,VERSION as PACK_VERSION,EVIDENCE_VIEW_VERSION,RISK_SCAN_VERSION,digest
    symbol=snapshot['symbol'];day=snapshot['date'];cutoff=cutoff_for(symbol,day)
    if not eligible(snapshot):return {'ok':False,'error_code':'WEB_SEARCH_NOT_ELIGIBLE','message':'A code-qualified technical case or existing holding is required.'}
    path=pack_path(symbol,day);before=read_company_research(symbol,day)
    raw=json.loads(path.read_text()) if path.exists() else {'version':PACK_VERSION,'risk_scan_version':RISK_SCAN_VERSION,'evidence_view_version':EVIDENCE_VIEW_VERSION,
        'symbol':symbol,'decision_at':cutoff.isoformat(),'window_start':str((cutoff-timedelta(days=180)).date()),'prepared_at':datetime.now(timezone.utc).isoformat(),
        'coverage':{'exchange_scan_complete':False,'invalid_timestamp_rows':0,'selected_documents_only':True,'source':'Official archive unavailable'},
        'risk_scan':{'candidate_count':0,'selected_urls':[],'bounded_limit':8},'documents':[],'errors':['Official archive unavailable'],
        'limitations':['Official archive unavailable; a dated web scan is a separate bounded source, not an exchange-scan substitute claim.']}
    if raw.get('web_search',{}).get('version')==VERSION:
        return {'ok':True,'company_evidence':before,'previous_pack_sha256':before.get('pack_sha256'),'search_audit':raw['web_search'],'cached':True}
    name,aliases=identity(symbol);historical=sorted(aliases)[0]
    try:
        from .security_identity import segments
        historical=segments(symbol,cutoff.date(),cutoff.date(),clip_listing=False)[0][0]
    except (ValueError,IndexError):pass
    subject=historical
    dates=f' after:{raw["window_start"]} before:{(cutoff+timedelta(days=1)).date()}'
    queries=[subject+' financial results India'+dates,subject+' adverse regulatory default news India'+dates]
    audit={'version':VERSION,'provider':'duckduckgo_html','decision_at':cutoff.isoformat(),'attempted_at':datetime.now(timezone.utc).isoformat(),
        'queries':[],'sources':[],'accepted_document_ids':[],'ready':False,'scope':'Two bounded financial/adverse queries; up to four trusted source pages. Not exhaustive web/news coverage or proof of safety. Publication metadata is not a certified historical content-version chain.'}
    accepted=[];unresolved=False;all_queries=True;seen=set();known={d['source_url']:d for d in raw['documents']}
    backend=backend or PublicWeb()
    for query in queries:
        try:hits=backend.search(query);audit['queries'].append({'query':query,'status':'searched','returned':len(hits)})
        except Exception as exc:
            audit['queries'].append({'query':query,'status':'unavailable','error':str(exc)[:100] if isinstance(exc,ValueError) else type(exc).__name__});all_queries=False;continue
        selected=[h for h in hits if trusted(h.get('url',''),symbol)][:2]
        for hit in selected:
            if hit['url'] in seen:continue
            seen.add(hit['url'])
            try:
                doc=extract_source(hit,symbol,cutoff,backend,known)
                if len(accepted)<MAX_ACCEPTED:accepted.append(doc)
                audit['sources'].append({'url':hit['url'],'status':'validated','available_at':doc['available_at'],'id':doc['id']})
            except Exception as exc:
                reason=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
                if reason not in {'SOURCE_AFTER_DECISION','SOURCE_OUTSIDE_LOOKBACK','PAGE_UPDATED_AFTER_DECISION'}:unresolved=True
                audit['sources'].append({'url':hit['url'],'status':'rejected','reason':reason[:100]})
    for doc in accepted:
        existing=next((d for d in raw['documents'] if d['source_url']==doc['source_url']),None)
        if existing:
            doc['id']=existing['id'];raw['documents'][raw['documents'].index(existing)]=doc
        else:raw['documents'].append(doc)
        audit['accepted_document_ids'].append(doc['id'])
    scan=raw.get('risk_scan',{});required=set(scan.get('selected_urls',[]))
    known_unresolved=scan.get('candidate_count',0)>scan.get('bounded_limit',8) or raw['coverage'].get('invalid_timestamp_rows',0)>0 or any(
        not any(d['source_url']==url and d['extraction_status']=='readable' for d in raw['documents']) for url in required)
    audit['ready']=bool(all_queries and not unresolved and not known_unresolved and any(d['publisher'].startswith('primary') for d in accepted))
    audit['status']='SUPPORTED_BOUNDED_SCAN' if audit['ready'] else 'SEARCHED_BUT_INSUFFICIENT'
    audit['citation_id']='WEBSCAN-'+digest([symbol,day,audit])[:16];audit['source_url']=ENGINE
    raw['web_search']=audit;raw['limitations'].append(audit['scope']);_persist_pack(path,raw)
    return {'ok':True,'company_evidence':read_company_research(symbol,day),'previous_pack_sha256':before.get('pack_sha256'),'search_audit':audit,'cached':False}
