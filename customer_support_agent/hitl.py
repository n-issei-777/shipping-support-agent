# Human-in-the-Loop (HITL) authorization gate module
import uuid
from typing import Any

from google.adk.events.request_input import RequestInput


def check_and_request_approval(
    action_type: str,
    amount_usd: float,
    details: dict[str, Any],
) -> dict[str, Any]:
    # Human approval gate for high-stakes actions
    APPROVAL_THRESHOLD_USD = 100.0

    if amount_usd < APPROVAL_THRESHOLD_USD:
        return {
            "requires_approval": False,
            "status": "auto_approved",
            "action_type": action_type,
            "amount_usd": amount_usd,
        }

    # Generate approval interrupt request for high-value action
    approval_id = f"hitl_approval:{uuid.uuid4().hex[:8]}"
    prompt_message = (
        f"[SUPERVISOR APPROVAL REQUIRED] Action '{action_type}' for amount ${amount_usd:.2f} "
        f"exceeds standard threshold (${APPROVAL_THRESHOLD_USD:.2f}). Details: {details}. "
        "Please respond with 'APPROVED' to execute or 'REJECTED' to decline."
    )

    req_input = RequestInput(
        interrupt_id=approval_id,
        message=prompt_message,
    )

    return {
        "requires_approval": True,
        "status": "pending_approval",
        "interrupt_id": approval_id,
        "request_input": req_input,
    }


def process_approval_response(
    interrupt_id: str,
    user_response: str,
) -> dict[str, Any]:
    # Process human supervisor approval decision
    decision = user_response.strip().upper()
    if decision == "APPROVED":
        return {
            "interrupt_id": interrupt_id,
            "approved": True,
            "status": "confirmed",
            "message": "Action was approved by supervisor and completed successfully.",
        }

    return {
        "interrupt_id": interrupt_id,
        "approved": False,
        "status": "declined_by_supervisor",
        "message": "Action was declined by supervisor.",
    }
