"""Create the PostgreSQL schema and seed official skills idempotently.

Run with ``python -m backend.app.init_db`` from the project root.
"""

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models import Assessment, AssessmentResult, Skill, Student, User  # noqa: F401
from backend.app.services.skill_service import seed_official_skills
from sqlalchemy import text


def initialize_database() -> None:
    if engine is None or SessionLocal is None:
        raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection before initialization.")

    Base.metadata.create_all(bind=engine)
    # create_all does not add columns to an existing students table. This
    # additive migration leaves legacy student rows unlinked and unchanged.
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE students ADD COLUMN IF NOT EXISTS "
                "user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_students_user_id "
                "ON students (user_id)"
            )
        )
    with SessionLocal() as db:
        seed_official_skills(db)


if __name__ == "__main__":
    initialize_database()
    print("Database tables are ready and the six official skills are seeded.")
