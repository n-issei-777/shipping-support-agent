# Shipping FAQ agent unit tests
from google.adk.agents import LlmAgent

from customer_support_agent.schemas import ShippingFaqResponse
from customer_support_agent.shipping_faq import shipping_faq_agent


class TestShippingFaqAgent:
    # Test shipping FAQ agent configuration

    def test_agent_instance(self):
        # Verify LlmAgent instance and configuration
        assert isinstance(shipping_faq_agent, LlmAgent)
        assert shipping_faq_agent.name == "shipping_faq_agent"
        assert shipping_faq_agent.model == "gemini-3.7-flash"

    def test_agent_instruction_contains_shipping_topics(self):
        # Verify instruction prompt covers core shipping topics
        raw_instruction = shipping_faq_agent.instruction
        assert isinstance(raw_instruction, str)
        instruction = raw_instruction.lower()
        assert "rates" in instruction or "rate" in instruction
        assert "tracking" in instruction or "track" in instruction
        assert "delivery" in instruction or "deliver" in instruction
        assert "returns" in instruction or "return" in instruction

    def test_agent_output_schema(self):
        # Verify agent output schema configuration
        assert shipping_faq_agent.output_schema == ShippingFaqResponse
