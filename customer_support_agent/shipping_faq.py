# Shipping FAQ agent definition module
from google.adk.agents import LlmAgent

from customer_support_agent.prompts import SHIPPING_AGENT_CONSTITUTION
from customer_support_agent.schemas import ShippingFaqResponse
from customer_support_agent.tools import (
    calculate_shipping_rates,
    submit_return_request,
    track_package_by_number,
)

# Shipping FAQ LLM Agent powered by gemini-3.7-flash and specialized domain tools
shipping_faq_agent = LlmAgent(
    name="shipping_faq_agent",
    model="gemini-3.7-flash",
    instruction=SHIPPING_AGENT_CONSTITUTION,
    tools=[
        calculate_shipping_rates,
        track_package_by_number,
        submit_return_request,
    ],
    output_schema=ShippingFaqResponse,
    output_key="faq_response",
)
