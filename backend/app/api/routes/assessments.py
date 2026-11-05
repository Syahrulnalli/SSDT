"""Serve assessment questions and record server-scored submissions."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, require_database
from backend.app.core.security import get_current_user, require_frontend_origin
from backend.app.models.user import User
from backend.app.schemas.assessment import (
    AssessmentCreate,
    AssessmentQuestionRead,
    AssessmentRead,
)
from backend.app.services.assessment_question_bank import SKILL_IDS, public_questions
from backend.app.services.assessment_service import create_assessment

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("/questions", response_model=list[AssessmentQuestionRead], summary="Get skill-specific assessment questions")
def get_assessment_questions(skill_id: str = Query(..., min_length=1, max_length=64)) -> list[dict]:
    """Return only the selected skill's questions, without answer keys."""
    if skill_id not in SKILL_IDS:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return public_questions(skill_id)


@router.post(
    "",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_frontend_origin)],
    summary="Record an assessment",
)
def record_assessment(
    payload: AssessmentCreate,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AssessmentRead:
    """Validate answers, calculate official per-skill scores, and save one snapshot."""
    db = require_database(db)
    if user.student is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No student profile is linked to this account.",
        )
    return create_assessment(db, payload, user.student)
