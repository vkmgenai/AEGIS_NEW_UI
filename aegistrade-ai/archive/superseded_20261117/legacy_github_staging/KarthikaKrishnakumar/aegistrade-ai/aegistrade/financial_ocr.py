"""Optional local macOS OCR for existing official financial PDFs, never LLM text."""
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime,timezone
import hashlib,json,subprocess,tempfile,shutil,threading
import requests
from .company_research import store_root,ARCHIVE_HOSTS,MAX_PDF_BYTES
from .evidence_library import atomic
LOCK=threading.Lock()
VERSION='pypdf+apple-vision-financial-v2'
OCR_LIMIT=threading.Semaphore(2)


def binary():
    source=Path(__file__).resolve().parents[1]/'scripts'/'ocr_pdf.swift'
    target=Path(tempfile.gettempdir())/('aegis-ocr-'+hashlib.sha256(source.read_bytes()).hexdigest()[:12])
    with LOCK:
        if not target.exists():
            compiler=shutil.which('swiftc')
            if not compiler:raise ValueError('Local macOS OCR compiler unavailable')
            subprocess.run([compiler,'-module-cache-path',str(Path(tempfile.gettempdir())/'aegis-swift-cache'),str(source),'-o',str(target)],check=True,capture_output=True,timeout=180)
    return target


def repair_pdf(url):
    u=urlparse(url)
    if u.scheme!='https' or u.hostname not in ARCHIVE_HOSTS or u.username or u.password or u.port not in (None,443) or u.query or not u.path.lower().endswith('.pdf'):raise ValueError('OCR source outside official PDF allowlist')
    key=hashlib.sha256(url.encode()).hexdigest();folder=store_root()/'attachments';cache=folder/(key+'.json');pdf=folder/(key+'.pdf')
    old=json.loads(cache.read_text()) if cache.exists() else {}
    if old.get('extraction_version') in {VERSION,'pypdf+apple-vision-first8-v1'} and old.get('content_sha256')==hashlib.sha256(old.get('text','').encode()).hexdigest():return old['text'],old['archive_sha256']
    if not pdf.exists():
        with requests.get(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.nseindia.com/'},stream=True,allow_redirects=False,timeout=30) as r:
            r.raise_for_status()
            if r.status_code!=200:raise ValueError('OCR PDF redirect refused')
            parts=[];size=0
            for chunk in r.iter_content(65536):
                size+=len(chunk)
                if size>MAX_PDF_BYTES:raise ValueError('OCR PDF exceeds download bound')
                parts.append(chunk)
        raw=b''.join(parts)
        if not raw.startswith(b'%PDF'):raise ValueError('OCR source did not return a PDF')
        folder.mkdir(parents=True,exist_ok=True);temp=pdf.with_suffix('.pdf.tmp');temp.write_bytes(raw);temp.replace(pdf)
    raw=pdf.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    # Bind OCR and PDF extraction to the very same source bytes.
    from pypdf import PdfReader
    from io import BytesIO
    reader=PdfReader(BytesIO(raw))
    if len(reader.pages)>250:raise ValueError('OCR PDF exceeds page bound')
    original='\n'.join((p.extract_text() or '') for p in reader.pages[:35])[:100000]
    from .company_research import _has_financial_content
    for page_limit in (2,4,8):
        with OCR_LIMIT:
            done=subprocess.run([str(binary()),str(pdf),str(page_limit)],capture_output=True,text=True,timeout=120)
        if done.returncode or len(done.stdout.strip())<300:raise ValueError('Local OCR unavailable/unreadable')
        text=('MACHINE OCR SUPPLEMENT: numerical and table-column accuracy is unverified; inspect original PDF.\n'+done.stdout+'\n[ORIGINAL PDF TEXT EXTRACTION]\n'+original)[:100000]
        if _has_financial_content(text) or len(reader.pages)<=page_limit:break
    value={'source_url':url,'extraction_version':VERSION,'text':text,'archive_sha256':sha,
           'content_sha256':hashlib.sha256(text.encode()).hexdigest(),'retrieved_at':datetime.now(timezone.utc).isoformat(),
           'ocr_pages':min(page_limit,len(reader.pages)),'caution':'OCR is not independently verified financial data.'}
    atomic(cache,value);return text,sha
