"""Deterministic, account-scoped analysis of persisted assessment results."""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.core.config import SKILL_GAP_THRESHOLD, SKILL_STRENGTH_THRESHOLD
from backend.app.models.assessment import Assessment, AssessmentResult
from backend.app.schemas.insights import SkillAnalysisRead
from skill_catalog import SKILLS


SCORING_METHOD = (
    "Each independent five-question quiz is scored as a percentage. "
    f"A latest score below {SKILL_GAP_THRESHOLD:g}% needs attention; "
    f"a score at or above {SKILL_STRENGTH_THRESHOLD:g}% is a current strength. "
    "Trends compare the two most recent attempts for the same skill."
)


def build_skill_analysis(
    rows: list[tuple[AssessmentResult, Assessment]],
    *,
    now: datetime | None = None,
    gap_threshold: float = SKILL_GAP_THRESHOLD,
    strength_threshold: float = SKILL_STRENGTH_THRESHOLD,
) -> SkillAnalysisRead:
    """Build all six canonical skill summaries; absent results remain unscored."""
    by_skill: dict[str, list[tuple[AssessmentResult, Assessment]]] = {
        item["id"]: [] for item in SKILLS
    }
    for result, assessment in rows:
        if result.skill_id in by_skill:
            by_skill[result.skill_id].append((result, assessment))

    skills = []
    for catalog_skill in SKILLS:
        history = sorted(
            by_skill[catalog_skill["id"]],
            key=lambda row: (row[1].assessed_at, row[1].id),
        )
        attempts = len(history)
        if not attempts:
            skills.append({
                "skill_id": catalog_skill["id"], "skill_name": catalog_skill["name"],
                "latest_score": None, "previous_score": None, "score_change": None,
                "attempts": 0, "last_assessed_at": None,
                "trend_status": "not_assessed", "classification": "not_assessed",
                "strengths": [], "areas_to_improve": [],
            })
            continue

        latest_result, latest_assessment = history[-1]
        latest = float(latest_result.score)
        previous = float(history[-2][0].score) if attempts > 1 else None
        change = round(latest - previous, 2) if previous is not None else None
        trend = (
            "insufficient_history" if change is None else
            "improving" if change > 0 else "declining" if change < 0 else "unchanged"
        )
        classification = (
            "needs_attention" if latest < gap_threshold else
            "strength" if latest >= strength_threshold else "developing"
        )
        strengths = []
        if classification == "strength":
            strengths.append(f"Latest quiz score is {latest:g}%, at or above the {strength_threshold:g}% strength threshold.")
        elif change is not None and change > 0:
            strengths.append(f"Score increased by {change:g} points from the previous comparable attempt.")
        areas = []
        if classification == "needs_attention":
            areas.append(f"Latest score is below the {gap_threshold:g}% attention threshold; review this skill's foundations.")
        elif classification == "developing":
            areas.append("Continue targeted practice; the current score is below the strength threshold.")
        if change is not None and change < 0:
            areas.append(f"Score decreased by {abs(change):g} points from the previous comparable attempt.")
        skills.append({
            "skill_id": catalog_skill["id"], "skill_name": catalog_skill["name"],
            "latest_score": latest, "previous_score": previous, "score_change": change,
            "attempts": attempts, "last_assessed_at": latest_assessment.assessed_at,
            "trend_status": trend, "classification": classification,
            "strengths": strengths, "areas_to_improve": areas,
        })

    return SkillAnalysisRead(
        computed_at=now or datetime.now(timezone.utc),
        scoring_method=SCORING_METHOD,
        gap_threshold=gap_threshold,
        strength_threshold=strength_threshold,
        attempted_skills=sum(1 for item in skills if item["attempts"]),
        skills=skills,
    )


def get_student_skill_analysis(db: Session, student_id: int) -> SkillAnalysisRead:
    """Query only the caller's student ID, which is derived from their session."""
    rows = db.execute(
        select(AssessmentResult, Assessment)
        .join(Assessment, Assessment.id == AssessmentResult.assessment_id)
        .options(joinedload(AssessmentResult.skill))
        .where(Assessment.student_id == student_id)
        .order_by(Assessment.assessed_at.asc(), Assessment.id.asc())
    ).all()
    return build_skill_analysis(rows)


def _evidence(item) -> str:
    parts = [f"Latest recorded score: {item.latest_score:g}%", f"attempts: {item.attempts}"]
    if item.previous_score is not None:
        parts.append(f"previous score: {item.previous_score:g}%")
    if item.score_change is not None:
        parts.append(f"change: {item.score_change:+g} points")
    if item.last_assessed_at is not None:
        parts.append(f"assessed: {item.last_assessed_at.date().isoformat()}")
    return "; ".join(parts) + "."


def build_rule_recommendations(analysis: SkillAnalysisRead):
    """Ground suggestions in a student's recorded results; never use unattempted skills."""
    from backend.app.schemas.insights import RecommendationItem

    recommendations = []
    for item in analysis.skills:
        if item.latest_score is None:
            continue
        if item.classification == "needs_attention":
            title = f"Strengthen {item.skill_name} foundations"
            need = f"Your latest {item.skill_name} quiz score is below the configured attention threshold."
            action = f"Review the core concepts covered by the {item.skill_name} quiz, then explain each concept in your own words."
            practice = f"Complete a small {item.skill_name} exercise that applies one concept at a time, then retake this quiz after practice."
            priority, basis = "high", f"Latest score {item.latest_score:g}% is below {analysis.gap_threshold:g}%."
        elif item.classification == "developing":
            title = f"Build consistency in {item.skill_name}"
            need = f"Your latest score is in the developing range, below the strength threshold."
            action = f"Practice the {item.skill_name} concepts where you hesitated and check your reasoning against a trusted reference."
            practice = f"Make a short {item.skill_name} mini-project using two concepts from the quiz, then note what you would improve."
            priority, basis = "medium", f"Latest score {item.latest_score:g}% is between the configured thresholds."
        else:
            title = f"Extend your {item.skill_name} skills"
            need = f"Your latest quiz score is at or above the strength threshold; this is a result on the quiz, not a broad mastery claim."
            action = f"Choose a more challenging {item.skill_name} problem and write down the approach and trade-offs."
            practice = f"Build a small {item.skill_name} extension that applies the same foundations in a new context."
            priority, basis = "low", f"Latest score {item.latest_score:g}% meets the configured strength threshold."
        recommendations.append(RecommendationItem(
            skill_id=item.skill_id, skill_name=item.skill_name, title=title, need=need,
            action=action, practice_activity=practice, priority=priority,
            priority_basis=basis, evidence=_evidence(item),
            usefulness="A short, focused practice task connects this recorded result to a concrete next learning step.",
        ))
    return recommendations
