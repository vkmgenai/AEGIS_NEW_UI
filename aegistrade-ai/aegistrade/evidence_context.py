"""Compact inference views. Full validated observations stay in the tool audit."""
from .company_research import digest


def compact_json(value):
    import json
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),default=str)


def projection_patch(before,after,path=''):
    """Lossless JSON Pointer operations; never shorten or summarize source text."""
    if before==after:return []
    if isinstance(before,dict) and isinstance(after,dict):
        result=[]
        def child(key):return path+'/'+str(key).replace('~','~0').replace('/','~1')
        for key in sorted(before.keys()-after.keys()):result.append({'op':'remove','path':child(key)})
        for key,value in after.items():
            if key not in before:result.append({'op':'add','path':child(key),'value':value})
            else:result.extend(projection_patch(before[key],value,child(key)))
        return result
    if isinstance(before,list) and isinstance(after,list):
        result=[]
        for i in range(min(len(before),len(after))):result.extend(projection_patch(before[i],after[i],path+'/'+str(i)))
        for i in reversed(range(len(after),len(before))):result.append({'op':'remove','path':path+'/'+str(i)})
        for i in range(len(before),len(after)):result.append({'op':'add','path':path+'/'+str(i),'value':after[i]})
        return result
    return [{'op':'replace','path':path,'value':after}]


def apply_projection_patch(before,operations):
    """Reference decoder used to verify exact reconstruction before inference."""
    from copy import deepcopy
    result=deepcopy(before)
    for operation in operations:
        parts=[p.replace('~1','/').replace('~0','~') for p in operation['path'].split('/')[1:]]
        if not parts:
            result=deepcopy(operation['value']);continue
        parent=result
        for part in parts[:-1]:parent=parent[int(part)] if isinstance(parent,list) else parent[part]
        key=int(parts[-1]) if isinstance(parent,list) else parts[-1]
        if operation['op']=='remove':del parent[key]
        elif operation['op']=='add' and isinstance(parent,list):parent.insert(key,deepcopy(operation['value']))
        else:parent[key]=deepcopy(operation['value'])
    return result


class CompanyEvidenceConversation:
    """A specialist sees one full pack, then exact changes with explicit references.

    Full tool observations remain in the audit. No references cross specialists.
    """
    def __init__(self):self.previous=None;self.previous_id=None

    def render(self,name,observation,observation_id):
        view=model_observation(name,observation)
        if name not in {'company_evidence','search_dated_web'} or not observation.get('ok'):return view
        company=view.get('company_evidence',{}) if name=='search_dated_web' else view
        if not company.get('pack_sha256'):return view
        selected=company
        if self.previous is not None:
            operations=projection_patch(self.previous,company)
            if apply_projection_patch(self.previous,operations)!=company:raise ValueError('Company projection could not be reconstructed exactly')
            update={'ok':True,'company_evidence_update':{
                'base_tool_call_id':self.previous_id,'base_projection_sha256':digest(self.previous),
                'projection_sha256':digest(company),'patch':operations,
                'instructions':'Resolve the previous company projection in this conversation, then apply these JSON Pointer operations in order. An empty patch means exactly identical evidence, not missing evidence. Preserve all source text, citations and unresolved risks. Full observations remain in the audit.'}}
            if len(compact_json(update))<len(compact_json(company)):selected=update
        from copy import deepcopy
        self.previous=deepcopy(company);self.previous_id=observation_id
        if name=='search_dated_web':return {**view,'company_evidence':selected}
        return selected


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
            if fields.get('disclosure_context'):item['materiality']['disclosure_context']=fields['disclosure_context']
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
