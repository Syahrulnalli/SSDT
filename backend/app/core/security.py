"""Password-adjacent token and cookie security helpers for the SSDT API."""

from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_COOKIE_NAME,
    AUTH_COOKIE_SECURE,
    FRONTEND_ORIGINS,
    IS_PRODUCTION,
    JWT_SECRET_KEY,
)
from backend.app.core.database import get_db, require_database
from backend.app.models.user import User

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "ssdt-api"
JWT_AUDIENCE = "ssdt-web"


def ensure_auth_is_configured() -> None:
    if len(JWT_SECRET_KEY.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured. Set a random JWT_SECRET_KEY of at least 32 bytes.",
        )


def create_access_token(user_id: int) -> str:
    ensure_auth_is_configured()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": expires,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def set_auth_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_access_token(user_id),
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def require_frontend_origin(request: Request) -> None:
    """Reject cross-site writes even if a browser sends a simple request."""
    origin = request.headers.get("origin", "").rstrip("/")
    if origin and origin in FRONTEND_ORIGINS:
        return

    # A same-origin React deployment needs no CORS allowlist entry. Compare
    # the browser Origin with Host (not forwarded scheme) so TLS termination
    # at the hosting proxy does not break the check. Cross-site Origins still
    # fail because their hostname does not match the request Host.
    try:
        parsed_origin = urlsplit(origin)
        parsed_host = urlsplit(f"//{request.headers.get('host', '')}")
        origin_port = parsed_origin.port or (443 if parsed_origin.scheme == "https" else 80)
        host_port = parsed_host.port or (443 if IS_PRODUCTION else origin_port)
        same_host = (
            parsed_origin.scheme in {"http", "https"}
            and parsed_origin.hostname is not None
            and parsed_origin.hostname.casefold() == (parsed_host.hostname or "").casefold()
            and origin_port == host_port
            and not parsed_origin.username
            and not parsed_origin.password
            and parsed_origin.path in {"", "/"}
            and not parsed_origin.query
            and not parsed_origin.fragment
            and (not IS_PRODUCTION or parsed_origin.scheme == "https")
        )
    except ValueError:
        same_host = False

    if not origin or not same_host:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )


def get_current_user(
    token: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
    db: Session | None = Depends(get_db),
) -> User:
    ensure_auth_is_configured()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["sub", "iat", "exp", "iss", "aud"]},
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        ) from exc

    db = require_database(db)
    user = db.scalar(
        select(User).options(joinedload(User.student)).where(User.id == user_id)
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    return user
