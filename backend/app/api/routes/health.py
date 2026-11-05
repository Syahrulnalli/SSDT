"""API, PostgreSQL, and Groq readiness endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import DATABASE_URL, GROQ_API_KEY, GROQ_MODEL
from backend.app.core.database import get_db, require_database
from backend.app.services.groq_service import GroqServiceError, test_groq_connection

router = APIRouter(tags=["health"])


@router.get("/health", summary="Check API process health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "database_configured": bool(DATABASE_URL)}


@router.get("/health/database", summary="Check PostgreSQL connectivity")
def database_health(db: Session | None = Depends(get_db)) -> dict[str, str]:
    db = require_database(db)
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is configured but unavailable.",
        ) from exc
    return {"status": "ok", "database": "postgresql"}


@router.get("/health/groq", summary="Check Groq configuration and connectivity")
async def groq_health() -> dict[str, str | bool]:
    configured = bool(GROQ_API_KEY)
    if not configured:
        return {
            "configured": False,
            "model": GROQ_MODEL,
            "connected": False,
            "error": "GROQ_API_KEY is not configured.",
        }

    try:
        await test_groq_connection()
    except GroqServiceError as exc:
        return {
            "configured": True,
            "model": GROQ_MODEL,
            "connected": False,
            "error": str(exc),
        }

    return {
        "configured": True,
        "model": GROQ_MODEL,
        "connected": True,
        "message": "Groq returned a response from the configured model.",
    }
