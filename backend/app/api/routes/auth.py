"""Registration, login, current-session, and logout endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import AUTH_COOKIE_NAME, AUTH_COOKIE_SECURE
from backend.app.core.database import get_db, require_database
from backend.app.core.security import (
    get_current_user,
    require_frontend_origin,
    set_auth_cookie,
)
from backend.app.models.user import User
from backend.app.schemas.auth import AuthSessionRead, LoginRequest, RegisterRequest
from backend.app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=AuthSessionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_frontend_origin)],
    summary="Register an account and student profile",
)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session | None = Depends(get_db),
) -> AuthSessionRead:
    db = require_database(db)
    user, student = register_user(db, payload)
    set_auth_cookie(response, user.id)
    return AuthSessionRead(user=user, student=student)


@router.post(
    "/login",
    response_model=AuthSessionRead,
    dependencies=[Depends(require_frontend_origin)],
    summary="Log in with a username or email",
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session | None = Depends(get_db),
) -> AuthSessionRead:
    db = require_database(db)
    user, student = authenticate_user(db, payload)
    set_auth_cookie(response, user.id)
    return AuthSessionRead(user=user, student=student)


@router.get("/me", response_model=AuthSessionRead, summary="Get the current account")
def me(user: User = Depends(get_current_user)) -> AuthSessionRead:
    if user.student is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No student profile is linked to this account.",
        )
    return AuthSessionRead(user=user, student=user.student)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_frontend_origin)],
    summary="Clear the current login cookie",
)
def logout(response: Response) -> Response:
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
    )
    return response
