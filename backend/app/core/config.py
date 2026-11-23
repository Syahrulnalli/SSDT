"""Environment-backed application settings."""

import os

from dotenv import load_dotenv

load_dotenv()


def _postgres_url() -> str | None:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        return None
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value.removeprefix("postgres://")
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value.removeprefix("postgresql://")
    if not value.startswith("postgresql+psycopg://"):
        raise ValueError("DATABASE_URL must point to PostgreSQL using the psycopg driver.")
    return value


DEMO_MODE = os.getenv("DEMO_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}
DATABASE_URL = None if DEMO_MODE else _postgres_url()
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "").strip().lower()
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "")
DEMO_STUDENT_NAME = os.getenv("DEMO_STUDENT_NAME", "Syahrul Nalli").strip() or "Syahrul Nalli"
DEMO_STUDENT_EMAIL = os.getenv("DEMO_STUDENT_EMAIL", "demo@example.com").strip().lower()
DEMO_STUDENT_PROGRAM = os.getenv("DEMO_STUDENT_PROGRAM", "BCA (AI/ML)").strip() or "BCA (AI/ML)"
DEMO_STUDENT_BATCH = os.getenv("DEMO_STUDENT_BATCH", "Demo").strip() or "Demo"
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"
SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "false").strip().lower() in {"1", "true", "yes", "on"}
FRONTEND_ORIGINS = tuple(
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "" if IS_PRODUCTION else "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
)
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").strip().lower() in {
    "1", "true", "yes", "on"
}
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b"
SKILL_GAP_THRESHOLD = float(os.getenv("SKILL_GAP_THRESHOLD", "60"))
SKILL_STRENGTH_THRESHOLD = float(os.getenv("SKILL_STRENGTH_THRESHOLD", "80"))
if not 0 <= SKILL_GAP_THRESHOLD < SKILL_STRENGTH_THRESHOLD <= 100:
    raise ValueError("Skill thresholds must satisfy 0 <= gap < strength <= 100.")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "ssdt_session").strip() or "ssdt_session"
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "true").strip().lower() in {
    "1", "true", "yes", "on"
}


def validate_production_config() -> None:
    """Fail closed when deployment would otherwise run with unsafe defaults."""
    if not IS_PRODUCTION:
        return
    if not DEMO_MODE and (not DATABASE_URL or not DATABASE_URL.startswith("postgresql+psycopg://")):
        raise RuntimeError("Production requires a PostgreSQL DATABASE_URL.")
    if DEMO_MODE and (not DEMO_USERNAME or len(DEMO_PASSWORD) < 12):
        raise RuntimeError("Production demo mode requires DEMO_USERNAME and a DEMO_PASSWORD of at least 12 characters.")
    if len(JWT_SECRET_KEY.encode("utf-8")) < 32:
        raise RuntimeError("Production requires a JWT_SECRET_KEY of at least 32 bytes.")
    if not AUTH_COOKIE_SECURE:
        raise RuntimeError("Production requires AUTH_COOKIE_SECURE=true.")
    if AUTO_CREATE_TABLES:
        raise RuntimeError("Production requires AUTO_CREATE_TABLES=false; initialize schema explicitly.")
    if not SERVE_FRONTEND:
        raise RuntimeError("Production requires SERVE_FRONTEND=true for the single-origin app.")
    if any(not origin.startswith("https://") or "*" in origin for origin in FRONTEND_ORIGINS):
        raise RuntimeError("Production FRONTEND_ORIGINS must contain only trusted HTTPS origins.")
