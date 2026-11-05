"""Assessment snapshots and per-skill results."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False
    )
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="assessments")
    results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan", order_by="AssessmentResult.skill_id"
    )


class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_assessment_result_score_range"),
        UniqueConstraint("assessment_id", "skill_id", name="uq_assessment_skill_result"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        ForeignKey("skills.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    assessment: Mapped[Assessment] = relationship(back_populates="results")
    skill: Mapped["Skill"] = relationship(back_populates="results")
