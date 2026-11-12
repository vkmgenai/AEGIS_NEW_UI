"""Reviewed, immutable portfolio lesson versions. No generation or P&L labels."""
from contextlib import contextmanager
from datetime import date,datetime,timezone
from pathlib import Path
import hashlib,json,os,re,sqlite3,uuid
from .security import scan_untrusted_text

VERSION='portfolio-lessons-v1'
TEMPLATES={
    'context':('execution','Treat context overflow as an engineering failure, not an adverse-company judgment. Use the bounded evidence view and preserve source audit; if required evidence cannot fit, abstain explicitly.', 'When research context or evidence packing fails.'),
    'materiality':('regime','Assess an adverse disclosure using its stated impact, amount, severity, recency, operating restrictions and continuing consequences. A negative keyword alone is not material downside. Attribute issuer statements and retain unresolved material risks.', 'When evaluating regulatory, litigation, management-change or other adverse disclosures.'),
    'coverage':('grounding','Separate limited financial or independent-news coverage from the findings of a completed bounded adverse scan. Unobserved imaginable risks are not evidence of an event. Keep unknown coverage and genuinely unresolved material exposure explicit.', 'When financial coverage is limited or an adverse assessment is unknown.'),
    'citation':('grounding','Check that each financial or event claim is supported by its exact observed source ID, reporting period and evidence text. A true fact attributed to the wrong source still needs correction.', 'When preparing or critiquing company claims and citations.')}


def _now():return datetime.now(timezone.utc).isoformat()
def _digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def _id(value):
    if not re.fullmatch(r'[0-9a-f]{32}',str(value)):raise ValueError('Invalid portfolio lesson/version ID')
    return value
def _root():return Path(os.getenv('AEGIS_DATA_DIR','data'))
def _state(run_id):return _root()/'c2_portfolio_runs'/_id(run_id)/'state.json'


@contextmanager
def _db():
    root=_root();root.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(root/'portfolio_lessons.sqlite',timeout=30)
    con.row_factory=sqlite3.Row
    con.execute('CREATE TABLE IF NOT EXISTS candidates (id TEXT PRIMARY KEY,run_id TEXT,kind TEXT,payload TEXT,status TEXT,reason TEXT,reviewed_at TEXT,UNIQUE(run_id,kind))')
    con.execute('CREATE TABLE IF NOT EXISTS versions (id TEXT PRIMARY KEY,sha256 TEXT,payload TEXT,created TEXT)')
    con.commit()
    try:yield con
    finally:con.close()


def _safe_lesson(text,condition):
    if not 10<=len(text)<=500 or not 5<=len(condition)<=240:raise ValueError('Lesson must be 10–500 characters; condition 5–240')
    combined=text+' '+condition
    if not scan_untrusted_text(combined)['ok']:raise ValueError('Instruction injection is not permitted in lessons')
    if re.search(r'(?i)always buy|never sell|guarantee.{0,30}profit|increase.{0,30}(?:size|risk).{0,30}(?:loss|recover)|ignore.{0,20}(?:risk|critic|stop)',combined):
        raise ValueError('Lessons cannot authorize trades, promise profit or change risk controls')


def _source_matches(payload):
    p=_state(payload['source_run_id'])
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=payload['source_digest']:
        raise ValueError('Source portfolio changed or is missing; draft/review from the correct completed result')
    for cid,expected in payload.get('research_digests',{}).items():
        source=p.parent/'research'/(_id(cid)+'.json')
        if not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
            raise ValueError('Source research changed or is missing')


