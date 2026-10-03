from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.schemas import WebhookPayload
from app.database import engine, Base, get_db
from app.models import WebhookEvent
from app.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(title="Payment Webhook Ingestor", lifespan=lifespan)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Verify DB connectivity on health check
        db.execute(Base.metadata.tables["webhook_events"].select().limit(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed - Database error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )


@app.post("/webhook", status_code=status.HTTP_200_OK)
def receive_webhook(
    payload: WebhookPayload,
    x_webhook_secret: str = Header(None, alias="X-Webhook-Secret"),
    db: Session = Depends(get_db),
):
    logger.info(f"Webhook received. event_id={payload.event_id} event_type={payload.event_type}")

    # 1. Verify secret header
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        logger.warning(
            f"Unauthorized webhook attempt. event_id={payload.event_id} - Invalid/missing secret header."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook secret header",
        )

    # 2. Idempotency Check - Duplicate protection using event_id
    try:
        existing_event = (
            db.query(WebhookEvent)
            .filter(WebhookEvent.event_id == payload.event_id)
            .first()
        )
    except Exception as e:
        logger.error(f"Database query error during idempotency check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operational failure",
        )

    if existing_event:
        logger.info(
            f"Duplicate webhook ignored. event_id={payload.event_id} status=PROCESSED_PREVIOUSLY"
        )
        return {
            "status": "ignored",
            "message": "Duplicate event already processed",
            "event_id": payload.event_id,
        }

    # 3. Store event in database
    try:
        db_event = WebhookEvent(
            event_id=payload.event_id,
            event_type=payload.event_type,
            payload=payload.model_dump(),
            status="PROCESSED",
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        logger.info(
            f"Webhook stored successfully. event_id={payload.event_id} event_type={payload.event_type}"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to store webhook in database. event_id={payload.event_id} error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist webhook event due to database error",
        )

    return {
        "status": "success",
        "message": "Webhook received and stored successfully",
        "event_id": payload.event_id,
    }
