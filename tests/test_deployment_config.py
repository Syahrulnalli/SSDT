"""Focused checks for fail-closed production settings and same-origin CSRF."""

import asyncio

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core import config, security
from backend.app.main import database_error_handler


def _production_settings(monkeypatch, *, origins=()):
    monkeypatch.setattr(config, "IS_PRODUCTION", True)
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql+psycopg://user:pass@db.example/ssdt")
    monkeypatch.setattr(config, "JWT_SECRET_KEY", "synthetic-secret-with-more-than-32-bytes")
    monkeypatch.setattr(config, "AUTH_COOKIE_SECURE", True)
    monkeypatch.setattr(config, "AUTO_CREATE_TABLES", False)
    monkeypatch.setattr(config, "SERVE_FRONTEND", True)
    monkeypatch.setattr(config, "FRONTEND_ORIGINS", origins)


def test_production_config_accepts_same_origin_without_cors_allowlist(monkeypatch):
    _production_settings(monkeypatch)
    config.validate_production_config()


@pytest.mark.parametrize(
    ("setting", "value"),
    [
        ("DATABASE_URL", None),
        ("JWT_SECRET_KEY", "too-short"),
        ("AUTH_COOKIE_SECURE", False),
        ("AUTO_CREATE_TABLES", True),
        ("SERVE_FRONTEND", False),
        ("FRONTEND_ORIGINS", ("http://public.example",)),
        ("FRONTEND_ORIGINS", ("*",)),
    ],
)
def test_production_config_rejects_unsafe_settings(monkeypatch, setting, value):
    _production_settings(monkeypatch)
    monkeypatch.setattr(config, setting, value)
    with pytest.raises(RuntimeError):
        config.validate_production_config()


def _request(host: str, origin: str) -> Request:
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",  # TLS may terminate before the ASGI server.
            "path": "/api/auth/register",
            "raw_path": b"/api/auth/register",
            "query_string": b"",
            "headers": [
                (b"host", host.encode()),
                (b"origin", origin.encode()),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 80),
        }
    )


def test_same_origin_https_write_is_allowed_without_cors_list(monkeypatch):
    monkeypatch.setattr(security, "IS_PRODUCTION", True)
    monkeypatch.setattr(security, "FRONTEND_ORIGINS", ())
    security.require_frontend_origin(_request("ssdt.example", "https://ssdt.example"))


@pytest.mark.parametrize(
    ("host", "origin"),
    [
        ("ssdt.example", "https://evil.example"),
        ("ssdt.example", "http://ssdt.example"),
        ("ssdt.example", "https://ssdt.example:444"),
        ("ssdt.example", "null"),
    ],
)
def test_cross_origin_or_insecure_production_write_is_rejected(monkeypatch, host, origin):
    monkeypatch.setattr(security, "IS_PRODUCTION", True)
    monkeypatch.setattr(security, "FRONTEND_ORIGINS", ())
    with pytest.raises(HTTPException) as exc_info:
        security.require_frontend_origin(_request(host, origin))
    assert exc_info.value.status_code == 403


def test_database_error_logs_and_response_do_not_expose_exception_details(caplog):
    request = _request("ssdt.example", "https://ssdt.example")
    sensitive_detail = "password=synthetic-secret SELECT * FROM student_records"
    response = asyncio.run(database_error_handler(request, SQLAlchemyError(sensitive_detail)))
    assert response.status_code == 503
    assert sensitive_detail not in response.body.decode()
    assert "synthetic-secret" not in caplog.text
    assert "student_records" not in caplog.text
