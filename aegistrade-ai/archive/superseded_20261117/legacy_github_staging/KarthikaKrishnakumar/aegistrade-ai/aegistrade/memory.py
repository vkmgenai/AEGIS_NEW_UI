"""Candidate lessons playbook. Human review required; only accepted lessons are retrievable."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
import uuid

class LessonStore:
    def __init__(self,path="aegistrade_lessons.sqlite"):
        self.conn=sqlite3.connect(str(path))
        self.conn.execute("CREATE TABLE IF NOT EXISTS lessons (id TEXT PRIMARY KEY, topic TEXT, text TEXT, condition TEXT, status TEXT, reviewer_reason TEXT, created TEXT)")
        self.conn.commit()

    def propose(self,topic:str,text:str,applies_when:str) -> str:
        lesson_id=uuid.uuid4().hex[:12]
        self.conn.execute("INSERT INTO lessons VALUES(?,?,?,?,?,?,?)",
                          (lesson_id,topic,text,applies_when,"PENDING","",datetime.now(timezone.utc).isoformat()))
        self.conn.commit()
        return lesson_id

    def review(self,lesson_id:str,decision:str,reason:str):
        if decision not in {"ACCEPT","REJECT"}:
            raise ValueError("Decision must be ACCEPT/REJECT")
        if not reason.strip():
            raise ValueError("Human reviewer must provide a reason")
        status="ACCEPTED" if decision=="ACCEPT" else "REJECTED"
        cur=self.conn.execute("UPDATE lessons SET status=?, reviewer_reason=? WHERE id=? AND status='PENDING'",
                              (status,reason,lesson_id))
        self.conn.commit()
        if cur.rowcount!=1:
            raise ValueError("Lesson missing or has already been reviewed")

    def accepted(self,topic:str) -> list[dict]:
        rows=self.conn.execute("SELECT id,topic,text,condition,reviewer_reason FROM lessons WHERE topic=? AND status='ACCEPTED'",(topic,)).fetchall()
        return [{"id":r[0],"topic":r[1],"text":r[2],"applies_when":r[3],"reviewer_reason":r[4]} for r in rows]

    def all_lessons(self):
        return self.conn.execute("SELECT id,topic,text,condition,status,reviewer_reason FROM lessons ORDER BY created").fetchall()
