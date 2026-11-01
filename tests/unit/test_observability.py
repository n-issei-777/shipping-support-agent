# Observability, structured logging, and distributed tracing unit tests
import json

from customer_support_agent.observability import (
    StructuredJsonLogger,
    TraceManager,
    capture_intent_and_outcome,
)


class TestStructuredJsonLogger:
    # Test structured JSON logging

    def test_json_log_format(self):
        # Verify log output format is valid JSON containing metadata
        logger = StructuredJsonLogger(name="test_logger")
        log_entry = logger.format_entry(
            level="INFO",
            event="workflow_started",
            trace_id="test-trace-123",
            metadata={"session_id": "sess-456", "query": "Where is my package?"},
        )
        parsed = json.loads(log_entry)
        assert parsed["level"] == "INFO"
        assert parsed["event"] == "workflow_started"
        assert parsed["trace_id"] == "test-trace-123"
        assert parsed["session_id"] == "sess-456"
        assert "timestamp" in parsed


class TestTraceManager:
    # Test OpenTelemetry distributed tracing

    def test_start_span_creates_trace_context(self):
        # Verify span creation and trace context generation
        tracer = TraceManager.get_tracer()
        assert tracer is not None
        with TraceManager.start_span("test_node_span") as span:
            assert span is not None
            trace_id = TraceManager.get_current_trace_id()
            assert trace_id is not None
            assert len(trace_id) > 0


class TestIntentVsOutcomeCapture:
    # Test intent vs. outcome recording

    def test_intent_and_outcome_recorded(self):
        # Verify recording of intent before action and outcome afterward
        events = []

        def dummy_logger(entry: dict):
            events.append(entry)

        with capture_intent_and_outcome(
            action_name="track_package_by_number",
            intent_details={"tracking_number": "TRK-12345"},
            log_callback=dummy_logger,
        ) as recorder:
            recorder.set_outcome({"status": "in_transit", "eta_days": 2})

        assert len(events) == 2
        assert events[0]["stage"] == "intent"
        assert events[0]["action"] == "track_package_by_number"
        assert events[1]["stage"] == "outcome"
        assert events[1]["outcome"]["status"] == "in_transit"
