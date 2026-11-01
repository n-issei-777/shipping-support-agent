# Human-in-the-Loop (HITL) authorization gate unit tests
from google.adk.events.request_input import RequestInput

from customer_support_agent.hitl import check_and_request_approval, process_approval_response


class TestHITLApprovalGate:
    # Test Human-in-the-Loop approval gate

    def test_low_value_action_bypasses_approval(self):
        # Low-value actions auto-approve without interrupt
        result = check_and_request_approval(
            action_type="return_request",
            amount_usd=50.0,
            details={"tracking_number": "TRK-12345"},
        )
        assert result["requires_approval"] is False
        assert result["status"] == "auto_approved"

    def test_high_value_action_requests_human_approval(self):
        # High-value actions ($100 or higher) emit RequestInput interrupt
        result = check_and_request_approval(
            action_type="return_request",
            amount_usd=300.0,
            details={"tracking_number": "TRK-99999", "reason": "Damaged high-end camera"},
        )
        assert result["requires_approval"] is True
        assert isinstance(result["request_input"], RequestInput)
        assert result["request_input"].interrupt_id.startswith("hitl_approval:")

    def test_process_approved_response(self):
        # Process supervisor approval response
        outcome = process_approval_response(
            interrupt_id="hitl_approval:123",
            user_response="APPROVED",
        )
        assert outcome["approved"] is True
        assert outcome["status"] == "confirmed"

    def test_process_rejected_response(self):
        # Process supervisor rejection response
        outcome = process_approval_response(
            interrupt_id="hitl_approval:123",
            user_response="REJECTED",
        )
        assert outcome["approved"] is False
        assert outcome["status"] == "declined_by_supervisor"
