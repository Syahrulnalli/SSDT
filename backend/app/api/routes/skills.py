"""Read-only endpoints for the six official skill categories."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, require_database
from backend.app.models.skill import Skill
from backend.app.schemas.skill import SkillRead
from backend.app.services.skill_service import skill_payload_from_row
from skill_catalog import SKILLS

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead], summary="List official skills")
def list_skills(db: Session | None = Depends(get_db)) -> list[dict]:
    """Return official skills loaded from PostgreSQL."""
    db = require_database(db)
    rows = db.scalars(select(Skill)).all()
    by_id = {row.id: row for row in rows}
    return [
        skill_payload_from_row(by_id[item["id"]], item)
        for item in SKILLS
        if item["id"] in by_id
    ]


@router.get("/{skill_id}", response_model=SkillRead, summary="Get an official skill")
def get_skill(skill_id: str, db: Session | None = Depends(get_db)) -> dict:
    """Return one official skill from PostgreSQL, or 404 if it does not exist."""
    db = require_database(db)
    row = db.get(Skill, skill_id)
    item = next((candidate for candidate in SKILLS if candidate["id"] == skill_id), None)
    if row is None or item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found.")
    return skill_payload_from_row(row, item)
