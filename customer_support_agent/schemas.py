# Data schema definitions
from enum import StrEnum

from pydantic import BaseModel, Field


class QueryCategory(StrEnum):
    # Customer query category
    RATES = "rates"
    TRACKING = "tracking"
    DELIVERY = "delivery"
    RETURNS = "returns"
    GREETING = "greeting"
    UNRELATED = "unrelated"


class ClassificationResult(BaseModel):
    # Query classification result model
    is_shipping_related: bool = Field(
        description="Whether query is related to shipping or support onboarding"
    )
    category: QueryCategory = Field(
        description="Identified query category (rates, tracking, delivery, returns, greeting, unrelated)"
    )
    query: str = Field(
        description="Raw user query text"
    )
    confidence: float = Field(
        default=1.0,
        description="Classification confidence score"
    )


class ShippingFaqResponse(BaseModel):
    # Shipping FAQ response model
    answer: str = Field(
        description="Detailed answer body for shipping inquiries or warm greeting"
    )
    category: str | None = Field(
        default=None,
        description="Associated shipping topic or greeting"
    )


# --- Tool Input / Output Schemas ---


class RateCalculationInput(BaseModel):
    # Rate calculation input schema
    origin_zip: str = Field(
        min_length=3,
        max_length=10,
        description="Origin 5-digit US ZIP code or postal code"
    )
    destination_zip: str = Field(
        min_length=3,
        max_length=10,
        description="Destination 5-digit US ZIP code or postal code"
    )
    weight_kg: float = Field(
        gt=0.0,
        le=70.0,
        description="Package weight in kilograms (> 0.0 and <= 70.0 kg)"
    )
    service_type: str = Field(
        default="standard",
        description="Service tier ('standard', 'express', 'overnight')"
    )


class RateCalculationOutput(BaseModel):
    # Rate calculation output schema
    service_name: str = Field(description="Name of shipping service tier")
    total_cost_usd: float = Field(description="Calculated total cost in USD")
    estimated_days: int = Field(description="Estimated transit time in business days")
    currency: str = Field(default="USD", description="Currency unit")


class TrackingLookupInput(BaseModel):
    # Tracking lookup input schema
    tracking_number: str = Field(
        min_length=5,
        description="Shipment tracking number (e.g., 'TRK-12345678')"
    )


class TrackingLookupOutput(BaseModel):
    # Tracking lookup output schema
    tracking_number: str = Field(description="Tracking identifier")
    status: str = Field(description="Current delivery status ('pending', 'in_transit', 'out_for_delivery', 'delivered')")
    location: str = Field(description="Current facility or last transit location")
    estimated_delivery: str = Field(description="Estimated delivery date/time")


class ReturnRequestInput(BaseModel):
    # Return request input schema
    tracking_number: str = Field(
        min_length=5,
        description="Original package tracking number"
    )
    reason: str = Field(
        min_length=3,
        description="Reason for item return"
    )
    estimated_value_usd: float = Field(
        ge=0.0,
        description="Declared monetary value in USD"
    )
    requires_pickup: bool = Field(
        default=False,
        description="Whether home courier pickup is requested"
    )


class ReturnRequestOutput(BaseModel):
    # Return request output schema
    return_id: str = Field(description="Generated return authorization ID")
    tracking_number: str = Field(description="Original tracking number")
    status: str = Field(description="Return authorization status ('approved', 'pending_human_approval', 'rejected')")
    return_label_url: str | None = Field(default=None, description="Downloadable return label URL")
    requires_human_approval: bool = Field(description="Whether high-value HITL approval is required")


class ToolErrorResult(BaseModel):
    # Guided tool error recovery model
    is_error: bool = Field(default=True, description="Error indicator flag")
    error_message: str = Field(description="Detailed error description")
    recovery_instructions: str = Field(description="Clear recovery instructions for LLM to guide customer")
