# Interactive console runner script
import asyncio
import sys

from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from customer_support_agent.agent import root_agent


async def main() -> None:
    # Initialize workflow application and in-memory runner
    app = App(name="customer_support_app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name="customer_support_app",
        user_id="customer",
    )

    print("--- Customer Support Agent (Shipping Company) ---")
    print("Type 'exit' or 'quit' to end.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input or user_input.lower() in ("exit", "quit"):
            print("Session ended.")
            break

        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        async for event in runner.run_async(
            user_id="customer",
            session_id=session.id,
            new_message=message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"\nAgent: {part.text}")
            elif event.output is not None:
                if isinstance(event.output, dict):
                    if "answer" in event.output:
                        print(f"\nAgent (FAQ): {event.output['answer']}")
                    elif "message" in event.output:
                        print(f"\nAgent (Decline): {event.output['message']}")


if __name__ == "__main__":
    asyncio.run(main())
