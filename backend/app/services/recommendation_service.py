"""Rule-based recommendations and optional Groq-authored learning guidance."""

import json
from datetime import datetime, timezone

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.assessment import Assessment, AssessmentResult
from backend.app.schemas.insights import (
    RecommendationSet,
    RecommendationTextResponse,
    SkillAnalysisRead,
)
from backend.app.services.groq_service import GroqServiceError, create_chat_completion
from backend.app.services.skill_analysis_service import build_rule_recommendations


SYSTEM_PROMPT = """You are a careful learning coach for a student skill tracker.
Use only the assessment evidence supplied by the server. Do not invent scores,
attempts, abilities, learning history, or facts about the student. Treat scores
and priorities as fixed evidence; do not change them. Return one concise,
practical suggestion for each supplied skill, using the exact skill_id. A quiz
score is limited evidence and must not be described as broad mastery. Suggestions
must be specific, achievable, and clearly distinguish the observed need from the
proposed action. Return one item for every supplied skill and no other skills.
Return JSON only with exactly this shape (all values are strings):
{"recommendations":[{"skill_id":"...","title":"...","need":"...","action":"...","practice_activity":"...","usefulness":"..."}]}.
Do not add scores, priority, evidence, or other keys; the server adds evidence."""


def _history_summary(db: Session, student_id: int) -> list[dict]:
    rows = db.execute(
        select(AssessmentResult, Assessment)
        .join(Assessment, Assessment.id == AssessmentResult.assessment_id)
        .where(Assessment.student_id == student_id)
        .order_by(Assessment.assessed_at.desc(), Assessment.id.desc())
    ).all()
    history: dict[str, list[dict]] = {}
    for result, assessment in rows:
        attempts = history.setdefault(result.skill_id, [])
        if len(attempts) < 3:
            attempts.append({"score": float(result.score), "date": assessment.assessed_at.date().isoformat()})
    return [{"skill_id": key, "attempts": values} for key, values in sorted(history.items())]


async def generate_recommendations(
    db: Session,
    student_id: int,
    analysis: SkillAnalysisRead,
) -> RecommendationSet:
    """Ask Groq to contextualize evidence; preserve server-derived evidence and priority."""
    rules = build_rule_recommendations(analysis)
    if not rules:
        return RecommendationSet(
            generated_at=datetime.now(timezone.utc), source="rules", ai_status="not_requested",
            message="Complete a skill quiz to receive recommendations based on assessment evidence.",
            recommendations=[],
        )

    compact_evidence = {
        "skills": [
            {
                "skill_id": item.skill_id,
                "skill_name": item.skill_name,
                "latest_score": item.latest_score,
                "previous_score": item.previous_score,
                "score_change": item.score_change,
                "attempts": item.attempts,
                "classification": item.classification,
                "strengths": item.strengths,
                "areas_to_improve": item.areas_to_improve,
            }
            for item in analysis.skills if item.latest_score is not None
        ],
        "recent_scores_by_skill": _history_summary(db, student_id),
        "thresholds": {
            "attention_below": analysis.gap_threshold,
            "strength_at_or_above": analysis.strength_threshold,
        },
    }
    try:
        raw = await create_chat_completion(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(compact_evidence, separators=(",", ":"))},
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=1800,
        )
        validated = RecommendationTextResponse.model_validate(json.loads(raw))
        by_id = {item.skill_id: item for item in validated.recommendations}
        expected = {item.skill_id for item in rules}
        if len(by_id) != len(validated.recommendations) or set(by_id) != expected:
            raise ValueError("Model output did not match the assessed skill set.")
        recommendations = [
            base.model_copy(update={
                "title": by_id[base.skill_id].title,
                "need": by_id[base.skill_id].need,
                "action": by_id[base.skill_id].action,
                "practice_activity": by_id[base.skill_id].practice_activity,
                "usefulness": by_id[base.skill_id].usefulness,
            })
            for base in rules
        ]
        return RecommendationSet(
            generated_at=datetime.now(timezone.utc), source="groq", ai_status="available",
            recommendations=recommendations,
        )
    except (GroqServiceError, ValidationError, json.JSONDecodeError, TypeError, ValueError):
        # The fallback is explicitly identified; it never claims an LLM response succeeded.
        return RecommendationSet(
            generated_at=datetime.now(timezone.utc), source="rules", ai_status="unavailable",
            message="AI-generated explanations are unavailable right now. These rule-based suggestions use your saved assessment results.",
            recommendations=rules,
        )
