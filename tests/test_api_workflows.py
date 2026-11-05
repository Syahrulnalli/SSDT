"""Isolated HTTP workflows for auth, student ownership, and skill assessments."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.router import api_router
from backend.app.core.database import Base, get_db
from backend.app.core import security
from backend.app.core.security import get_current_user
from backend.app.main import app
from backend.app.models import Assessment, AssessmentResult, Skill, Student, User
from backend.app.services.assessment_question_bank import ASSESSMENT_QUESTIONS, SKILL_IDS
from backend.app.services.skill_service import seed_official_skills
from skill_catalog import SKILLS


@pytest.fixture
def api_context(monkeypatch):
    """Use a disposable test-only SQLite database; no configured PostgreSQL writes."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = factory()
    seed_official_skills(db)

    monkeypatch.setattr(security, "JWT_SECRET_KEY", "isolated-test-secret-32-bytes-long!!")
    monkeypatch.setattr(security, "AUTH_COOKIE_SECURE", False)
    monkeypatch.setattr(security, "FRONTEND_ORIGINS", ("http://localhost:5173",))
    from backend.app.api.routes import auth as auth_routes
    monkeypatch.setattr(auth_routes, "AUTH_COOKIE_SECURE", False)
    app.dependency_overrides[get_db] = lambda: db

    # Do not enter TestClient as a context manager: that would run production's
    # table-initialization lifespan against the configured PostgreSQL database.
    client = TestClient(app, base_url="http://localhost")
    yield client, db, factory
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)
    db.close()
    engine.dispose()


def _register(client: TestClient, username: str, email: str):
    response = client.post(
        "/api/auth/register",
        headers={"Origin": "http://localhost:5173"},
        json={
            "username": username,
            "email": email,
            "password": "Correct-Horse-2026!",
            "name": f"Test {username}",
            "program": "BCA",
            "batch": "2027",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _python_answers(*, correct: bool) -> list[dict[str, str]]:
    questions = [item for item in ASSESSMENT_QUESTIONS if item["skill_id"] == "python"]
    return [
        {
            "question_id": question["id"],
            "selected_option_id": question["correct_option_id"] if correct else next(
                option["id"] for option in question["options"]
                if option["id"] != question["correct_option_id"]
            ),
        }
        for question in questions
    ]


def test_auth_registration_login_session_cookie_and_logout(api_context):
    client, db, _ = api_context

    invalid = client.post(
        "/api/auth/register",
        headers={"Origin": "http://localhost:5173"},
        json={"username": "x", "email": "not-an-email", "password": "short"},
    )
    assert invalid.status_code == 422
    assert db.scalar(select(func.count()).select_from(User)) == 0

    account = _register(client, "rajesh_test", "rajesh_test@example.com")
    assert "password_hash" not in account["user"]
    cookie_header = client.cookies.jar
    cookie = next(item for item in cookie_header if item.name == "ssdt_session")
    assert cookie.has_nonstandard_attr("HttpOnly")
    assert cookie.get_nonstandard_attr("SameSite").lower() == "lax"
    assert not cookie.secure  # HTTP localhost development setting.

    duplicate = client.post(
        "/api/auth/register",
        headers={"Origin": "http://localhost:5173"},
        json={
            "username": "another_name", "email": "rajesh_test@example.com",
            "password": "Correct-Horse-2026!", "name": "Duplicate",
            "program": "BCA", "batch": "2027",
        },
    )
    assert duplicate.status_code == 409

    wrong_password = client.post(
        "/api/auth/login",
        headers={"Origin": "http://localhost:5173"},
        json={"username_or_email": "rajesh_test", "password": "Wrong-password-2026"},
    )
    assert wrong_password.status_code == 401
    login = client.post(
        "/api/auth/login",
        headers={"Origin": "http://localhost:5173"},
        json={"username_or_email": "rajesh_test@example.com", "password": "Correct-Horse-2026!"},
    )
    assert login.status_code == 200
    restored = client.get("/api/auth/me")
    assert restored.status_code == 200
    assert restored.json()["user"]["username"] == "rajesh_test"
    analysis = client.get("/api/insights/analysis")
    assert analysis.status_code == 200
    assert len(analysis.json()["skills"]) == 6
    assert all(item["latest_score"] is None for item in analysis.json()["skills"])

    logged_out = client.post("/api/auth/logout", headers={"Origin": "http://localhost:5173"})
    assert logged_out.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_protected_routes_reject_unauthenticated_access(api_context):
    client, _, _ = api_context
    assert client.get("/api/insights/analysis").status_code == 401
    assert client.get("/api/students/1").status_code == 401
    assert client.get("/api/students/1/progress").status_code == 401


def test_official_skills_and_assessment_history_workflow(api_context):
    client, db, _ = api_context
    names_by_id = {item["id"]: item["name"] for item in SKILLS}
    assert len(SKILL_IDS) == 6
    assert set(names_by_id.values()) == {
        "Python", "Machine Learning", "Artificial Intelligence",
        "SQL & Databases", "Web Development", "Problem Solving & Algorithms",
    }
    listed = client.get("/api/skills")
    assert listed.status_code == 200
    assert len(listed.json()) == 6
    assert {item["id"] for item in listed.json()} == set(SKILL_IDS)
    assert client.get("/api/skills/python").status_code == 200
    assert client.get("/api/skills/not-a-skill").status_code == 404

    account = _register(client, "assessment_test", "assessment_test@example.com")
    student_id = account["student"]["id"]
    questions = client.get("/api/assessments/questions?skill_id=python")
    assert questions.status_code == 200 and len(questions.json()) == 5
    assert all("correct_option_id" not in question for question in questions.json())
    assert client.get("/api/assessments/questions?skill_id=unknown").status_code == 404

    bad = client.post(
        "/api/assessments",
        headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "answers": _python_answers(correct=True), "score": 100},
    )
    assert bad.status_code == 422  # Client cannot submit a score.
    invalid_option = _python_answers(correct=True)
    invalid_option[0]["selected_option_id"] = "not-an-option"
    bad_option = client.post(
        "/api/assessments",
        headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "answers": invalid_option},
    )
    assert bad_option.status_code == 422
    assert db.scalar(select(func.count()).select_from(Assessment)) == 0

    first = client.post(
        "/api/assessments", headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "answers": _python_answers(correct=True)},
    )
    second = client.post(
        "/api/assessments", headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "answers": _python_answers(correct=False)},
    )
    assert first.status_code == 201 and second.status_code == 201
    assert float(first.json()["overall_score"]) == 100
    assert float(second.json()["overall_score"]) == 0
    assert first.json()["student_id"] == student_id == second.json()["student_id"]
    assert first.json()["results"][0]["skill_id"] == "python"

    history = client.get(f"/api/students/{student_id}/assessments")
    assert history.status_code == 200 and len(history.json()) == 2
    assert {float(item["overall_score"]) for item in history.json()} == {0, 100}
    progress = client.get(f"/api/students/{student_id}/progress")
    assert progress.status_code == 200 and len(progress.json()) == 2
    assert [float(item["score"]) for item in progress.json()] == [100, 0]
    levels = client.get(f"/api/students/{student_id}/skills")
    assert len(levels.json()) == 6
    assert next(item for item in levels.json() if item["skill_id"] == "python")["latest_score"] == 0
    assert next(item for item in levels.json() if item["skill_id"] == "machine-learning")["latest_score"] is None
    analysis = client.get("/api/insights/analysis")
    python = next(item for item in analysis.json()["skills"] if item["skill_id"] == "python")
    assert python["attempts"] == 2 and python["score_change"] == -100
    assert python["trend_status"] == "declining"


