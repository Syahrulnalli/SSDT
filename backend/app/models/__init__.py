"""SQLAlchemy models. Import all models here for metadata registration."""

from backend.app.models.assessment import Assessment, AssessmentResult
from backend.app.models.skill import Skill
from backend.app.models.student import Student
from backend.app.models.user import User

__all__ = ["Assessment", "AssessmentResult", "Skill", "Student", "User"]
