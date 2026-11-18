"""Versioned extractive company evidence. No generated facts or financial normalization."""
import re

VERSION='company-view-v5-substantive-body'


def materiality_fields(text):
    """Verbatim source windows, not inferred severity or monetary calculations."""
    text=_body(_lines(text))
    patterns={
        'issuer_reported_impact':(r'impact\s+on\s+(?:financial|operations?|business)',440),
        'action_context':(r'nature\s+and\s+details|(?:penalty|fine)\s+(?:of|is|has)|imposed|restrictions?',280),
        'amount_context':(r'(?<![A-Za-z])(?:INR\b|Rs\.?(?![A-Za-z])|₹)\s*\d[\d,]*(?:\.\d+)?',190),
        'status_context':(r'resolved|settled|pending|withdrawn|appeal|stayed|resign|cessation|successor|no other material',250),
        'event_context':(r'fraud|default|insolven|bankrupt|downgrade|litigation|suspend|restriction|disruption|penalt|resign',300)}
    result={};ranges=[]
    for key,(pattern,size) in patterns.items():
        found=re.search(pattern,text,re.I)
        result[key]=_bounded(text[max(0,found.start()-50):found.start()+size],size+50) if found else None
        if found:ranges.append((max(0,found.start()-50),min(len(text),found.start()+size),key))
    merged=[]
    for start,end,key in sorted(ranges):
        if merged and start<=merged[-1][1]:
            merged[-1][1]=max(merged[-1][1],end);merged[-1][2].append(key)
        else:merged.append([start,end,[key]])
    # Actual overlapping offsets from one source are merged without inferred transitions.
    result['source_windows']=[{'fields':keys,'text':text[start:end]} for start,end,keys in merged]
    result['disclosure_context']=_bounded(text,650)
    return result


def _lines(text):
    return '\n'.join(' '.join(line.split()) for line in text.splitlines() if line.strip())


def _bounded(text,limit):
    if len(text)<=limit:return text
    # Keep complete rows/sentences rather than cutting a financial value in half.
    end=text.rfind('\n',0,limit)
    if end<limit//2:end=text.rfind(' ',0,limit)
    return text[:max(end,0)].rstrip()


def _body(text):
    """Prefer the attached announcement over the exchange cover letter."""
    candidates=list(re.finditer(r'(?im)^Encl(?:osure)?[.: ].*$',text))
    for candidate in candidates:
        tail=text[candidate.end():].strip()
        if len(tail)>100:return tail
    subject=re.search(r'(?im)^(?:sub(?:ject)?\s*[.:]|dear\s+(?:sir|madam)|pursuant\s+to\b)',text)
    if subject and subject.start()<12000:return text[subject.start():]
    return text


def financial_excerpt(text,limit=2400):
    text=_lines(text)
    heading=re.search(r'(?i)(?:statement of\s+)?(?:(?:standalone|consolidated)\s+(?:un)?audited|(?:un)?audited\s+(?:standalone|consolidated))\s+financial results',text)
    # Issuer results narratives retain reporting period, basis, currency and risk context.
    metric=re.search(r'(?im)^.{0,90}(?:revenues?|ebitda|net income|net profit|profit after tax).{0,60}(?:₹|INR|Rs\.?|crore)',text)
    if metric:
        nearby=text[max(0,metric.start()-500):metric.start()+1800]
        # Prefer an early issuer results summary to later auditor/subsidiary paragraphs.
        if metric.start()<18000 and (not heading or metric.start()<heading.start()) and re.search(r'(?i)consolidated|standalone|quarter|Q[1-4]|six.month',nearby):
            start=max(0,text.rfind('\n',0,max(0,metric.start()-450)))
            return _bounded('ISSUER RESULTS CONTEXT (verbatim; preserve units, period and basis):\n'+text[start:],limit)
    # Preserve an actual statement heading, units and column headers together.
    if heading:
        start=max(0,text.rfind('\n',0,max(0,heading.start()-160)))
        return _bounded('FINANCIAL STATEMENT CONTEXT (verbatim; read column periods and basis):\n'+text[start:],limit)
    # Keep the original beginning: it can contain units/periods missing from isolated rows.
    return _bounded('DOCUMENT CONTEXT (verbatim; numerical interpretation may remain unavailable):\n'+_body(text),limit)


def announcement_excerpt(text,limit=1200):
    text=_body(_lines(text))
    # Remove only short stationery lines; retain transaction amounts and business context.
    kept=[]
    for line in text.splitlines():
        stationery=re.match(r'(?i)^(?:regd\.?\s*office|corporate office|CIN\s*:|T\.:|F\.:|scrip code|symbol\s*:|exchange plaza|bandra.kurla|phiroze|dalal street)',line)
        if stationery and not re.search(r'(?i)acquir|crore|revenue|profit|transaction|stake',line):continue
        kept.append(line)
    body='\n'.join(kept)
    if len(body)<=limit:return body
    impact=materiality_fields(body)['issuer_reported_impact']
    if impact:
        # Retain the issuer's impact section even when it follows a long cover letter.
        notice='EXTRACTIVE WINDOWS; gaps omitted. Issuer statements are not independently verified.\n'
        tail='\nISSUER IMPACT CONTEXT (verbatim):\n'+impact
        return notice+_bounded(body,max(0,limit-len(notice)-len(tail)))+tail
    return _bounded(body,limit)


def excerpt(text,kind):
    if kind=='financial_results':return financial_excerpt(text)
    if kind=='annual_report':return financial_excerpt(text,limit=1600)
    return announcement_excerpt(text,limit=1200 if kind=='announcement' else 1100)


def compact_documents(documents,has_financial_content):
    """Allocate context to usable financial facts and event bodies, not repeated metadata."""
    financial=[d for d in documents if d.kind in {'financial_results','annual_report'}
               and d.extraction_status=='readable' and has_financial_content(d.text)]
    financial.sort(key=lambda d:('press release' in d.title.lower(),d.available_at),reverse=True)
    primary=financial[0].id if financial else None
    visible=[];omitted=[]
    for d in documents:
        qualifies=d in financial
        if d.extraction_status!='readable' or (d.kind=='financial_results' and not qualifies):
            omitted.append({'id':d.id,'kind':d.kind,'available_at':d.available_at.isoformat(),
                'reason':'unreadable' if d.extraction_status!='readable' else 'not substantive financial results'})
            continue
        if d.kind in {'financial_results','annual_report'}:
            evidence=financial_excerpt(d.text,limit=2400 if d.id==primary else 500)
        else:evidence=announcement_excerpt(d.text,limit=1200 if d.kind=='announcement' else 800)
        visible.append({'id':d.id,'kind':d.kind,'title':d.title[:180],'source_url':d.source_url,
            'published_at':d.published_at.isoformat(),'available_at':d.available_at.isoformat(),
            'extraction_status':d.extraction_status,'financial_content_detected':qualifies,'excerpt':evidence})
    return visible,omitted
