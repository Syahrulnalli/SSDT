"""Temporary frontend preview data. Replace these constants with real records later.

Nothing in this module is produced by an assessment or an AI/ML model.
"""

DEMO_SKILL_SCORES = {
    "python": 64,
    "machine-learning": 47,
    "artificial-intelligence": 58,
    "sql-databases": 73,
    "web-development": 69,
    "problem-solving-algorithms": 55,
}

DEMO_GAPS = (
    {"skill_id": "machine-learning", "status": "Focus area", "tone": "warm"},
    {"skill_id": "artificial-intelligence", "status": "Building foundations", "tone": "cool"},
    {"skill_id": "problem-solving-algorithms", "status": "Keep practicing", "tone": "neutral"},
)

DEMO_RECOMMENDATIONS = (
    {
        "title": "Strengthen machine learning fundamentals",
        "detail": "Review core learning types and how training data supports a model.",
        "skill_id": "machine-learning",
        "kind": "LEARNING FOCUS",
    },
    {
        "title": "Practice algorithmic problem solving",
        "detail": "Work through small problems and explain the steps in your solution.",
        "skill_id": "problem-solving-algorithms",
        "kind": "PRACTICE IDEA",
    },
    {
        "title": "Build a small FastAPI and ML project",
        "detail": "Bring web development and machine learning together in a guided project.",
        "skill_id": "web-development",
        "kind": "PROJECT IDEA",
    },
)

DEMO_PROGRESS = (
    {"label": "Mar", "value": 42},
    {"label": "Apr", "value": 48},
    {"label": "May", "value": 54},
    {"label": "Jun", "value": 61},
)
