"""Combine API route groups under the shared /api prefix."""

from fastapi import APIRouter

from backend.app.api.routes import assessments, auth, health, insights, skills, students

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(skills.router)
api_router.include_router(students.router)
api_router.include_router(assessments.router)
api_router.include_router(insights.router)
