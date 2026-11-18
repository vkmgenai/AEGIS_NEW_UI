"""Reviewed Reflexion playbook with freeze manifest and audit notes.

The system proposes; a person decides. No lessons change hard-coded risk rules.
"""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib,json,sqlite3
from .memory import LessonStore

class ReviewedPlaybook(LessonStore):
    def __init__(self,path='data/lessons.sqlite'):
        super().__init__(path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS playbook_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        self.conn.commit()
    def _frozen(self) -> bool:
        return self.conn.execute("SELECT value FROM playbook_meta WHERE key='frozen'").fetchone() is not None
    def propose(self, topic, text, applies_when):
        if self._frozen(): raise ValueError('Frozen playbook cannot be changed')
        return super().propose(topic,text,applies_when)
    def review(self,lesson_id,decision,reason):
        if self._frozen(): raise ValueError('Frozen playbook cannot be changed')
        return super().review(lesson_id,decision,reason)
    def freeze(self,reviewer: str) -> dict:
        if not reviewer.strip(): raise ValueError('Reviewer required')
        rows=self.conn.execute("SELECT id,topic,text,condition,reviewer_reason FROM lessons WHERE status='ACCEPTED' ORDER BY id").fetchall()
        canon=json.dumps(rows,sort_keys=True,default=str)
        digest=hashlib.sha256(canon.encode()).hexdigest()
        data={'sha256':digest,'count':len(rows),'reviewer':reviewer,'frozen_at':datetime.now(timezone.utc).isoformat()}
        self.conn.execute("INSERT OR REPLACE INTO playbook_meta(key,value) VALUES ('frozen',?)",(json.dumps(data),))
        self.conn.commit()
        return data
    def freeze_info(self) -> dict|None:
        row=self.conn.execute("SELECT value FROM playbook_meta WHERE key='frozen'").fetchone()
        return json.loads(row[0]) if row else None
    def retrieve(self,topic,condition_keywords:list[str]) -> list[dict]:
        lessons=self.accepted(topic)
        tokens={t.lower() for t in condition_keywords}
        return [x for x in lessons if not x['applies_when'] or any(t in x['applies_when'].lower() for t in tokens)]

def propose_failure_lesson(error_code:str) -> dict:
    """Reproducible proposal candidates; actual LLM reflection optional for class demo."""
    known={
        'STALE_DATA':('data_freshness','Check the quote timestamp before trusting a signal.','When a quote timestamp is older than the configured threshold'),
        'ROUTING_MISMATCH':('regime','Check approved regime eligibility before choosing the strategy.','When indicators conflict with a proposed strategy'),
        'CITATION_MISSING':('grounding','Cite policy passage IDs alongside explanations.','When explaining a rule-based trading decision'),
        'DUPLICATE_ORDER':('execution','Reconcile the existing order id before any retry.','When an order API times out'),
        'BAD_LESSON':('risk','Increase trade size after losing trades to recover quickly.','When trades are losing'),
    }
    if error_code not in known: raise ValueError('Unknown failure type')
    t,lesson,condition=known[error_code]
    return {'topic':t,'lesson':lesson,'applies_when':condition, 'source_error':error_code}
