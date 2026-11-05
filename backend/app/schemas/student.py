"""Student API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StudentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    program: str = Field(min_length=1, max_length=100)
    batch: str = Field(min_length=1, max_length=20)

    @field_validator("name", "program", "batch")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    program: str
    batch: str
    created_at: datetime


class StudentSkillRead(BaseModel):
    skill_id: str
    skill_name: str
    focus: list[str]
    latest_score: float | None
    assessed_at: datetime | None
