# Polite decline handler node module
from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.genai import types

DECLINE_MESSAGE = (
    "Thank you for contacting our customer support. "
    "I specialize only in shipping-related inquiries, including shipping rates, package tracking, "
    "delivery timelines, and returns. I am unable to assist with queries outside these shipping services. "
    "Please let me know if you have any questions regarding your shipment, rates, tracking, delivery, or returns."
)


def decline_handler(node_input: Any, ctx: Context | None = None) -> Event:
    # Generate polite decline message for out-of-domain inquiries
    return Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=DECLINE_MESSAGE)],
        ),
        output={"status": "declined", "message": DECLINE_MESSAGE},
    )
