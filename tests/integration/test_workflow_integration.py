# Workflow integration tests
from unittest.mock import patch

import pytest
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner
from google.adk.workflow import Workflow
from google.genai import types

from customer_support_agent.agent import root_agent
from customer_support_agent.schemas import ShippingFaqResponse


class TestWorkflowGraphStructure:
    # Test workflow graph structure and initialization

    def test_workflow_instance(self):
        # Verify workflow instance properties
        assert isinstance(root_agent, Workflow)
        assert root_agent.name == "customer_support_agent"

    def test_workflow_has_edges(self):
        # Verify presence of workflow graph edges
        assert root_agent.graph is not None
        assert len(root_agent.graph.edges) >= 3


@pytest.mark.asyncio
class TestWorkflowExecution:
    # End-to-end integration tests for workflow execution

    async def test_unrelated_query_routes_to_decline(self):
        # Test routing of out-of-domain query to decline handler
        app = App(name="customer_support_app", root_agent=root_agent)
        runner = InMemoryRunner(app=app)

        session = await runner.session_service.create_session(
            app_name="customer_support_app", user_id="test_user"
        )

        outputs = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="What is the weather in Paris?")],
            ),
        ):
            if event.output is not None:
                outputs.append(event.output)

        assert any(
            (isinstance(out, dict) and "shipping" in str(out).lower())
            or (isinstance(out, str) and "shipping" in out.lower())
            for out in outputs
        )

    async def test_shipping_query_routes_to_faq_agent(self):
        # Test routing of shipping inquiry to FAQ agent
        app = App(name="customer_support_app", root_agent=root_agent)
        runner = InMemoryRunner(app=app)

        session = await runner.session_service.create_session(
            app_name="customer_support_app", user_id="test_user"
        )

        assert root_agent.graph is not None
        faq_node = next(
            n for n in root_agent.graph.nodes if n.name == "shipping_faq_agent"
        )

        async def mock_faq_run(*args, **kwargs):
            faq_resp = ShippingFaqResponse(
                answer="Our standard shipping rate is $5.99 for orders up to 5kg.",
                category="rates",
            )
            yield Event(output=faq_resp.model_dump())

        with patch.object(faq_node, "_run_impl", side_effect=mock_faq_run):
            outputs = []
            async for event in runner.run_async(
                user_id="test_user",
                session_id=session.id,
                new_message=types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text="What are the shipping rates for express delivery?"
                        )
                    ],
                ),
            ):
                if event.output is not None:
                    outputs.append(event.output)

            assert any(
                isinstance(out, dict) and "standard shipping rate" in str(out).lower()
                for out in outputs
            )
