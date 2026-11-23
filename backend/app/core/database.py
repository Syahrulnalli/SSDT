"""SQLAlchemy engine, session dependency, and declarative base."""

from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.config import DATABASE_URL, DEMO_MODE


class Base(DeclarativeBase):
    pass


if DEMO_MODE:
    # A real, isolated in-memory SQLite database backs the optional demo. It
    # never opens the configured PostgreSQL connection and is lost on restart.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
elif DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = None
SessionLocal = (
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    if engine
    else None
)


def get_db() -> Generator[Session | None, None, None]:
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_database(db: Session | None) -> Session:
    """Raise a safe availability error after FastAPI has validated the request."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is not configured. Set DATABASE_URL in the backend environment.",
        )
    return db
