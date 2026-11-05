"""Official skill API schemas."""

from pydantic import BaseModel


class SkillRead(BaseModel):
    id: str
    name: str
    symbol: str
    description: str
    focus: list[str]
