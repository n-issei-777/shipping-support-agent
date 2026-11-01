# Structured logging, distributed tracing, and intent/outcome tracking module
import contextlib
import datetime
import json
import logging
import uuid
from collections.abc import Callable, Generator
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from customer_support_agent.guardrails import PIIScrubber

# OpenTelemetry TracerProvider initialization
_provider = TracerProvider()
_exporter = InMemorySpanExporter()
_provider.add_span_processor(SimpleSpanProcessor(_exporter))
trace.set_tracer_provider(_provider)
_tracer = trace.get_tracer("customer_support_agent.tracer")


class StructuredJsonLogger:
    # Structured JSON logger

    def __init__(self, name: str = "customer_support_agent"):
        self.name = name
        self.logger = logging.getLogger(name)

    def format_entry(
        self,
        level: str,
        event: str,
        trace_id: str | None = None,
        span_id: str | None = None,
        node_path: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        # Format log entry into structured JSON string
        now = datetime.datetime.now(datetime.UTC).isoformat()
        clean_meta = {}
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, str):
                    clean_meta[k] = PIIScrubber.scrub(v)
                else:
                    clean_meta[k] = v

        entry = {
            "timestamp": now,
            "logger": self.name,
            "level": level.upper(),
            "event": event,
            "trace_id": trace_id or TraceManager.get_current_trace_id(),
            "span_id": span_id,
            "node_path": node_path,
            "session_id": session_id or clean_meta.pop("session_id", None),
            "metadata": clean_meta,
        }
        return json.dumps(entry, ensure_ascii=False)

    def info(self, event: str, **kwargs: Any) -> None:
        log_str = self.format_entry(level="INFO", event=event, **kwargs)
        self.logger.info(log_str)

    def error(self, event: str, **kwargs: Any) -> None:
        log_str = self.format_entry(level="ERROR", event=event, **kwargs)
        self.logger.error(log_str)


class TraceManager:
    # OpenTelemetry distributed tracing manager

    @classmethod
    def get_tracer(cls) -> trace.Tracer:
        return _tracer

    @classmethod
    def get_current_trace_id(cls) -> str:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.trace_id, "032x")
        return uuid.uuid4().hex

    @classmethod
    @contextlib.contextmanager
    def start_span(cls, name: str, attributes: dict[str, Any] | None = None) -> Generator[trace.Span]:
        with _tracer.start_as_current_span(name) as span:
            if attributes:
                for k, v in attributes.items():
                    span.set_attribute(k, str(v))
            yield span


class ActionRecorder:
    # Action recorder tracking execution intent and resulting outcome

    def __init__(self, action_name: str, intent_details: dict[str, Any], log_callback: Callable[[dict], None]):
        self.action_name = action_name
        self.intent_details = intent_details
        self.log_callback = log_callback
        self.outcome: Any = None

    def set_outcome(self, outcome: Any) -> None:
        self.outcome = outcome


@contextlib.contextmanager
def capture_intent_and_outcome(
    action_name: str,
    intent_details: dict[str, Any],
    log_callback: Callable[[dict], None] | None = None,
) -> Generator[ActionRecorder]:
    # Capture intended action (Intent) before execution and resulting output (Outcome) after
    logger = StructuredJsonLogger()
    callback = log_callback or (lambda entry: logger.info(event="action_lifecycle", metadata=entry))

    # 1. Record Intent
    intent_entry = {
        "stage": "intent",
        "action": action_name,
        "intent_details": intent_details,
    }
    callback(intent_entry)

    recorder = ActionRecorder(action_name, intent_details, callback)
    try:
        yield recorder
    finally:
        # 2. Record Outcome
        outcome_entry = {
            "stage": "outcome",
            "action": action_name,
            "outcome": recorder.outcome,
        }
        callback(outcome_entry)
