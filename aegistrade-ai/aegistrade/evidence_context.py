"""Compact inference views. Full validated observations stay in the tool audit."""
from .company_research import digest


def compact_json(value):
    import json
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),default=str)


def model_observation(name,observation):
    if name=='search_dated_web' and observation.get('ok'):
        return {'ok':True,'company_evidence':model_observation('company_evidence',observation.get('company_evidence',{})),
            'search_status':observation.get('search_audit',{}).get('status'),'cached':observation.get('cached',False)}
    if name!='company_evidence' or not observation.get('ok'):return observation
    fields=('ok','symbol','decision_at','status','pack_sha256','evidence_view_version','reasons','limitations','web_scan')
    result={k:observation[k] for k in fields if k in observation}
    result['coverage']={k:v for k,v in observation.get('coverage',{}).items()
                        if k in {'exchange_scan_complete','invalid_timestamp_rows','selected_documents_only'}}
    scan=observation.get('adverse_scan',{})
    result['adverse_scan']={k:v for k,v in scan.items() if k not in {'source_url'}}
    result['documents']=[];window_references={};shared_windows={}
    for d in observation.get('documents',[]):
        # Source URLs, publication/retrieval metadata and complete excerpts remain in the audit.
        item={k:d[k] for k in ('id','kind','title','available_at','extraction_status','financial_content_detected') if k in d}
        if d.get('materiality') and d['id'] in scan.get('matched_document_ids',[]):
            fields=d['materiality']
            item['materiality']={'source_windows':fields.get('source_windows',[]),
                'missing_fields':[k for k,v in fields.items() if v is None]}
            if not fields.get('source_windows'):item['materiality']=fields
            else:
                windows=[]
                for window in fields['source_windows']:
                    text=window['text']
                    if text not in window_references:
                        wid='W'+str(len(shared_windows)+1);window_references[text]=wid;shared_windows[wid]=text
                    windows.append({'fields':window['fields'],'verbatim_text_ref':window_references[text]})
                item['materiality']['source_windows']=windows
            # The windows carry all selected fields; do not repeat the same opening excerpt.
            item['excerpt']=d.get('excerpt','')[:120] if not fields.get('source_windows') else None
            item.pop('financial_content_detected',None)
            item.pop('extraction_status',None)
        else:item['excerpt']=d.get('excerpt','')
        result['documents'].append(item)
    if shared_windows:result['shared_verbatim_windows']=shared_windows
    result['omitted_documents']=observation.get('omitted_documents',[])
    result['view_provenance']={'full_observation_sha256':digest(observation),
        'scope':'Resolve every verbatim_text_ref through shared_verbatim_windows; each source keeps its fields and citation ID. Bounded source windows; full validated source observations and URLs retained in audit. Missing fields are unknown, not Nil. Issuer impact is attributed, not independently verified.'}
    return result
