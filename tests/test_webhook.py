from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_webhook_success():
    payload = {
        "event_id": "evt_123",
        "event_type": "payment_success",
        "amount": 5000.0,
    }
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Webhook received successfully",
        "event_id": "evt_123",
    }


def test_webhook_invalid_secret():
    payload = {
        "event_id": "evt_123",
        "event_type": "payment_success",
        "amount": 5000.0,
    }
    headers = {"X-Webhook-Secret": "wrong-secret"}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 401


def test_webhook_missing_secret():
    payload = {
        "event_id": "evt_123",
        "event_type": "payment_success",
        "amount": 5000.0,
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 401


def test_webhook_invalid_payload():
    payload = {"event_id": "evt_123"}  # missing event_type and amount
    headers = {"X-Webhook-Secret": settings.WEBHOOK_SECRET}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity
