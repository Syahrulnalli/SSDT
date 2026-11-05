"""Tests for deterministic student analysis and optional Groq guidance."""

import asyncio
from types import SimpleNamespace
from datetime import datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
import httpx
from groq import APITimeoutError, RateLimitError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.routes import insights
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_user
from backend.app.main import app
from backend.app.models.assessment import Assessment, AssessmentResult
from backend.app.models.skill import Skill
from backend.app.models.student import Student
from backend.app.models.user import User
from backend.app.services.groq_service import GroqServiceError
from backend.app.services.recommendation_service import generate_recommendations
from backend.app.services import groq_service
from backend.app.services.skill_analysis_service import (
    build_rule_recommendations,
    build_skill_analysis,
    get_student_skill_analysis,
)
from skill_catalog import SKILLS


def _row(skill_id: str, score: int, assessment_id: int, day: int):
    assessed = Assessment(id=assessment_id, student_id=1, assessed_at=datetime(2026, 10, day, tzinfo=timezone.utc))
    result = AssessmentResult(id=assessment_id, assessment_id=assessment_id, skill_id=skill_id, score=Decimal(score))
    return result, assessed


def _analysis(rows=()):
    return build_skill_analysis(list(rows), now=datetime(2026, 10, 23, tzinfo=timezone.utc))


def test_empty_history_returns_six_unscored_official_skills():
    result = _analysis()
    assert [item.skill_id for item in result.skills] == [item["id"] for item in SKILLS]
    assert result.attempted_skills == 0
    assert all(item.latest_score is None and item.classification == "not_assessed" for item in result.skills)
    assert build_rule_recommendations(result) == []


def test_one_skill_only_has_no_invented_scores_or_trend():
    result = _analysis([_row("python", 40, 1, 1)])
    python = next(item for item in result.skills if item.skill_id == "python")
    unattempted = next(item for item in result.skills if item.skill_id == "machine-learning")
    assert result.attempted_skills == 1
    assert python.latest_score == 40 and python.previous_score is None
    assert python.trend_status == "insufficient_history"
    assert python.classification == "needs_attention"
    assert unattempted.latest_score is None and unattempted.attempts == 0
    recs = build_rule_recommendations(result)
    assert [item.skill_id for item in recs] == ["python"]
    assert "40%" in recs[0].evidence


def test_multiple_skills_have_independent_scores_and_prioritized_evidence():
    result = _analysis([
        _row("python", 40, 1, 1),
        _row("machine-learning", 90, 2, 2),
    ])
    by_id = {item.skill_id: item for item in result.skills}
    assert result.attempted_skills == 2
    assert by_id["python"].latest_score == 40
    assert by_id["machine-learning"].latest_score == 90
    assert by_id["artificial-intelligence"].latest_score is None
    recs = {item.skill_id: item for item in build_rule_recommendations(result)}
    assert set(recs) == {"python", "machine-learning"}
    assert recs["python"].priority == "high"
    assert recs["machine-learning"].priority == "low"
    assert "40%" in recs["python"].evidence and "90%" in recs["machine-learning"].evidence


def test_recommendation_uses_latest_previous_score_and_dates(db_session):
    _, student = _student(db_session, "student_history", "history@example.com")
    _save_score(db_session, student, 30)
    _save_score(db_session, student, 55)
    analysis = get_student_skill_analysis(db_session, student.id)
    python = next(item for item in analysis.skills if item.skill_id == "python")
    rec = build_rule_recommendations(analysis)[0]
    assert python.attempts == 2 and python.previous_score == 30 and python.latest_score == 55
    assert python.score_change == 25 and python.trend_status == "improving"
    assert python.last_assessed_at is not None
    assert "previous score: 30%" in rec.evidence and "change: +25 points" in rec.evidence
    assert "assessed:" in rec.evidence


@pytest.mark.parametrize(
    ("scores", "expected_trend", "expected_change"),
    [([50, 70], "improving", 20), ([75, 55], "declining", -20), ([60, 60], "unchanged", 0)],
)
def test_trend_compares_two_latest_attempts_for_same_skill(scores, expected_trend, expected_change):
    rows = [_row("python", score, index + 1, index + 1) for index, score in enumerate(scores)]
    python = next(item for item in _analysis(rows).skills if item.skill_id == "python")
    assert python.attempts == 2
    assert python.previous_score == scores[0]
    assert python.latest_score == scores[1]
    assert python.score_change == expected_change
    assert python.trend_status == expected_trend


