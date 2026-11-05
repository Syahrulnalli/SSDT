"""Convenience ASGI entry point. Run with ``uvicorn app:app --reload``."""

from backend.app.main import app

__all__ = ["app"]
