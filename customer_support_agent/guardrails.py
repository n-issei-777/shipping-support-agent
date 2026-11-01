# Guardrails and PII scrubbing module
import re
from typing import ClassVar


class PIIScrubber:
    # Personal Identifiable Information (PII) scrubber

    # Credit card regular expression (13-16 digits)
    CARD_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    # Email address regular expression
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    # Phone number regular expression
    PHONE_REGEX = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
    # Social Security Number (SSN) regular expression
    SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    @classmethod
    def scrub(cls, text: str) -> str:
        # Detect and redact sensitive PII patterns in text
        if not text:
            return text

        scrubbed = cls.CARD_REGEX.sub("[REDACTED_CARD]", text)
        scrubbed = cls.EMAIL_REGEX.sub("[REDACTED_EMAIL]", scrubbed)
        scrubbed = cls.PHONE_REGEX.sub("[REDACTED_PHONE]", scrubbed)
        scrubbed = cls.SSN_REGEX.sub("[REDACTED_SSN]", scrubbed)
        return scrubbed


class SafetyGuardrail:
    # Input security and prompt injection guardrail

    INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"ignore\s+all\s+(previous|prior)\s+instructions",
        r"ignore\s+above\s+instructions",
        r"output\s+your\s+system\s+prompt",
        r"reveal\s+internal\s+instructions",
        r"you\s+are\s+now\s+in\s+dan\s+mode",
        r"system\s*:\s*override",
    ]

    @classmethod
    def validate_input(cls, user_text: str) -> tuple[bool, str | None]:
        # Validate user input for prompt injection attempts
        if not user_text:
            return True, None

        normalized = user_text.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, normalized):
                return False, "prompt_injection_detected"

        return True, None
