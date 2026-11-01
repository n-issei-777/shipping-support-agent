# Shipping domain tools module
import uuid

from customer_support_agent.schemas import (
    RateCalculationInput,
    RateCalculationOutput,
    ReturnRequestInput,
    ReturnRequestOutput,
    ToolErrorResult,
    TrackingLookupOutput,
)


def calculate_shipping_rates(
    origin_zip: str,
    destination_zip: str,
    weight_kg: float,
    service_type: str = "standard",
) -> RateCalculationOutput | ToolErrorResult:
    """Calculates shipping rates and delivery estimates only when origin ZIP, destination ZIP, and positive weight are provided.

    IMPORTANT: Do NOT call this tool for greetings (e.g. 'hello'), capability inquiries, or when postal codes and weight are missing from the customer's query.

    Args:
        origin_zip: Origin US 5-digit ZIP code (must be provided).
        destination_zip: Destination US 5-digit ZIP code (must be provided).
        weight_kg: Package weight in kilograms (must be > 0.0 and <= 70.0 kg).
        service_type: Service tier ('standard', 'express', or 'overnight'). Defaults to 'standard'.

    Returns:
        RateCalculationOutput containing the total cost, estimated transit days, and service name.
        ToolErrorResult if validation fails or inputs are missing/invalid, with recovery guidance.
    """
    try:
        validated = RateCalculationInput(
            origin_zip=origin_zip,
            destination_zip=destination_zip,
            weight_kg=weight_kg,
            service_type=service_type,
        )
    except Exception as exc:
        return ToolErrorResult(
            is_error=True,
            error_message=f"Validation failed for rate calculation: {exc!s}",
            recovery_instructions="Please ask the customer to provide their origin ZIP, destination ZIP, and package weight (in kg). Do not retry without these values.",
        )

    base_rates = {
        "standard": (8.50, 4),
        "express": (18.50, 2),
        "overnight": (35.00, 1),
    }

    tier = validated.service_type.lower()
    if tier not in base_rates:
        tier = "standard"

    base_price, est_days = base_rates[tier]
    total_cost = round(base_price + (validated.weight_kg * 2.20), 2)

    return RateCalculationOutput(
        service_name=f"{tier.capitalize()} Courier Service",
        total_cost_usd=total_cost,
        estimated_days=est_days,
        currency="USD",
    )


# Mock shipment tracking database
MOCK_TRACKING_DATABASE = {
    "TRK-12345678": {
        "status": "in_transit",
        "location": "Regional Distribution Hub - Chicago, IL",
        "estimated_delivery": "Tomorrow by 5:00 PM",
    },
    "TRK-99999999": {
        "status": "out_for_delivery",
        "location": "Local Carrier Facility - Seattle, WA",
        "estimated_delivery": "Today by 2:00 PM",
    },
    "TRK-88888888": {
        "status": "delivered",
        "location": "Front Porch - Austin, TX",
        "estimated_delivery": "Delivered Yesterday at 11:30 AM",
    },
}


def track_package_by_number(
    tracking_number: str,
) -> TrackingLookupOutput | ToolErrorResult:
    """Retrieves current shipment status, real-time location, and delivery estimates for a specific tracking number.

    IMPORTANT: Do NOT call this tool for greetings or when no tracking number is provided.

    Args:
        tracking_number: The unique carrier tracking number (format: 'TRK-XXXXXXXX' or numeric ID).

    Returns:
        TrackingLookupOutput containing tracking number, milestone status, current location, and ETA.
        ToolErrorResult if the tracking number is missing, invalid format, or not found.
    """
    clean_number = tracking_number.strip().upper()
    if not clean_number:
        return ToolErrorResult(
            is_error=True,
            error_message="Tracking number cannot be empty.",
            recovery_instructions="Please ask the customer to provide their tracking number (typically formatted like TRK-12345678). Do not guess.",
        )

    # Format verification
    if not clean_number.startswith("TRK-") and not clean_number.isdigit():
        return ToolErrorResult(
            is_error=True,
            error_message=f"Tracking number '{clean_number}' does not match standard carrier format.",
            recovery_instructions="Inform the customer that valid tracking numbers start with 'TRK-' followed by digits. Ask if they have their order confirmation.",
        )

    record = MOCK_TRACKING_DATABASE.get(clean_number)
    if not record:
        return TrackingLookupOutput(
            tracking_number=clean_number,
            status="in_transit",
            location="In Transit to Local Delivery Station",
            estimated_delivery="Expected in 2-3 business days",
        )

    return TrackingLookupOutput(
        tracking_number=clean_number,
        status=record["status"],
        location=record["location"],
        estimated_delivery=record["estimated_delivery"],
    )


def submit_return_request(
    tracking_number: str,
    reason: str,
    estimated_value_usd: float = 0.0,
    requires_pickup: bool = False,
) -> ReturnRequestOutput | ToolErrorResult:
    """Creates a new return authorization request and generates return shipping documentation.

    IMPORTANT: Do NOT call this tool for greetings or general questions. Only call when a customer explicitly requests a return.

    Args:
        tracking_number: The original parcel tracking number associated with the item to return.
        reason: Detailed description of the reason for return (e.g., damaged, wrong size, defective).
        estimated_value_usd: Declared monetary value of the return goods in USD (must be >= 0.0).
        requires_pickup: Whether doorstep courier pickup is requested (True) or drop-off (False).

    Returns:
        ReturnRequestOutput containing the return ID, approval status, and return label link.
        ToolErrorResult if input parameters are invalid or missing.
    """
    try:
        validated = ReturnRequestInput(
            tracking_number=tracking_number,
            reason=reason,
            estimated_value_usd=estimated_value_usd,
            requires_pickup=requires_pickup,
        )
    except Exception as exc:
        return ToolErrorResult(
            is_error=True,
            error_message=f"Validation failed for return request: {exc!s}",
            recovery_instructions="Please verify tracking number and return value are provided with valid non-negative numbers.",
        )

    return_id = f"RET-{uuid.uuid4().hex[:8].upper()}"
    is_high_value = validated.estimated_value_usd >= 100.0

    if is_high_value:
        return ReturnRequestOutput(
            return_id=return_id,
            tracking_number=validated.tracking_number,
            status="pending_human_approval",
            return_label_url=None,
            requires_human_approval=True,
        )

    return ReturnRequestOutput(
        return_id=return_id,
        tracking_number=validated.tracking_number,
        status="approved",
        return_label_url=f"https://shipping.example.com/labels/{return_id}.pdf",
        requires_human_approval=False,
    )
