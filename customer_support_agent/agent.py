# Root workflow agent definition
from google.adk.workflow import START, Workflow

from customer_support_agent.classifier import classify_query
from customer_support_agent.decline import decline_handler
from customer_support_agent.shipping_faq import shipping_faq_agent

# Define the graph workflow
root_agent = Workflow(
    name="customer_support_agent",
    description="Customer support graph workflow agent for a shipping company.",
    edges=[
        (START, classify_query),
        (
            classify_query,
            {
                "shipping_faq": shipping_faq_agent,
                "decline": decline_handler,
            },
        ),
    ],
)