def draft_from_run(run_id):
    path=_state(run_id)
    if not path.exists():raise ValueError('Source portfolio not found')
    state=json.loads(path.read_text())
    if not state['status'].startswith('COMPLETED'):raise ValueError('Review a completed portfolio; active/paused results are not final')
    groups={}
    for d in state.get('decisions',[]):
        if d.get('action') not in {'BLOCKED','FILL_BLOCKED'}:continue
        failure=d.get('failure') or {};code=failure.get('code','');errors=' '.join(d.get('errors',[]))
        kind=('context' if 'CONTEXT_BUDGET' in code+errors else 'citation' if 'CRITIC_REJECTED' in code+errors else
              'coverage' if 'No readable financial' in errors else 'materiality' if any(x in code+errors for x in ('ADVERSE_RISK','COMPANY_ASSESSMENT')) else None)
        if kind:groups.setdefault(kind,[]).append(d)
    created=[]
    with _db() as con:
        for kind,decisions in groups.items():
            if con.execute('SELECT id FROM candidates WHERE run_id=? AND kind=?',(run_id,kind)).fetchone():continue
            topic,text,condition=TEMPLATES[kind];evidence=[];digests={}
            for d in decisions:
                item={k:d[k] for k in ('date','symbol','purpose','action','errors') if k in d}
                if d.get('id'):
                    source=path.parent/'research'/(_id(d['id'])+'.json')
                    if source.exists():
                        raw=source.read_bytes();digests[d['id']]=hashlib.sha256(raw).hexdigest();out=json.loads(raw)
                        pack=out.get('company_research') or next((t.get('observation',{}) for t in out.get('tool_trace',[]) if t.get('tool')=='company_evidence'),{})
                        item['company_assessment']=out.get('company_assessment')
                        item['source_documents']=[{k:doc[k] for k in ('id','title','source_url','available_at') if k in doc} for doc in pack.get('documents',[])]
                        item['adverse_scan']=pack.get('adverse_scan',{})
                        # Use the original immutable pack, never newer filings, for human source review.
                        sha=pack.get('pack_sha256','')
                        archive=_root()/'company_research'/'snapshots'/(sha+'.json') if re.fullmatch(r'[0-9a-f]{64}',sha) else None
                        if archive and archive.exists():
                            from .company_research import digest,cutoff_for
                            from .company_excerpts import materiality_fields
                            original=json.loads(archive.read_text())
                            if digest(original)!=sha:raise ValueError('Source evidence snapshot integrity check failed')
                            cutoff=cutoff_for(d['symbol'],d['date'])
                            item['source_materiality_windows']=[{'id':doc['id'],'source_url':doc['source_url'],
                                'available_at':doc['available_at'],'fields':materiality_fields(doc['text'])}
                                for doc in original.get('documents',[]) if doc.get('text')
                                and datetime.fromisoformat(doc['available_at'])<=cutoff
                                and (doc['id'] in pack.get('adverse_scan',{}).get('matched_document_ids',[])
                                     or doc['source_url'] in original.get('risk_scan',{}).get('selected_urls',[]))]

                evidence.append(item)
            cid=uuid.uuid4().hex
            payload={'id':cid,'source_run_id':run_id,'source_digest':hashlib.sha256(path.read_bytes()).hexdigest(),
                'source_dates':[state['dates'][0],state['dates'][-1]],'trained_through':state['dates'][-1],
                'topic':topic,'lesson':text,'applies_when':condition,'created_at':_now(),
                'research_digests':digests,'cases':evidence,
                'scope':'Conditional process lesson; not a finding that every blocked case was wrong. Later P&L intentionally excluded.'}
            con.execute('INSERT INTO candidates VALUES(?,?,?,?,?,?,?)',(cid,run_id,kind,json.dumps(payload),'PENDING','',None));created.append(cid)
        con.commit()
    return {'created_ids':created,'candidate_count':len(created),'model_calls':0}


def list_candidates():
    with _db() as con:
        return [{**json.loads(r['payload']),'status':r['status'],'review_reason':r['reason'],'reviewed_at':r['reviewed_at']} for r in con.execute('SELECT * FROM candidates ORDER BY rowid DESC')]


def review(candidate_id,decision,reason,lesson=None,condition=None):
    _id(candidate_id)
    if decision not in {'ACCEPT','REJECT'} or not 5<=len(reason.strip())<=800:raise ValueError('Choose ACCEPT/REJECT and give a 5–800 character rationale')
    with _db() as con:
        con.execute('BEGIN IMMEDIATE')
        row=con.execute('SELECT * FROM candidates WHERE id=?',(candidate_id,)).fetchone()
        if not row or row['status']!='PENDING':raise ValueError('Candidate is missing or already reviewed')
        payload=json.loads(row['payload']);_source_matches(payload)
        if lesson is not None:payload['lesson']=lesson.strip()
        if condition is not None:payload['applies_when']=condition.strip()
        _safe_lesson(payload['lesson'],payload['applies_when'])
        con.execute('UPDATE candidates SET payload=?,status=?,reason=?,reviewed_at=? WHERE id=?',
            (json.dumps(payload),'ACCEPTED' if decision=='ACCEPT' else 'REJECTED',reason.strip(),_now(),candidate_id));con.commit()


