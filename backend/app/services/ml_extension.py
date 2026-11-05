"""Testable interface for a future trained predictor; no model is configured."""

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class SkillObservation:
    skill_id: str
    score: float
    assessed_at: str


@dataclass(frozen=True)
class SkillPrediction:
    skill_id: str
    predicted_score: float
    evaluation_name: str


class SkillPredictor(Protocol):
    """An injectable future model must accept observed history and name its evaluation."""

    def predict(self, observations: Sequence[SkillObservation]) -> Sequence[SkillPrediction]: ...


# None is intentional: the current data and evaluation evidence do not justify a model.
predictor: SkillPredictor | None = None
