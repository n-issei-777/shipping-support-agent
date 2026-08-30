# Polite decline handler unit tests
from customer_support_agent.decline import DECLINE_MESSAGE, decline_handler


class TestDeclineHandler:
    # Test decline handler node

    def test_decline_handler_returns_event(self):
        # Verify decline message event generation
        query = "What is the capital of Japan?"
        event = decline_handler(node_input=query)
        assert event is not None
        assert event.output is not None
        assert event.content is not None

    def test_decline_message_content(self):
        # Verify decline message covers supported shipping topics
        assert "rates" in DECLINE_MESSAGE.lower() or "pricing" in DECLINE_MESSAGE.lower()
        assert "tracking" in DECLINE_MESSAGE.lower() or "track" in DECLINE_MESSAGE.lower()
        assert "delivery" in DECLINE_MESSAGE.lower() or "shipping" in DECLINE_MESSAGE.lower()
        assert "returns" in DECLINE_MESSAGE.lower() or "return" in DECLINE_MESSAGE.lower()
