"""Safe account registration, login, and current-session schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

from backend.app.schemas.student import StudentRead


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9._-]+$")
    email: EmailStr
    password: SecretStr = Field(min_length=12, max_length=128)
    name: str = Field(min_length=1, max_length=120)
    program: str = Field(min_length=1, max_length=100)
    batch: str = Field(min_length=1, max_length=20)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return str(value).strip().lower()

    @field_validator("name", "program", "batch")
    @classmethod
    def trim_profile_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username_or_email: str = Field(min_length=3, max_length=255)
    password: SecretStr = Field(min_length=1, max_length=128)

    @field_validator("username_or_email")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


class AuthSessionRead(BaseModel):
    user: UserRead
    student: StudentRead