def freeze(candidate_ids):
    if not candidate_ids or len(candidate_ids)>32 or len(set(candidate_ids))!=len(candidate_ids):raise ValueError('Choose 1–32 distinct accepted candidates')
    with _db() as con:
        con.execute('BEGIN IMMEDIATE');lessons=[]
        for cid in sorted(candidate_ids):
            row=con.execute('SELECT * FROM candidates WHERE id=?',(_id(cid),)).fetchone()
            if not row or row['status']!='ACCEPTED':raise ValueError('Only human-accepted candidates can be frozen')
            p=json.loads(row['payload']);_source_matches(p);_safe_lesson(p['lesson'],p['applies_when'])
            lessons.append({k:p[k] for k in ('id','topic','lesson','applies_when','source_run_id','source_digest','trained_through')})
            lessons[-1].update(reviewed_by='authenticated_demo_reviewer',review_reason=row['reason'],reviewed_at=row['reviewed_at'])
        payload={'schema':VERSION,'lessons':lessons,'trained_through':max(x['trained_through'] for x in lessons)}
        sha=_digest(payload);existing=con.execute('SELECT * FROM versions WHERE sha256=?',(sha,)).fetchone()
        if existing:return {'id':existing['id'],'sha256':sha,'created_at':existing['created'],**payload}
        vid=uuid.uuid4().hex;created=_now()
        con.execute('INSERT INTO versions VALUES(?,?,?,?)',(vid,sha,json.dumps(payload),created));con.commit()
    return {'id':vid,'sha256':sha,'created_at':created,**payload}


def load_version(version_id):
    with _db() as con:row=con.execute('SELECT * FROM versions WHERE id=?',(_id(version_id),)).fetchone()
    if not row:raise ValueError('Frozen portfolio playbook not found')
    payload=json.loads(row['payload'])
    if payload.get('schema')!=VERSION or _digest(payload)!=row['sha256']:raise ValueError('Frozen portfolio playbook integrity check failed')
    for lesson in payload['lessons']:_safe_lesson(lesson['lesson'],lesson['applies_when'])
    return {'id':row['id'],'sha256':row['sha256'],'created_at':row['created'],**payload}


def list_versions():
    with _db() as con:ids=[r['id'] for r in con.execute('SELECT id FROM versions ORDER BY created DESC')]
    return [{k:v[k] for k in ('id','sha256','created_at','trained_through')}|{'lesson_count':len(v['lessons'])} for v in map(load_version,ids)]


def bind(version_id,start_date,allow_development=False):
    if not version_id:return None
    book=load_version(version_id);overlap=str(start_date)<=book['trained_through']
    if overlap and not allow_development:raise ValueError('Lesson training overlaps this period; choose later dates or explicitly mark a development replay')
    return {'id':book['id'],'sha256':book['sha256'],'trained_through':book['trained_through'],
        'scope':'DEVELOPMENT_REPLAY' if overlap else 'LATER_PERIOD_EVALUATION'}


def validate_binding(manifest,case_date):
    if not manifest:return None
    book=load_version(manifest['id'])
    if book['sha256']!=manifest['sha256'] or book['trained_through']!=manifest['trained_through']:raise ValueError('Portfolio playbook changed; cannot mix lessons within a run')
    if manifest['scope'] not in {'DEVELOPMENT_REPLAY','LATER_PERIOD_EVALUATION'}:raise ValueError('Invalid memory evaluation scope')
    if manifest['scope']=='LATER_PERIOD_EVALUATION' and str(case_date)<=book['trained_through']:raise ValueError('Future-derived lesson cannot enter an earlier evaluation case')
    return book


def retrieve(manifest,snapshot,pack):
    book=validate_binding(manifest,snapshot['date'])
    if not book:return []
    # Match only current evidence and technical context, never subsequent price/P&L.
    current=' '.join([snapshot.get('regime',''),snapshot.get('approved_candidate',''),snapshot.get('research_purpose',''),
                      *[d.get('title','') for d in pack.get('documents',[])]]).lower()
    if pack.get('adverse_scan',{}).get('matched_document_ids'):current+=' adverse regulatory litigation management disclosure'
    current+=' financial company research citations'
    scored=[]
    for lesson in book['lessons']:
        words=set(re.findall(r'[a-z]{4,}',lesson['applies_when'].lower()))
        score=sum(w in current for w in words)+(2 if lesson['topic']=='grounding' else 0)
        if score or lesson['topic']=='execution':scored.append((score,lesson['id'],lesson))
    from .evidence_context import model_observation,compact_json
    # Optional reminders yield space to dated source evidence and specialist hand-offs.
    budget=min(2400,max(0,26000-len(compact_json(model_observation('company_evidence',pack)))-10000))
    selected=[];used=set()
    for _,_,l in sorted(scored,key=lambda x:(-x[0],x[1])):
        if l['topic'] in used:continue
        item={k:l[k] for k in ('id','topic','lesson','applies_when')}
        if len(json.dumps(selected+[item],ensure_ascii=False))>budget:continue
        selected.append(item);used.add(l['topic'])
        if len(selected)==3:break
    return selected
