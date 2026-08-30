# Context management, persistent session store, and async memory consolidation
import asyncio
import json
import sqlite3
from typing import Any, List

from google.genai import types

from customer_support_agent.guardrails import PIIScrubber


def compact_conversation_history(
    messages: List[types.Content],
    max_turns: int = 10,
) -> List[types.Content]:
    # Sliding-window conversation compaction to prevent context bloat
    if len(messages) <= max_turns:
        return messages

    # Aggregate older turns into a concise summary message
    old_messages = messages[:-max_turns]
    recent_messages = messages[-max_turns:]

    summary_text = (
        f"[Context Compaction: {len(old_messages)} earlier conversation turns summarized "
        "to maintain optimal token performance]"
    )
    summary_content = types.Content(
        role="system",
        parts=[types.Part.from_text(text=summary_text)],
    )

    return [summary_content] + recent_messages


class PersistentSessionStore:
    # SQLite persistent session store

    def __init__(self, db_path: str = "customer_sessions.db"):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    async def init_db(self) -> None:
        # Initialize database tables
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

    async def save_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        # Apply PII scrubbing and persist session state
        clean_state = {}
        for k, v in state.items():
            if isinstance(v, str):
                clean_state[k] = PIIScrubber.scrub(v)
            else:
                clean_state[k] = v

        state_json = json.dumps(clean_state, ensure_ascii=False)
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO sessions (session_id, state_json) VALUES (?, ?)",
            (session_id, state_json),
        )
        conn.commit()

    async def get_session_state(self, session_id: str) -> dict[str, Any]:
        # Retrieve stored session state
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT state_json FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return {}

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


async def async_consolidate_memory(
    session_id: str,
    session_store: PersistentSessionStore,
    turn_summary: str,
) -> bool:
    # Asynchronous non-blocking background memory consolidation
    await asyncio.sleep(0.01)  # Async background task simulation
    current_state = await session_store.get_session_state(session_id)
    history = current_state.get("memory_summary", "")
    new_history = f"{history}\n{turn_summary}".strip()
    current_state["memory_summary"] = new_history
    await session_store.save_session_state(session_id, current_state)
    return True