def test_thresholds_are_transparent_and_configurable():
    result = build_skill_analysis([_row("python", 70, 1, 1)], gap_threshold=50, strength_threshold=70)
    python = next(item for item in result.skills if item.skill_id == "python")
    assert python.classification == "strength"
    assert result.gap_threshold == 50 and result.strength_threshold == 70


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        yield session
    engine.dispose()


def _student(session: Session, username: str, email: str):
    user = User(username=username, email=email, password_hash="test-only")
    student = Student(name=username, email=email, program="BCA", batch="2027")
    user.student = student
    session.add(user)
    session.flush()
    if session.get(Skill, "python") is None:
        session.add(Skill(id="python", name="Python", description="Python assessment"))
        session.flush()
    return user, student


def _save_score(session: Session, student: Student, score: int):
    assessment = Assessment(student_id=student.id)
    session.add(assessment)
    session.flush()
    session.add(AssessmentResult(assessment_id=assessment.id, skill_id="python", score=Decimal(score)))
    session.commit()


def test_database_analysis_isolated_by_student(db_session):
    _, student_a = _student(db_session, "student_a", "a@example.test")
    _save_score(db_session, student_a, 30)
    _, student_b = _student(db_session, "student_b", "b@example.test")
    _save_score(db_session, student_b, 90)
    a = get_student_skill_analysis(db_session, student_a.id)
    b = get_student_skill_analysis(db_session, student_b.id)
    assert next(item for item in a.skills if item.skill_id == "python").latest_score == 30
    assert next(item for item in b.skills if item.skill_id == "python").latest_score == 90


def test_groq_failure_falls_back_to_marked_rule_recommendation(db_session):
    _, student = _student(db_session, "student_c", "c@example.test")
    _save_score(db_session, student, 40)
    analysis = get_student_skill_analysis(db_session, student.id)
    with patch("backend.app.services.recommendation_service.create_chat_completion", new=AsyncMock(side_effect=GroqServiceError("The Groq request timed out."))):
        result = asyncio.run(generate_recommendations(db_session, student.id, analysis))
    assert result.source == "rules" and result.ai_status == "unavailable"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].skill_id == "python"
    assert "unavailable" in result.message.lower()
    assert db_session.query(Assessment).count() == 1


def test_groq_output_is_validated_and_cannot_change_score_or_priority(db_session):
    _, student = _student(db_session, "student_d", "d@example.test")
    _save_score(db_session, student, 40)
    analysis = get_student_skill_analysis(db_session, student.id)
    valid = '{"recommendations":[{"skill_id":"python","title":"Review Python basics","need":"The current quiz score is under the set threshold.","action":"Practice one Python concept at a time and explain each step.","practice_activity":"Write a short Python program that uses a loop and a function.","usefulness":"This connects the quiz topics to a repeatable exercise."}]}'
    with patch("backend.app.services.recommendation_service.create_chat_completion", new=AsyncMock(return_value=valid)):
        result = asyncio.run(generate_recommendations(db_session, student.id, analysis))
    assert result.source == "groq" and result.ai_status == "available"
    assert result.recommendations[0].title == "Review Python basics"
    assert result.recommendations[0].priority == "high"
    assert result.recommendations[0].evidence.startswith("Latest recorded score: 40%")


def test_malformed_or_wrong_skill_groq_response_uses_rules_fallback(db_session):
    _, student = _student(db_session, "student_e", "e@example.test")
    _save_score(db_session, student, 40)
    analysis = get_student_skill_analysis(db_session, student.id)
    invalid = '{"recommendations":[{"skill_id":"machine-learning","title":"Review ML basics","need":"The score needs review.","action":"Review and practice the lesson topics again.","practice_activity":"Try a small learning task using the lesson.","usefulness":"The task provides another chance to practice."}]}'
    with patch("backend.app.services.recommendation_service.create_chat_completion", new=AsyncMock(return_value=invalid)):
        result = asyncio.run(generate_recommendations(db_session, student.id, analysis))
    assert result.source == "rules" and result.ai_status == "unavailable"
    assert [item.skill_id for item in result.recommendations] == ["python"]


