"""Assessment and historical progress queries."""

from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.app.models.assessment import Assessment, AssessmentResult
from backend.app.models.skill import Skill
from backend.app.models.student import Student
from backend.app.schemas.assessment import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentResultRead,
    ProgressPointRead,
)
from backend.app.services.assessment_question_bank import (
    ASSESSMENT_QUESTIONS,
    QUESTION_BY_ID,
    SKILL_IDS,
    SKILL_NAMES,
)
from backend.app.services.skill_service import seed_official_skills
from skill_catalog import SKILLS


def get_student_or_404(db: Session, student_id: int, user_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None or student.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


def serialize_assessment(assessment: Assessment) -> AssessmentRead:
    results = [
        AssessmentResultRead(
            skill_id=result.skill_id,
            skill_name=result.skill.name if result.skill else SKILL_NAMES[result.skill_id],
            score=result.score,
        )
        for result in assessment.results
    ]
    overall_score = (
        sum((result.score for result in results), Decimal("0")) / len(results)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if results else Decimal("0.00")
    return AssessmentRead(
        id=assessment.id,
        student_id=assessment.student_id,
        assessed_at=assessment.assessed_at,
        overall_score=overall_score,
        results=results,
    )


def create_assessment(db: Session, payload: AssessmentCreate, student: Student) -> AssessmentRead:
    if student.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No student profile is linked to this account.",
        )
    if payload.skill_id not in SKILL_IDS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Unknown skill ID.")
    answer_by_id = {answer.question_id: answer.selected_option_id for answer in payload.answers}
    unknown_questions = sorted(set(answer_by_id) - set(QUESTION_BY_ID))
    if unknown_questions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown assessment question ID(s): {', '.join(unknown_questions)}.",
        )

    selected_questions = [q for q in ASSESSMENT_QUESTIONS if q["skill_id"] == payload.skill_id]
    expected_questions = {question["id"] for question in selected_questions}
    if set(answer_by_id) != expected_questions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Submit every question for the selected skill and no others.",
        )

    correct = 0
    for question in selected_questions:
        selected_option_id = answer_by_id[question["id"]]
        valid_option_ids = {option["id"] for option in question["options"]}
        if selected_option_id not in valid_option_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid answer option for question {question['id']}.",
            )
        if selected_option_id == question["correct_option_id"]:
            correct += 1

    seed_official_skills(db)
    assessment = Assessment(student_id=student.id)
    score = (Decimal(correct * 100) / Decimal(len(selected_questions))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assessment.results = [
        AssessmentResult(
            skill_id=payload.skill_id,
            score=score,
        )
    ]
    db.add(assessment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The assessment could not be saved because it conflicts with existing data.",
        ) from exc
    db.refresh(assessment)
    return serialize_assessment(assessment)


def list_student_assessments(db: Session, student_id: int, user_id: int) -> list[AssessmentRead]:
    get_student_or_404(db, student_id, user_id)
    rows = db.scalars(
        select(Assessment)
        .options(joinedload(Assessment.results).joinedload(AssessmentResult.skill))
        .where(Assessment.student_id == student_id)
        .order_by(Assessment.assessed_at.desc(), Assessment.id.desc())
    ).unique().all()
    return [serialize_assessment(row) for row in rows]


def list_student_progress(db: Session, student_id: int, user_id: int) -> list[ProgressPointRead]:
    get_student_or_404(db, student_id, user_id)
    rows = db.execute(
        select(AssessmentResult, Assessment)
        .join(Assessment, Assessment.id == AssessmentResult.assessment_id)
        .options(joinedload(AssessmentResult.skill))
        .where(Assessment.student_id == student_id)
        .order_by(Assessment.assessed_at.asc(), Assessment.id.asc(), AssessmentResult.skill_id.asc())
    ).all()
    return [
        ProgressPointRead(
            assessment_id=assessment.id,
            skill_id=result.skill_id,
            skill_name=result.skill.name if result.skill else SKILL_NAMES[result.skill_id],
            score=result.score,
            assessed_at=assessment.assessed_at,
        )
        for result, assessment in rows
    ]


def list_current_skills(db: Session, student_id: int, user_id: int) -> list[dict]:
    get_student_or_404(db, student_id, user_id)
    rows = db.execute(
        select(AssessmentResult, Assessment)
        .join(Assessment, Assessment.id == AssessmentResult.assessment_id)
        .where(Assessment.student_id == student_id)
        .order_by(Assessment.assessed_at.desc(), Assessment.id.desc())
    ).all()
    latest: dict[str, tuple[AssessmentResult, Assessment]] = {}
    for result, assessment in rows:
        latest.setdefault(result.skill_id, (result, assessment))

    focus_by_id = {item["id"]: list(item["focus"]) for item in SKILLS}
    return [
        {
            "skill_id": item["id"],
            "skill_name": item["name"],
            "focus": focus_by_id[item["id"]],
            "latest_score": float(latest[item["id"]][0].score) if item["id"] in latest else None,
            "assessed_at": latest[item["id"]][1].assessed_at if item["id"] in latest else None,
        }
        for item in SKILLS
    ]
