from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class WebhookPayload(BaseModel):
    event_id: str = Field(..., description="Unique event ID for idempotency")
    event_type: str = Field(..., description="Type of event, e.g. payment_success")
    amount: float = Field(..., gt=0, description="Payment amount must be greater than zero")
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp in ISO format",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_age(cls, v: Optional[datetime]) -> datetime:
        if v is None:
            return datetime.now(timezone.utc)

        now = datetime.now(timezone.utc)

        # Ensure timezone awareness for comparison
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        # Reject webhooks older than 24 hours (86400 seconds)
        time_diff = (now - v).total_seconds()
        if time_diff > 86400:
            raise ValueError("Webhook event is older than 24 hours")

        # Reject webhooks set more than 5 minutes in the future
        if time_diff < -300:
            raise ValueError("Webhook timestamp cannot be in the future")

        return v
