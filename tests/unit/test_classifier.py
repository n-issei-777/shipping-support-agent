# Unit tests for query classifier
import pytest
from google.genai import types

from customer_support_agent.classifier import (
    classify_query,
    determine_classification,
    extract_query_text,
)
from customer_support_agent.schemas import QueryCategory


class TestExtractQueryText:
    # Test query text extraction from various formats

    def test_extract_from_string(self):
        # Extract from plain string
        text = "Where is my package?"
        assert extract_query_text(text) == text

    def test_extract_from_content(self):
        # Extract from types.Content object
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text="Track my order #12345")],
        )
        assert extract_query_text(content) == "Track my order #12345"

    def test_extract_from_dict(self):
        # Extract from dictionary object
        data = {"query": "How much for express shipping?"}
        assert extract_query_text(data) == "How much for express shipping?"


class TestDetermineClassification:
    # Test query classification logic

    @pytest.mark.parametrize(
        "query, expected_category",
        [
            ("What are the shipping rates to Tokyo?", QueryCategory.RATES),
            ("How much does 5kg delivery cost?", QueryCategory.RATES),
            ("Can I get a shipping rate quote?", QueryCategory.RATES),
            ("Where is my package with tracking number 987654?", QueryCategory.TRACKING),
            ("Track shipment TRK-12345", QueryCategory.TRACKING),
            ("What is the status of my delivery?", QueryCategory.TRACKING),
            ("When will my parcel be delivered?", QueryCategory.DELIVERY),
            ("Can I schedule weekend delivery?", QueryCategory.DELIVERY),
            ("What is your standard delivery timeframe?", QueryCategory.DELIVERY),
            ("How do I return a damaged product?", QueryCategory.RETURNS),
            ("What is your return policy for packages?", QueryCategory.RETURNS),
            ("I need to send back an item I received", QueryCategory.RETURNS),
            ("hello", QueryCategory.GREETING),
            ("Hi there, how can you help me?", QueryCategory.GREETING),
            ("Good morning, I have a question", QueryCategory.GREETING),
            ("こんにちは", QueryCategory.GREETING),
        ],
    )
    def test_shipping_related_queries(self, query: str, expected_category: QueryCategory):
        # Verify classification for shipping queries and greetings
        result = determine_classification(query)
        assert result.is_shipping_related is True
        assert result.category == expected_category

    @pytest.mark.parametrize(
        "query",
        [
            "What is the weather like in New York today?",
            "Can you write a Python script for binary search?",
            "Who won the 2022 World Cup?",
            "Tell me a funny joke.",
            "What is the capital of France?",
        ],
    )
    def test_unrelated_queries(self, query: str):
        # Verify classification for unrelated queries
        result = determine_classification(query)
        assert result.is_shipping_related is False
        assert result.category == QueryCategory.UNRELATED


class TestClassifyQueryNode:
    # Test classification node function

    def test_shipping_query_routing(self):
        # Verify routing for shipping rate query
        query = "How much to ship a package to California?"
        event = classify_query(node_input=query)
        assert event.actions.route == "shipping_faq"
        assert event.output is not None

    def test_greeting_query_routing(self):
        # Verify routing for greeting query (routes to shipping_faq)
        query = "hello"
        event = classify_query(node_input=query)
        assert event.actions.route == "shipping_faq"
        assert event.output is not None

    def test_unrelated_query_routing(self):
        # Verify routing for unrelated query (routes to decline)
        query = "What is the best recipe for chocolate cake?"
        event = classify_query(node_input=query)
        assert event.actions.route == "decline"
        assert event.output is not None
