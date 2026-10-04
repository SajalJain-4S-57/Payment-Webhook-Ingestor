# Payment Webhook Ingestor

A production-ready, highly available **Payment Webhook Ingestion Service** built with **FastAPI**, **SQLAlchemy**, **Pydantic**, and **Docker**. 

This service provides secure webhook verification, payload schema validation, duplicate protection (idempotency), structured operational logging, active database health monitoring, and CI/CD deployment pipelines.

---

## 🌟 Key Features

- **Webhook Signature Verification**: Authenticates incoming requests via secret header validation (`X-Webhook-Secret`).
- **Payload Schema & Timestamp Validation**: Validates JSON payloads, positive transaction amounts, and enforces timestamp freshness (rejecting events older than 24 hours).
- **Idempotency & Duplicate Protection**: Prevents duplicate webhook event processing by tracking unique `event_id` keys in persistent storage.
- **Payload Size Rate-Limiting**: Rejects oversized payloads (>1MB) to guard against Denial-of-Service attacks.
- **Active Health Monitoring**: `/health` endpoint performs active database connectivity verification, returning `HTTP 503` if storage is unreachable.
- **Structured Operational Logging**: Output formatted standard logs capturing request lifecycle events without exposing sensitive credentials or payload data.
- **Multi-Environment Database Persistence**: Uses **SQLite** for zero-dependency local development and **Managed PostgreSQL** for production.
- **Containerized & Automated CI/CD**: Packaged into lightweight Docker containers with automated **GitHub Actions** workflows running pytest and Docker build verifications on every push.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.11 + FastAPI
- **ORM & Database**: SQLAlchemy (SQLite locally / PostgreSQL in production)
- **Data Validation**: Pydantic v2 & `pydantic-settings`
- **Testing**: Pytest & HTTPX TestClient
- **Containerization**: Docker (`python:3.11-slim`)
- **CI/CD Pipeline**: GitHub Actions

---

## 🚀 API Endpoints

### 1. Health Check
`GET /health`

**Response (`200 OK`)**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Receive Webhook
`POST /webhook`

**Request Headers**:
- `Content-Type`: `application/json`
- `X-Webhook-Secret`: `<YOUR_WEBHOOK_SECRET>`

**Request Body**:
```json
{
  "event_id": "evt_1001",
  "event_type": "payment_success",
  "amount": 250.00,
  "timestamp": "2026-10-05T00:00:00Z"
}
```

**Success Response (`200 OK`)**:
```json
{
  "status": "success",
  "message": "Webhook received and stored successfully",
  "event_id": "evt_1001"
}
```

**Duplicate Event Response (`200 OK`)**:
```json
{
  "status": "ignored",
  "message": "Duplicate event already processed",
  "event_id": "evt_1001"
}
```

---

## ⚙️ Local Setup & Installation

### 1. Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/SajalJain-4S-57/Payment-Webhook-Ingestor.git
cd Payment-Webhook-Ingestor

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

### 4. Run Development Server
```bash
uvicorn app.main:app --reload
```
Access interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

---

## 🧪 Running Automated Tests

Run the full automated unit and integration test suite:
```bash
pytest -v
```

---

## 🐳 Running with Docker

### Build Image:
```bash
docker build -t webhook-service .
```

### Run Container:
```bash
docker run -d -p 8000:8000 --name webhook-container \
  -e DATABASE_URL=sqlite:///./webhooks.db \
  -e WEBHOOK_SECRET=your-local-secret \
  webhook-service
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
