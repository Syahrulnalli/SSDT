"""Load the canonical skill catalog shared with the React frontend."""

import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).with_name("skill_catalog.json")
SKILLS: tuple[dict[str, Any], ...] = tuple(
    json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
)
