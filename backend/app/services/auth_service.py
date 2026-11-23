"""Account creation and password verification using Argon2id hashes."""

import secrets
from hmac import compare_digest

from fastapi import HTTPException, status
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.config import (
    DEMO_MODE,
    DEMO_PASSWORD,
    DEMO_STUDENT_BATCH,
    DEMO_STUDENT_EMAIL,
    DEMO_STUDENT_NAME,
    DEMO_STUDENT_PROGRAM,
    DEMO_USERNAME,
)
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest

password_hash = PasswordHash.recommended()
_dummy_password_hash = password_hash.hash(secrets.token_urlsafe(32))


def register_user(db: Session, payload: RegisterRequest) -> tuple[User, Student]:
    username = payload.username
    email = str(payload.email).lower()
    existing_user = db.scalar(
        select(User.id).where(or_(User.username == username, User.email == email))
    )
    existing_student = db.scalar(select(Student.id).where(Student.email == email))
    if existing_user is not None or existing_student is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username or email is already in use.",
        )

    user = User(
        username=username,
        email=email,
        password_hash=password_hash.hash(payload.password.get_secret_value()),
    )
    db.add(user)
    try:
        db.flush()
        student = Student(
            user_id=user.id,
            name=payload.name,
            email=email,
            program=payload.program,
            batch=payload.batch,
        )
        db.add(student)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username or email is already in use.",
        ) from exc

    db.refresh(user)
    db.refresh(student)
    return user, student


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, Student]:
    identifier = payload.username_or_email
    if DEMO_MODE:
        if not DEMO_USERNAME or not DEMO_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Demo sign-in is not configured on the server.",
            )
        username_matches = compare_digest(identifier, DEMO_USERNAME) or compare_digest(
            identifier, DEMO_STUDENT_EMAIL
        )
        if not username_matches or not compare_digest(
            payload.password.get_secret_value(), DEMO_PASSWORD
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.scalar(select(User).where(User.username == DEMO_USERNAME))
        if user is None:
            user = User(
                username=DEMO_USERNAME,
                email=DEMO_STUDENT_EMAIL,
                password_hash=password_hash.hash(DEMO_PASSWORD),
            )
            user.student = Student(
                name=DEMO_STUDENT_NAME,
                email=DEMO_STUDENT_EMAIL,
                program=DEMO_STUDENT_PROGRAM,
                batch=DEMO_STUDENT_BATCH,
            )
            db.add(user)
        else:
            user.password_hash = password_hash.hash(DEMO_PASSWORD)
            if user.student is None:
                user.student = Student(
                    name=DEMO_STUDENT_NAME,
                    email=DEMO_STUDENT_EMAIL,
                    program=DEMO_STUDENT_PROGRAM,
                    batch=DEMO_STUDENT_BATCH,
                )
        db.commit()
        db.refresh(user)
        return user, user.student

    user = db.scalar(
        select(User)
        .where(or_(User.username == identifier, User.email == identifier))
    )
    candidate_hash = user.password_hash if user is not None else _dummy_password_hash
    try:
        password_is_valid = password_hash.verify(
            payload.password.get_secret_value(), candidate_hash
        )
    except UnknownHashError:
        password_is_valid = False

    if user is None or not password_is_valid or user.student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user, user.student