def test_missing_groq_key_is_reported_without_attempting_a_request(monkeypatch):
    monkeypatch.setattr(groq_service, "GROQ_API_KEY", "")
    with pytest.raises(GroqServiceError, match="not configured"):
        asyncio.run(groq_service.create_chat_completion([{"role": "user", "content": "test"}]))


def test_groq_timeout_has_a_safe_message(monkeypatch):
    class FakeCompletions:
        async def create(self, **kwargs):
            raise APITimeoutError(request=httpx.Request("POST", "https://api.groq.com"))

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

    monkeypatch.setattr(groq_service, "GROQ_API_KEY", "test-only")
    monkeypatch.setattr(groq_service, "AsyncGroq", lambda **kwargs: FakeClient())
    with pytest.raises(GroqServiceError, match="timed out"):
        asyncio.run(groq_service.create_chat_completion([{"role": "user", "content": "test"}]))


def test_groq_rate_limit_has_a_safe_message(monkeypatch):
    class FakeCompletions:
        async def create(self, **kwargs):
            raise RateLimitError("limited", response=httpx.Response(429, request=httpx.Request("POST", "https://api.groq.com")), body=None)

    class FakeClient:
        chat = SimpleNamespace(completions=FakeCompletions())
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None

    monkeypatch.setattr(groq_service, "GROQ_API_KEY", "test-only")
    monkeypatch.setattr(groq_service, "AsyncGroq", lambda **kwargs: FakeClient())
    with pytest.raises(GroqServiceError, match="rate limit"):
        asyncio.run(groq_service.create_chat_completion([{"role": "user", "content": "synthetic"}]))


def test_session_identity_scopes_analysis_and_ignores_client_student_id(db_session):
    user_a, student_a = _student(db_session, "student_api_a", "api-a@example.test")
    _save_score(db_session, student_a, 35)
    user_b, student_b = _student(db_session, "student_api_b", "api-b@example.test")
    _save_score(db_session, student_b, 95)
    active_user = [user_a]
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: active_user[0]
    try:
        client = TestClient(app)
        response_a = client.get(f"/api/insights/analysis?student_id={student_b.id}")
        active_user[0] = db_session.get(User, user_a.id)
        python_a = next(item for item in response_a.json()["skills"] if item["skill_id"] == "python")
        assert response_a.status_code == 200 and python_a["latest_score"] == 35

        active_user[0] = db_session.get(User, user_b.id)
        response_b = client.get("/api/insights/analysis")
        assert next(item for item in response_b.json()["skills"] if item["skill_id"] == "python")["latest_score"] == 95
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


def test_recommendations_are_account_scoped_explicit_and_not_persisted(db_session):
    user, student = _student(db_session, "student_recs", "recs@example.test")
    _save_score(db_session, student, 45)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.get("/api/insights/recommendations")
        assert response.status_code == 200
        payload = response.json()
        assert payload["source"] == "rules"
        assert [item["skill_id"] for item in payload["recommendations"]] == ["python"]
        assert db_session.query(Assessment).count() == 1

        with patch(
            "backend.app.services.recommendation_service.create_chat_completion",
            new=AsyncMock(side_effect=GroqServiceError("Temporary provider issue.")),
        ):
            refreshed = client.post(
                "/api/insights/recommendations/generate",
                headers={"Origin": "http://localhost:5173"},
            )
        assert refreshed.status_code == 200
        assert refreshed.json()["ai_status"] == "unavailable"
        assert db_session.query(Assessment).count() == 1
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


def test_analysis_endpoint_requires_authenticated_user():
    def unauthenticated():
        raise HTTPException(status_code=401, detail="Authentication is required.")

    app.dependency_overrides[get_current_user] = unauthenticated
    try:
        response = TestClient(app).get("/api/insights/analysis")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 401


def test_frontend_bundle_does_not_contain_configured_groq_key():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        from backend.app.core.config import GROQ_API_KEY
        key = GROQ_API_KEY
    if not key:
        pytest.skip("No Groq key is configured for the secret-exposure assertion.")
    root = Path(__file__).resolve().parents[1]
    assets = list((root / "frontend" / "dist").rglob("*.js"))
    assert assets, "Build the frontend before running the asset secret scan."
    assert all(key not in asset.read_text(encoding="utf-8") for asset in assets)
