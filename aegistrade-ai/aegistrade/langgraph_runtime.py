"""Shared persistent LangGraph infrastructure.

The SQLite database stores orchestration checkpoints only. Financial portfolio
state and immutable ledgers remain in their existing versioned JSON artifacts.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
import os

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


def checkpoint_path() -> Path:
    path = Path(os.getenv("AEGIS_DATA_DIR", "data")) / "langgraph" / "checkpoints.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def graph_config(thread_id: str, *, checkpoint_ns: str = "") -> dict:
    if not thread_id or len(thread_id) > 240:
        raise ValueError("A bounded LangGraph thread ID is required")
    return {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns}}


@contextmanager
def sync_checkpointer():
    """Open the durable SQLite checkpointer for one synchronous graph call."""
    with SqliteSaver.from_conn_string(str(checkpoint_path())) as saver:
        saver.setup()
        yield saver


@asynccontextmanager
async def async_checkpointer():
    """Open the durable SQLite checkpointer for one asynchronous graph call."""
    async with AsyncSqliteSaver.from_conn_string(str(checkpoint_path())) as saver:
        await saver.setup()
        yield saver

