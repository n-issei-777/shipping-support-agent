# Query classification node module
import re
from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types

from customer_support_agent.schemas import ClassificationResult, QueryCategory


def extract_query_text(node_input: Any) -> str:
    # Extract text from various input types
    if isinstance(node_input, str):
        return node_input
    if isinstance(node_input, types.Content):
        text_parts = []
        for part in node_input.parts:
            if hasattr(part, "text") and part.text:
                text_parts.append(part.text)
        return " ".join(text_parts)
    if isinstance(node_input, dict):
        return str(
            node_input.get("query")
            or node_input.get("text")
            or node_input.get("content")
            or str(node_input)
        )
    return str(node_input)


# Keyword pattern collections for shipping topics
GREETING_KEYWORDS = [
    r"^\s*hello\b",
    r"^\s*hi\b",
    r"^\s*hey\b",
    r"\bgreetings\b",
    r"\bgood (morning|afternoon|evening|day)\b",
    r"\bhow are you\b",
    r"\bhow can you help\b",
    r"\bwhat can you do\b",
    r"\bcan you help me\b",
    r"\bi have a question\b",
    r"\bsupport\b",
    r"^\s*help\s*$",
    r"こんにちは",
    r"はじめまして",
    r"おはよう",
    r"こんばんは",
    r"よろしく",
]

RETURNS_KEYWORDS = [
    r"\breturn(s|ed|ing)?\b",
    r"\bsend back\b",
    r"\brefund\b",
    r"\bdamaged\b",
    r"\bdefective\b",
    r"\bexchange\b",
    r"返品",
    r"返送",
    r"返金",
    r"交換",
    r"破損",
]

RATES_KEYWORDS = [
    r"\brates?\b",
    r"\bcost\b",
    r"\bcosts?\b",
    r"\bprice\b",
    r"\bpricing\b",
    r"\bquote\b",
    r"\bfee\b",
    r"\bfees?\b",
    r"\bhow much\b",
    r"料金",
    r"配送料",
    r"運賃",
    r"見積",
    r"送料",
]

TRACKING_KEYWORDS = [
    r"\btrack\b",
    r"\btracking\b",
    r"\bwhere is\b",
    r"\bstatus\b",
    r"\bshipment trk\b",
    r"\btrk-\w+\b",
    r"\border #?\d+\b",
    r"\bpackage #?\d+\b",
    r"追跡",
    r"荷物状況",
    r"どこ",
    r"ステータス",
]

DELIVERY_KEYWORDS = [
    r"\bdeliver(y|ed|ing|s)?\b",
    r"\bparcel\b",
    r"\bpackage\b",
    r"\btimeframe\b",
    r"\bschedule\b",
    r"\bwhen will\b",
    r"\beta\b",
    r"\barrive\b",
    r"\barrival\b",
    r"配達",
    r"配送",
    r"到着",
    r"お届け",
    r"再配達",
]


def determine_classification(query_text: str) -> ClassificationResult:
    # Determine category and routing for input query text
    cleaned = query_text.strip().lower()

    # Out-of-domain rejection triggers
    unrelated_triggers = [
        r"\bweather\b",
        r"\bpython\b",
        r"\bscript\b",
        r"\bcode\b",
        r"\bbinary search\b",
        r"\bquicksort\b",
        r"\bworld cup\b",
        r"\bjoke\b",
        r"\bcapital of\b",
        r"\brecipe\b",
        r"\bwho is\b",
        r"\bwho won\b",
        r"\bwhat is the capital\b",
        r"天気",
        r"プログラミング",
        r"ジョーク",
        r"首都",
        r"料理",
    ]
    for pattern in unrelated_triggers:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=False,
                category=QueryCategory.UNRELATED,
                query=query_text,
                confidence=0.95,
            )

    # 1. Greetings and onboarding (routes to shipping FAQ agent to greet user warmly)
    for pattern in GREETING_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=True,
                category=QueryCategory.GREETING,
                query=query_text,
                confidence=0.95,
            )

    # 2. Returns and refunds (takes priority over tracking ID mentions)
    for pattern in RETURNS_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=True,
                category=QueryCategory.RETURNS,
                query=query_text,
                confidence=0.95,
            )

    # 3. Shipping rates and pricing
    for pattern in RATES_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=True,
                category=QueryCategory.RATES,
                query=query_text,
                confidence=0.95,
            )

    # 4. Shipment tracking and milestones
    for pattern in TRACKING_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=True,
                category=QueryCategory.TRACKING,
                query=query_text,
                confidence=0.95,
            )

    # 5. Delivery scheduling and transit timeframes
    for pattern in DELIVERY_KEYWORDS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return ClassificationResult(
                is_shipping_related=True,
                category=QueryCategory.DELIVERY,
                query=query_text,
                confidence=0.90,
            )

    # Default fallback to unrelated
    return ClassificationResult(
        is_shipping_related=False,
        category=QueryCategory.UNRELATED,
        query=query_text,
        confidence=0.80,
    )


def classify_query(node_input: Any, ctx: Context | None = None) -> Event:
    # Workflow classification node function
    query_text = extract_query_text(node_input)
    result = determine_classification(query_text)

    route = "shipping_faq" if result.is_shipping_related else "decline"

    # Emit clean query text as output for downstream LLM, with routing action
    return Event(
        output=query_text,
        actions=EventActions(route=route),
    )
