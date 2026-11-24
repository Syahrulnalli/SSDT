"""Build and seed the one temporary identity used by database-independent demo mode."""

from datetime import datetime, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from backend.app.core.config import (
    DEMO_PASSWORD,
    DEMO_STUDENT_BATCH,
    DEMO_STUDENT_EMAIL,
    DEMO_STUDENT_NAME,
    DEMO_STUDENT_PROGRAM,
    DEMO_USERNAME,
)
from backend.app.models.student import Student
from backend.app.models.user import User

DEMO_USER_ID = 1
DEMO_STUDENT_ID = 1
DEMO_CREATED_AT = datetime.now(timezone.utc)


def build_demo_identity() -> User:
    """Return the canonical demo identity without connecting to any database."""
    student = Student(
        id=DEMO_STUDENT_ID,
        user_id=DEMO_USER_ID,
        name=DEMO_STUDENT_NAME,
        email=DEMO_STUDENT_EMAIL,
        program=DEMO_STUDENT_PROGRAM,
        batch=DEMO_STUDENT_BATCH,
        created_at=DEMO_CREATED_AT,
    )
    user = User(
        id=DEMO_USER_ID,
        username=DEMO_USERNAME,
        email=DEMO_STUDENT_EMAIL,
        password_hash="demo-session-identity",
        created_at=DEMO_CREATED_AT,
    )
    user.student = student
    return user


def seed_demo_identity(db: Session) -> None:
    """Seed the temporary SQLite data store so quiz/history routes have an owner."""
    if db.scalar(select(User.id).where(User.id == DEMO_USER_ID)) is not None:
        return

    db.add(
        User(
            id=DEMO_USER_ID,
            username=DEMO_USERNAME,
            email=DEMO_STUDENT_EMAIL,
            password_hash=PasswordHash.recommended().hash(secrets.token_urlsafe(32)),
            created_at=DEMO_CREATED_AT,
            student=Student(
                id=DEMO_STUDENT_ID,
                user_id=DEMO_USER_ID,
                name=DEMO_STUDENT_NAME,
                email=DEMO_STUDENT_EMAIL,
                program=DEMO_STUDENT_PROGRAM,
                batch=DEMO_STUDENT_BATCH,
                created_at=DEMO_CREATED_AT,
            ),
        )
    )
    db.commit()
