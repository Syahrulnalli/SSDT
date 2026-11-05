"""Authenticated analysis and recommendation routes for the signed-in student."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, require_database
from backend.app.core.security import get_current_user, require_frontend_origin
from backend.app.models.user import User
from backend.app.schemas.insights import RecommendationSet, SkillAnalysisRead
from backend.app.services.recommendation_service import generate_recommendations
from backend.app.services.skill_analysis_service import (
    build_rule_recommendations,
    get_student_skill_analysis,
)

router = APIRouter(prefix="/insights", tags=["skill insights"])


def _current_student_id(user: User) -> int:
    if user.student is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No student profile is linked to this account.",
        )
    return user.student.id


@router.get("/analysis", response_model=SkillAnalysisRead, summary="Analyze the current student's saved results")
def current_analysis(
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SkillAnalysisRead:
    db = require_database(db)
    return get_student_skill_analysis(db, _current_student_id(user))


@router.get("/recommendations", response_model=RecommendationSet, summary="Get current rule-based recommendations")
def current_recommendations(
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecommendationSet:
    db = require_database(db)
    analysis = get_student_skill_analysis(db, _current_student_id(user))
    recommendations = build_rule_recommendations(analysis)
    return RecommendationSet(
        generated_at=analysis.computed_at,
        source="rules",
        ai_status="not_requested",
        message=(None if recommendations else "Complete a skill quiz to receive recommendations based on assessment evidence."),
        recommendations=recommendations,
    )


@router.post(
    "/recommendations/generate",
    response_model=RecommendationSet,
    dependencies=[Depends(require_frontend_origin)],
    summary="Generate current-student learning guidance with Groq",
)
async def refresh_recommendations(
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecommendationSet:
    db = require_database(db)
    student_id = _current_student_id(user)
    analysis = get_student_skill_analysis(db, student_id)
    return await generate_recommendations(db, student_id, analysis)