def test_student_records_and_assessment_writes_are_isolated(api_context):
    client_a, _, _ = api_context
    account_a = _register(client_a, "owner_a", "owner_a@example.com")
    student_a = account_a["student"]["id"]
    client_b = TestClient(app, base_url="http://localhost")
    account_b = _register(client_b, "owner_b", "owner_b@example.com")
    student_b = account_b["student"]["id"]

    client_a.post(
        "/api/assessments", headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "answers": _python_answers(correct=True)},
    )
    for path in (
        f"/api/students/{student_a}",
        f"/api/students/{student_a}/skills",
        f"/api/students/{student_a}/assessments",
        f"/api/students/{student_a}/progress",
    ):
        assert client_b.get(path).status_code == 404
    own_analysis = client_b.get(f"/api/insights/analysis?student_id={student_a}")
    assert own_analysis.status_code == 200
    assert own_analysis.json()["attempted_skills"] == 0

    cannot_create_profile_for_other_email = client_b.post(
        "/api/students",
        headers={"Origin": "http://localhost:5173"},
        json={
            "name": "Wrong owner", "email": "owner_a@example.com",
            "program": "BCA", "batch": "2027",
        },
    )
    assert cannot_create_profile_for_other_email.status_code == 409  # A second profile cannot be attached.
    client_supplied_owner = client_b.post(
        "/api/students",
        headers={"Origin": "http://localhost:5173"},
        json={
            "name": "Wrong owner", "email": "owner_b@example.com",
            "program": "BCA", "batch": "2027", "student_id": student_a,
        },
    )
    assert client_supplied_owner.status_code == 422
    assert client_b.post(
        "/api/assessments",
        headers={"Origin": "http://localhost:5173"},
        json={"skill_id": "python", "student_id": student_a, "answers": _python_answers(correct=True)},
    ).status_code == 422  # Request schema rejects client-supplied ownership.
