from fastapi import FastAPI, Header, HTTPException, status
from app.config import settings
from app.schemas import WebhookPayload

app = FastAPI(title="Payment Webhook Ingestor")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/webhook", status_code=status.HTTP_200_OK)
def receive_webhook(
    payload: WebhookPayload,
    x_webhook_secret: str = Header(None, alias="X-Webhook-Secret"),
):
    # Verify secret header
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook secret header",
        )

    return {
        "status": "success",
        "message": "Webhook received successfully",
        "event_id": payload.event_id,
    }
