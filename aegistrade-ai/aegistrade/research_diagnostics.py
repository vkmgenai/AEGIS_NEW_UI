"""Safe field-level research diagnostics, including read-only legacy trace analysis."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from pydantic import ValidationError
from .llm_research import MarketJudgement,StrategyJudgement,CriticJudgement,SingleJudgement

SCHEMAS={'market':MarketJudgement,'strategy':StrategyJudgement,'critic':CriticJudgement,'single':SingleJudgement}


class ResearchStop(ValueError):
    def __init__(self,code,message,category='EVIDENCE'):
        self.code=code;self.message=message;self.category=category
        super().__init__(message)


def inference_diagnostic(usage,role=None):
    """Expose controlled transport codes, never arbitrary provider exception text."""
    failed=next((u for u in reversed(usage) if u.get('error')),None)
    if not failed:return None
    code=failed.get('error_code');http=failed.get('http_status')
    messages={
        'CODEX_TIMEOUT':'Codex did not finish before the local CLI timeout. The invocation was stopped. This does not establish a login or quota problem.',
        'CODEX_OUTPUT_INVALID':'Codex returned output the adapter could not validate. Inspect the response-format diagnostics; this does not establish an account-credit problem.',
        'CODEX_QUOTA':'Codex reported an account usage/rate limit. Check the account allowance before consenting to retry.',
        'CODEX_AUTH_REQUIRED':'Codex ChatGPT sign-in is unavailable. Check login status in Terminal.',
        'CODEX_MODEL_UNAVAILABLE':'The selected CLI model is unavailable to this account. Check the configured model.',
        'CODEX_TOOL_VIOLATION':'Unexpected native CLI tool output was blocked; inspect the adapter configuration.',
        'CODEX_EXEC_FAILED':'Codex could not finish its invocation. Inspect local execution/connectivity diagnostics before retrying.',
    }
    if code not in messages:
        code='HTTP_'+str(http) if isinstance(http,int) else 'INFERENCE_FAILED'
        message={401:'Provider authentication was rejected.',402:'Provider payment/account access was rejected.',
                 429:'Provider reported a rate/usage limit.'}.get(http,'Inference execution failed; inspect its saved transport status.')
    else:message=messages[code]
    diagnostic={'code':code,'category':'PROVIDER','agent':role,'message':message}
    if isinstance(failed.get('latency_s'),(int,float)):diagnostic['elapsed_seconds']=failed['latency_s']
    if isinstance(failed.get('timeout_seconds'),(int,float)):diagnostic['timeout_seconds']=failed['timeout_seconds']
    if failed.get('invalid_reason') in {'Invalid response envelope','Invalid virtual calls','Unexpected virtual call',
        'Tool request outside declared schema','Invalid final response envelope','No successful Codex completion event',
        'CLI final envelope exceeds response size bound','CLI output exceeds adapter bounds'}:
        diagnostic['invalid_reason']=failed['invalid_reason']
    if failed.get('validation_stage') in {'event_stream','answer_file','response_envelope','virtual_tool_arguments','specialist_content'}:
        diagnostic['validation_stage']=failed['validation_stage']
        error=failed.get('json_error',{})
        diagnostic['json_error']={k:error[k] for k in ('line','column','position') if isinstance(error.get(k),int)}
        if failed.get('invalid_reason')=='Malformed JSON at '+failed['validation_stage']:
            diagnostic['invalid_reason']=failed['invalid_reason']
    return diagnostic


def field_limits(schema):
    """Generate prompt limits from the real schema; keep the prompt compact."""
    root=schema.model_json_schema();found={}
    def visit(node,path):
        if '$ref' in node:node=root['$defs'][node['$ref'].rsplit('/',1)[-1]]
        bounds={k:node[k] for k in ('minLength','maxLength','minItems','maxItems') if k in node}
        if bounds:found[path]=bounds
        for name,child in node.get('properties',{}).items():visit(child,path+'.'+name if path else name)
    visit(root,'');return found


def validation_diagnostic(exc,role,*,payload=None):
    if isinstance(exc,ResearchStop):
        return {'code':exc.code,'category':exc.category,'agent':role,'message':exc.message}
    if isinstance(exc,ValidationError):
        issues=[]
        for error in exc.errors(include_input=False,include_url=False)[:8]:
            path=error['loc'];field='.'.join(map(str,path));kind=error['type'];ctx=error.get('ctx',{})
            current=payload
            for part in path:
                try:current=current[part]
                except (KeyError,TypeError,IndexError):current=None;break
            actual=len(current) if isinstance(current,(str,list,dict)) else None
            if kind in {'string_too_long','string_too_short'}:
                bound=ctx.get('max_length',ctx.get('min_length'));comparison='at most' if kind=='string_too_long' else 'at least'
                message=f'{field} must contain {comparison} {bound} characters'
                if actual is not None:message+=f' (received {actual})'
            elif kind in {'too_long','too_short'}:
                bound=ctx.get('max_length',ctx.get('min_length'));comparison='at most' if kind=='too_long' else 'at least'
                message=f'{field} must contain {comparison} {bound} items'
            elif kind=='missing':message=f'{field} is required'
            elif kind=='extra_forbidden':message=f'{field} is not an allowed field'
            else:message=f'{field} does not match the required schema ({kind})'
            issues.append({'field':field,'type':kind,'message':message})
        return {'code':'OUTPUT_SCHEMA_INVALID','category':'SCHEMA','agent':role,'issues':issues,
                'message':'; '.join(x['message'] for x in issues)}
    if isinstance(exc,json.JSONDecodeError):
        return {'code':'OUTPUT_JSON_INVALID','category':'SCHEMA','agent':role,'message':'Return one valid JSON object without markdown or commentary.'}
    # Only known application messages are exposed. Arbitrary provider exceptions may contain secrets.
    known={
        'Adverse event risk is material or remains unknown':('ADVERSE_RISK_BLOCKED','EVIDENCE'),
        'Adverse disclosure coverage is incomplete':('ADVERSE_SCAN_INCOMPLETE','EVIDENCE'),
        'A completed cited adverse-disclosure scan is required':('ADVERSE_SCAN_CITATION_REQUIRED','EVIDENCE'),
        'Limited financial coverage must be disclosed as LIMITED':('LIMITED_COVERAGE_DISCLOSURE_REQUIRED','EVIDENCE'),
        'Shared LLM budget exhausted':('CALL_BUDGET_EXHAUSTED','BUDGET'),
        'Output budget exhausted':('OUTPUT_BUDGET_EXHAUSTED','BUDGET'),
        'Context budget exceeded; evidence was not silently removed':('CONTEXT_BUDGET_EXCEEDED','BUDGET'),
        'Specialist correction budget exhausted':('CORRECTION_BUDGET_EXHAUSTED','SCHEMA'),
        'Required evidence missing':('REQUIRED_TOOLS_MISSING','EVIDENCE'),
        'Market hand-off contradicts code evidence':('MARKET_REGIME_CONFLICT','POLICY'),
        'Action conflicts with research purpose':('PORTFOLIO_ACTION_CONFLICT','POLICY'),
        'Strategy conflicts with code':('STRATEGY_ROUTE_CONFLICT','POLICY'),
        'Unsupported citation':('POLICY_CITATION_UNSUPPORTED','EVIDENCE'),
        'A project-policy citation is required for a route decision':('PROJECT_POLICY_CITATION_REQUIRED','EVIDENCE'),
        'Company citation not observed/readable':('COMPANY_CITATION_UNSUPPORTED','EVIDENCE'),
        'A financial filing with financial content is required':('FINANCIAL_CITATION_REQUIRED','EVIDENCE'),
        'Insufficient company evidence':('COMPANY_EVIDENCE_INSUFFICIENT','EVIDENCE'),
        'Company research requires review or has insufficient evidence':('COMPANY_ASSESSMENT_BLOCKED','EVIDENCE'),
        'Unsafe output blocked':('UNSAFE_OUTPUT','POLICY'),
    }
    if isinstance(exc,ValueError) and str(exc) in known:
        code,category=known[str(exc)]
        return {'code':code,'category':category,'agent':role,'message':str(exc)}
    return {'code':'RESEARCH_EXECUTION_FAILED','category':'EXECUTION','agent':role,
            'message':'Research could not finish. Inspect the saved tool and inference trace.'}


def diagnose_legacy_output(output):
    """Explain historical generic schema errors without rewriting signed evidence."""
    transport=inference_diagnostic(output.get('usage',[]),output.get('failure',{}).get('agent'))
    if transport:
        return {**transport,'source':'saved_transport_usage',
                'unproductive_revision_after_rejection':output.get('handoffs',{}).get('critic',{}).get('payload',{}).get('accept') is False
                    and any(e.get('event')=='replan' and e.get('agent')=='supervisor' for e in output.get('trajectory',[]))}
    if output.get('failure'):return output['failure']
    if output.get('guard_pass') or not any('BLOCK: ValidationError;' in x for x in output.get('model_errors',[])):return None
    for event in reversed(output.get('trajectory',[])):
        if event.get('event')!='llm_response':continue
        role=event.get('agent');content=event.get('message',{}).get('content')
        if role not in SCHEMAS or not content:continue
        try:
            payload=json.loads(content)
            SCHEMAS[role].model_validate(payload)
        except ValidationError as exc:
            return {**validation_diagnostic(exc,role,payload=payload),'source':'saved_response_revalidation'}
        except (ValueError,TypeError):continue
        break
    return None


@lru_cache(maxsize=256)
def _saved_failure(path,mtime_ns):
    try:return diagnose_legacy_output(json.loads(Path(path).read_text()))
    except (OSError,ValueError,TypeError,KeyError):return None


def saved_failure(path):
    try:return _saved_failure(str(path),path.stat().st_mtime_ns)
    except OSError:return None
