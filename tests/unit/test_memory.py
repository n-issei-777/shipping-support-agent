# Context management, persistent memory, and async storage unit tests
import pytest
from google.genai import types

from customer_support_agent.memory import (
    PersistentSessionStore,
    async_consolidate_memory,
    compact_conversation_history,
)


class TestHistoryCompaction:
    # Test conversation history compaction

    def test_compaction_reduces_long_history(self):
        # Verify sliding-window compaction on long message histories
        messages = [
            types.Content(
                role="user" if i % 2 == 0 else "model",
                parts=[types.Part.from_text(text=f"Turn message {i}")],
            )
            for i in range(20)
        ]
        compacted = compact_conversation_history(messages, max_turns=6)
        assert len(compacted) <= 7  # Summary message + recent turns


class TestPersistentSessionStore:
    # Test SQLite persistent session storage

    @pytest.mark.asyncio
    async def test_save_and_retrieve_session_data(self):
        # Verify saving and retrieving session state
        store = PersistentSessionStore(db_path=":memory:")
        await store.init_db()

        await store.save_session_state(
            session_id="sess_001",
            state={"customer_id": "cust_123", "last_tracking": "TRK-987"},
        )

        retrieved = await store.get_session_state("sess_001")
        assert retrieved["customer_id"] == "cust_123"
        assert retrieved["last_tracking"] == "TRK-987"


class TestAsyncMemoryOperations:
    # Test asynchronous memory operations

    @pytest.mark.asyncio
    async def test_async_memory_consolidation(self):
        # Verify asynchronous non-blocking memory consolidation
        store = PersistentSessionStore(db_path=":memory:")
        await store.init_db()

        task = await async_consolidate_memory(
            session_id="sess_002",
            session_store=store,
            turn_summary="Customer requested rates to 90210.",
        )
        assert task is True

        state = await store.get_session_state("sess_002")
        assert "Customer requested rates to 90210." in state.get("memory_summary", "")
