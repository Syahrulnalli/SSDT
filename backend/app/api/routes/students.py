"""Student profile and skill summary endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, require_database
from backend.app.core.security import get_current_user, require_frontend_origin
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.schemas.assessment import AssessmentRead, ProgressPointRead
from backend.app.schemas.student import StudentCreate, StudentRead, StudentSkillRead
from backend.app.services.assessment_service import (
    get_student_or_404,
    list_current_skills,
    list_student_assessments,
    list_student_progress,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_frontend_origin)],
    summary="Create the current user's student profile",
)
def create_student(
    payload: StudentCreate,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Student:
    """Create a missing profile for the logged-in user without allowing reassignment."""
    db = require_database(db)
    if db.scalar(select(Student.id).where(Student.user_id == user.id)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This account already has a student profile.",
        )
    if str(payload.email).lower() != user.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The student profile email must match the signed-in account.",
        )
    student = Student(
        user_id=user.id,
        name=payload.name,
        email=str(payload.email).lower(),
        program=payload.program,
        batch=payload.batch,
    )
    db.add(student)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        ) from exc
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentRead, summary="Get a student profile")
def get_student(
    student_id: int,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Student:
    db = require_database(db)
    return get_student_or_404(db, student_id, user.id)


@router.get("/{student_id}/skills", response_model=list[StudentSkillRead], summary="Get current skill levels")
def get_student_skills(
    student_id: int,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    """Return all six skills with each student's most recent recorded score."""
    db = require_database(db)
    return list_current_skills(db, student_id, user.id)


@router.get("/{student_id}/assessments", response_model=list[AssessmentRead], summary="List student assessments")
def get_student_assessments(
    student_id: int,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AssessmentRead]:
    db = require_database(db)
    return list_student_assessments(db, student_id, user.id)


@router.get("/{student_id}/progress", response_model=list[ProgressPointRead], summary="Get skill progress history")
def get_student_progress(
    student_id: int,
    db: Session | None = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProgressPointRead]:
    """Return assessment results in chronological order for dashboard history."""
    db = require_database(db)
    return list_student_progress(db, student_id, user.id)
