"""Validated passage ingestion, primary-source metadata and corpus fingerprints."""
from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Literal
import hashlib,json,os
from pydantic import BaseModel, ConfigDict, Field, model_validator

DEFAULT_CORPUS=Path(__file__).resolve().parents[1]/'knowledge'/'corpus.jsonl'

class Passage(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:str=Field(pattern=r'^[A-Z][A-Z0-9]{1,11}-[A-Za-z0-9_-]+$',max_length=80)
    date:date
    source:str=Field(min_length=3,max_length=500)
    title:str=Field(min_length=3,max_length=200)
    text:str=Field(min_length=10,max_length=4000)
    authority:Literal['project_policy','external_reference']='project_policy'
    date_kind:Literal['authored','retrieved','published']='authored'
    topic:str='core_policy'
    source_locator:str|None=Field(default=None,max_length=1200)
    source_url:str|None=Field(default=None,pattern=r'^https?://',max_length=1200)
    published_date:date|None=None
    retrieved_date:date|None=None
    review_status:str='pending_team_review'

    @model_validator(mode='after')
    def source_required(self):
        if self.authority=='external_reference' and not self.source_url:
            raise ValueError('External references require an original-source URL')
        return self


def validate_passages(rows):
    parsed=[Passage.model_validate(r).model_dump(mode='json',exclude_none=True) for r in rows]
    if not parsed or len({r['id'] for r in parsed})!=len(parsed):raise ValueError('Corpus must be nonempty with unique passage IDs')
    return parsed


def load_corpus(path=None):
    path=Path(path or os.getenv('AEGIS_POLICY_CORPUS_PATH') or DEFAULT_CORPUS)
    text=path.read_text(encoding='utf-8')
    rows=json.loads(text) if text.lstrip().startswith('[') else [json.loads(line) for line in text.splitlines() if line.strip()]
    return validate_passages(rows)


def corpus_digest(docs):
    return hashlib.sha256(json.dumps(docs,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def corpus_info():
    docs=load_corpus()
    return {'passages':len(docs),'sha256':corpus_digest(docs),
            'project_policy_passages':sum(d['authority']=='project_policy' for d in docs),
            'external_reference_passages':sum(d['authority']=='external_reference' for d in docs),
            'source_count':len({d.get('source_url') or d.get('source_locator') or d['source'] for d in docs}),
            'scope':'Project policies, strategy/risk/data specifications and primary-source background. No current news, future returns or hidden gold answers.',
            'review_status':'Code/source checked; independent human review and evaluation labels remain required.'}
