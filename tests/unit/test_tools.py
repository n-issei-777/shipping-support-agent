# Shipping domain tools unit tests

from customer_support_agent.schemas import (
    RateCalculationOutput,
    ReturnRequestOutput,
    ToolErrorResult,
    TrackingLookupOutput,
)
from customer_support_agent.tools import (
    calculate_shipping_rates,
    submit_return_request,
    track_package_by_number,
)


class TestToolDocstringsAndNaming:
    # Test tool naming and docstrings

    def test_calculate_shipping_rates_docstring(self):
        # Verify rate calculation tool docstring
        doc = calculate_shipping_rates.__doc__
        assert doc is not None
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "origin" in doc
        assert "destination" in doc

    def test_track_package_by_number_docstring(self):
        # Verify package tracking tool docstring
        doc = track_package_by_number.__doc__
        assert doc is not None
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "tracking_number" in doc

    def test_submit_return_request_docstring(self):
        # Verify return request tool docstring
        doc = submit_return_request.__doc__
        assert doc is not None
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "requires_approval" in doc or "approval" in doc or "authorization" in doc


class TestCalculateShippingRates:
    # Test rate calculation tool execution

    def test_standard_rate_calculation(self):
        # Calculate standard shipping rate
        result = calculate_shipping_rates(
            origin_zip="10001",
            destination_zip="90210",
            weight_kg=2.0,
            service_type="standard",
        )
        assert isinstance(result, RateCalculationOutput)
        assert result.total_cost_usd > 0
        assert result.estimated_days >= 1

    def test_invalid_weight_guided_error(self):
        # Verify guided error return for invalid weight
        result = calculate_shipping_rates(
            origin_zip="10001",
            destination_zip="90210",
            weight_kg=-5.0,
        )
        assert isinstance(result, ToolErrorResult)
        assert result.is_error is True
        assert len(result.recovery_instructions) > 0


class TestTrackPackageByNumber:
    # Test package tracking tool execution

    def test_existing_package_tracking(self):
        # Query valid tracking number
        result = track_package_by_number("TRK-12345678")
        assert isinstance(result, TrackingLookupOutput)
        assert result.tracking_number == "TRK-12345678"
        assert result.status in ("in_transit", "delivered", "out_for_delivery", "pending")

    def test_nonexistent_package_guided_error(self):
        # Verify guided error return for invalid tracking number format
        result = track_package_by_number("INVALID-000")
        assert isinstance(result, ToolErrorResult)
        assert result.is_error is True
        assert "TRK-" in result.recovery_instructions or "format" in result.recovery_instructions


class TestSubmitReturnRequest:
    # Test return request tool execution

    def test_standard_return_request(self):
        # Standard value return request (auto-approved)
        result = submit_return_request(
            tracking_number="TRK-12345678",
            reason="Item size does not fit",
            estimated_value_usd=45.0,
            requires_pickup=False,
        )
        assert isinstance(result, ReturnRequestOutput)
        assert result.requires_human_approval is False
        assert result.status == "approved"

    def test_high_value_return_triggers_approval(self):
        # High value return request ($100 or higher triggers approval)
        result = submit_return_request(
            tracking_number="TRK-12345678",
            reason="Expensive electronics damaged",
            estimated_value_usd=250.0,
            requires_pickup=True,
        )
        assert isinstance(result, ReturnRequestOutput)
        assert result.requires_human_approval is True
        assert result.status == "pending_human_approval"
