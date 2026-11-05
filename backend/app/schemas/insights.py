"""Validated response shapes for assessment analysis and learning guidance."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SkillAnalysisItem(BaseModel):
    skill_id: str
    skill_name: str
    latest_score: float | None
    previous_score: float | None
    score_change: float | None
    attempts: int
    last_assessed_at: datetime | None
    trend_status: Literal["not_assessed", "insufficient_history", "improving", "declining", "unchanged"]
    classification: Literal["not_assessed", "needs_attention", "developing", "strength"]
    strengths: list[str]
    areas_to_improve: list[str]


class SkillAnalysisRead(BaseModel):
    computed_at: datetime
    scoring_method: str
    gap_threshold: float
    strength_threshold: float
    attempted_skills: int
    skills: list[SkillAnalysisItem]


class RecommendationItem(BaseModel):
    skill_id: str
    skill_name: str
    title: str = Field(max_length=120)
    need: str = Field(max_length=500)
    action: str = Field(max_length=500)
    practice_activity: str = Field(max_length=500)
    priority: Literal["high", "medium", "low"]
    priority_basis: str = Field(max_length=300)
    evidence: str = Field(max_length=300)
    usefulness: str = Field(max_length=400)


class RecommendationText(BaseModel):
    """Only model-authored text; scores, priorities, and evidence stay server-owned."""

    model_config = ConfigDict(extra="forbid")

    skill_id: str
    title: str = Field(min_length=3, max_length=120)
    need: str = Field(min_length=8, max_length=500)
    action: str = Field(min_length=8, max_length=500)
    practice_activity: str = Field(min_length=8, max_length=500)
    usefulness: str = Field(min_length=8, max_length=400)


class RecommendationTextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendations: list[RecommendationText]


class RecommendationSet(BaseModel):
    generated_at: datetime
    source: Literal["rules", "groq"]
    ai_status: Literal["not_requested", "available", "unavailable"]
    message: str | None = None
    recommendations: list[RecommendationItem]
