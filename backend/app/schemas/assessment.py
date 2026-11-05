"""Question, answer-only submission, and assessment result schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ASSESSMENT_QUESTION_COUNT = 5


class AssessmentOptionRead(BaseModel):
    id: str
    text: str


class AssessmentQuestionRead(BaseModel):
    id: str
    skill_id: str
    skill_name: str
    difficulty: str
    text: str
    options: list[AssessmentOptionRead]


class AssessmentAnswerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1, max_length=64)
    selected_option_id: str = Field(min_length=1, max_length=16)


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: str = Field(min_length=1, max_length=64)
    answers: list[AssessmentAnswerCreate] = Field(
        min_length=ASSESSMENT_QUESTION_COUNT,
        max_length=ASSESSMENT_QUESTION_COUNT,
    )

    @model_validator(mode="after")
    def validate_answers(self):
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Each quiz question must be answered exactly once.")
        return self


class AssessmentResultRead(BaseModel):
    skill_id: str
    skill_name: str
    score: Decimal


class AssessmentRead(BaseModel):
    id: int
    student_id: int
    assessed_at: datetime
    overall_score: Decimal
    results: list[AssessmentResultRead]


class ProgressPointRead(BaseModel):
    assessment_id: int
    skill_id: str
    skill_name: str
    score: Decimal
    assessed_at: datetime
