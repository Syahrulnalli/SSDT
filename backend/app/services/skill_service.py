"""Read and seed the fixed official skill catalog."""

from sqlalchemy.orm import Session

from backend.app.models.skill import Skill
from skill_catalog import SKILLS


def skill_payload(skill: dict) -> dict:
    focus = list(skill["focus"])
    return {
        "id": skill["id"],
        "name": skill["name"],
        "symbol": skill["symbol"],
        "description": "; ".join(focus),
        "focus": focus,
    }


def skill_payload_from_row(row: Skill, official_skill: dict) -> dict:
    """Combine persisted skill fields with the canonical display metadata."""
    payload = skill_payload(official_skill)
    payload["id"] = row.id
    payload["name"] = row.name
    payload["description"] = row.description
    return payload


def seed_official_skills(db: Session) -> None:
    """Insert missing official skills without adding non-canonical categories."""
    existing_ids = set(db.query(Skill.id).all())
    existing_ids = {row[0] for row in existing_ids}
    for item in SKILLS:
        if item["id"] not in existing_ids:
            db.add(
                Skill(
                    id=item["id"],
                    name=item["name"],
                    description="; ".join(item["focus"]),
                )
            )
    db.commit()
