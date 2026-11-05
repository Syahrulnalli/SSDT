"""FastAPI app, API routes, and the preserved server-rendered preview pages."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.router import api_router
from backend.app.core.config import (
    AUTO_CREATE_TABLES, FRONTEND_ORIGINS, IS_PRODUCTION, SERVE_FRONTEND,
    validate_production_config,
)
from backend.app.core.database import engine
from backend.app.init_db import initialize_database
from demo_data import DEMO_GAPS, DEMO_PROGRESS, DEMO_RECOMMENDATIONS, DEMO_SKILL_SCORES
from skill_catalog import SKILLS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    validate_production_config()
    if SERVE_FRONTEND and not FRONTEND_INDEX.is_file():
        raise RuntimeError("SERVE_FRONTEND is enabled but the built React app is missing.")
    if engine is not None and AUTO_CREATE_TABLES:
        initialize_database()
    try:
        yield
    finally:
        if engine is not None:
            engine.dispose()


app = FastAPI(
    title="Student Skill Development Tracker API",
    description="Student profiles, official skills, assessment snapshots, and progress history.",
    version="1.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    lifespan=lifespan,
)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Return a safe database availability error without leaking SQL or credentials."""
    # SQLAlchemy exception text can contain SQL parameters or connection details.
    # Keep provider logs useful without writing query data or credentials.
    logger.error("Database operation failed (%s)", type(exc).__name__)
    return JSONResponse(
        status_code=503,
        content={"detail": "The database operation could not be completed."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(FRONTEND_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(api_router)
app.mount(
    "/static",
    StaticFiles(directory=str(PROJECT_ROOT / "static")),
    name="static",
)
if SERVE_FRONTEND:
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend-assets")


def page_response(request: Request, template: str, context: dict):
    if SERVE_FRONTEND:
        return FileResponse(FRONTEND_INDEX)
    return templates.TemplateResponse(request=request, name=template, context=context)


def dashboard_context(request: Request) -> dict:
    scores = {skill["id"]: DEMO_SKILL_SCORES[skill["id"]] for skill in SKILLS}
    return {
        "request": request,
        "skills": SKILLS,
        "scores": scores,
        "overall": round(sum(scores.values()) / len(scores)),
        "gaps": DEMO_GAPS,
        "recommendations": DEMO_RECOMMENDATIONS,
        "progress": DEMO_PROGRESS,
    }


@app.get("/", name="home", include_in_schema=False)
def home(request: Request):
    return page_response(request, "index.html", dashboard_context(request))


@app.get("/dashboard", name="dashboard", include_in_schema=False)
def dashboard(request: Request):
    return page_response(request, "dashboard.html", dashboard_context(request))


@app.get("/assessment", name="assessment", include_in_schema=False)
def assessment(request: Request):
    return page_response(request, "assessment.html", {"request": request, "skills": SKILLS})


@app.get("/skills", name="skills", include_in_schema=False)
def skill_framework(request: Request):
    return page_response(request, "skills.html", {"request": request, "skills": SKILLS})


@app.get("/recommendations", name="recommendations", include_in_schema=False)
def recommendations(request: Request):
    return page_response(request, "recommendations.html", {"request": request, "recommendations": DEMO_RECOMMENDATIONS})


@app.get("/progress", name="progress", include_in_schema=False)
def progress(request: Request):
    return page_response(request, "progress.html", {"request": request, "progress": DEMO_PROGRESS})


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Avoid a browser 404 for clients that request the default favicon path."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/static/favicon.svg", status_code=307)


if SERVE_FRONTEND:
    @app.get("/favicon.png", include_in_schema=False)
    def frontend_favicon():
        return FileResponse(FRONTEND_DIST / "favicon.png")


if SERVE_FRONTEND:
    @app.get("/{frontend_path:path}", include_in_schema=False)
    def react_deep_link(frontend_path: str):
        if frontend_path.startswith("api/") or "." in frontend_path.rsplit("/", 1)[-1]:
            return JSONResponse(status_code=404, content={"detail": "Not found."})
        return FileResponse(FRONTEND_INDEX)
