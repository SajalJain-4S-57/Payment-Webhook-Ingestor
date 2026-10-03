from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON
from app.database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id = Column(String, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="PROCESSED")
    received_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
