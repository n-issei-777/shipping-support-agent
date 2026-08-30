# Schema definition unit tests
import pytest
from pydantic import ValidationError

from customer_support_agent.schemas import (
    ClassificationResult,
    QueryCategory,
    RateCalculationInput,
    RateCalculationOutput,
    ReturnRequestInput,
    ReturnRequestOutput,
    ShippingFaqResponse,
    ToolErrorResult,
    TrackingLookupInput,
    TrackingLookupOutput,
)


class TestRateCalculationSchemas:
    # Test rate calculation schemas

    def test_valid_rate_input(self):
        # Valid rate calculation inputs
        data = RateCalculationInput(
            origin_zip="10001",
            destination_zip="90210",
            weight_kg=2.5,
            service_type="express",
        )
        assert data.weight_kg == 2.5
        assert data.service_type == "express"

    def test_invalid_weight_raises_error(self):
        # Non-positive weight raises validation error
        with pytest.raises(ValidationError):
            RateCalculationInput(
                origin_zip="10001",
                destination_zip="90210",
                weight_kg=-1.0,
            )

    def test_rate_output_serialization(self):
        # Verify rate calculation output serialization
        out = RateCalculationOutput(
            service_name="Express Courier",
            total_cost_usd=18.50,
            estimated_days=2,
            currency="USD",
        )
        d = out.model_dump()
        assert d["total_cost_usd"] == 18.50


class TestTrackingSchemas:
    # Test shipment tracking schemas

    def test_valid_tracking_input(self):
        # Valid tracking number input
        data = TrackingLookupInput(tracking_number="TRK-12345678")
        assert data.tracking_number == "TRK-12345678"

    def test_empty_tracking_number_raises_error(self):
        # Empty tracking number raises validation error
        with pytest.raises(ValidationError):
            TrackingLookupInput(tracking_number="   ")


class TestReturnRequestSchemas:
    # Test return request schemas

    def test_valid_return_input(self):
        # Valid return request input
        data = ReturnRequestInput(
            tracking_number="TRK-99999",
            reason="Damaged item received",
            estimated_value_usd=150.0,
            requires_pickup=True,
        )
        assert data.estimated_value_usd == 150.0

    def test_negative_value_raises_error(self):
        # Negative value raises validation error
        with pytest.raises(ValidationError):
            ReturnRequestInput(
                tracking_number="TRK-99999",
                reason="Damaged item",
                estimated_value_usd=-50.0,
            )


class TestToolErrorResultSchema:
    # Test guided error result schema

    def test_guided_error_result(self):
        # Verify guided error result attributes
        err = ToolErrorResult(
            is_error=True,
            error_message="Invalid zip code format",
            recovery_instructions="Please ask the customer to provide a valid 5-digit US ZIP code.",
        )
        assert err.is_error is True
        assert "5-digit" in err.recovery_instructions
