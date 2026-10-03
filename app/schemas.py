from pydantic import BaseModel, Field


class WebhookPayload(BaseModel):
    event_id: str = Field(..., description="Unique event ID for idempotency")
    event_type: str = Field(..., description="Type of event, e.g. payment_success")
    amount: float = Field(..., description="Payment amount")
