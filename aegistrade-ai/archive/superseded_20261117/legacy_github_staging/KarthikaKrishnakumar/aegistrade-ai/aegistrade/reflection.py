"""One-call development-only reflection. Human review is required before use."""
from pydantic import BaseModel, ConfigDict, Field
from .llm_research import RouterClient, SIX_SLOT, strip_json
from .agentic import scrub
from .llm_backend import create_client

class ReflectionLesson(BaseModel):
    model_config=ConfigDict(extra='forbid')
    topic:str=Field(pattern=r'^(regime|grounding|data_freshness|execution)$')
    lesson:str=Field(min_length=10,max_length=600)
    applies_when:str=Field(min_length=10,max_length=300)


def reflect_development_failure(run:dict,case_id:str,model:str):
    if run.get('settings',{}).get('dataset_split')!='development':
        raise ValueError('Lessons may only be generated from development runs')
    matches=[x for x in run.get('outputs',[]) if x.get('case_id')==case_id and x.get('config')=='C2']
    if len(matches)!=1 or not matches[0].get('model_errors'):
        raise ValueError('Select one failed C2 development output')
    failed=matches[0]
    if not any(x.get('event')=='llm_response' for x in failed.get('trajectory',[])):
        raise ValueError('Provider/account failures need an operational fix, not a paid reflection call')
    # Only the case's scored failure is supplied, never held-out labels or a full database.
    context=scrub({k:failed.get(k) for k in ['case_id','model_errors','tool_trace','handoffs']})
    from .agentic import CONFIG
    spec=CONFIG['reflection']
    prompt=SIX_SLOT.format(role=spec['role'],context=str(context)[:7000],task=spec['task'],
        constraints=spec['constraints'],format=spec['format'],examples=spec['examples'])
    client=create_client(model=model,max_calls=1,max_output_tokens_total=400)
    lesson=ReflectionLesson.model_validate(strip_json(client.complete(prompt,max_tokens=400)))
    from .security import scan_untrusted_text
    if not scan_untrusted_text(lesson.model_dump_json())['ok']:raise ValueError('Unsafe proposed lesson blocked')
    return lesson.model_dump(),client.usage
