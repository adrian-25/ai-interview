"""
Negative Marking Engine
========================
Deterministic, rule-based calculator for scoring with negative marking.

Formula
-------
    final_score = correct - (wrong * penalty_per_wrong)

Default penalty: 0.25 per wrong answer.
    e.g. correct=8, wrong=2  ->  8 - (2 * 0.25) = 7.5

Design Principles (mirrors the Decision Engine module in this project)
------------------------------------------------------------------
- Determinism: same input always produces the same output.
- Auditability: result carries the inputs and penalty used, not just
  the final number, so a caller/logger can reconstruct "why".
- Configurability: penalty_per_wrong is a constructor parameter, not a
  hardcoded constant, so different exams/sections can use different
  negative-marking schemes without code changes.
- Safety: invalid *inputs* (negative counts, wrong types) raise a clear
  error. An invalid *result* (a negative final_score) is NOT an error —
  that's the entire point of negative marking and must be allowed.
"""
from dataclasses import dataclass
from typing import Optional, Union

Number = Union[int, float]

DEFAULT_PENALTY_PER_WRONG = 0.25


class InvalidScoreInputError(ValueError):
    """Raised when `correct` / `wrong` counts are missing-but-invalid,
    non-numeric, or negative. Negative *counts* don't make sense
    (you can't answer -1 questions), so they are rejected here —
    this is distinct from the final_score itself going negative,
    which is expected and allowed."""


@dataclass(frozen=True)
class ScoreResult:
    """Structured result of a negative-marking calculation."""
    final_score: float
    correct: int
    wrong: int
    penalty_per_wrong: float
    total_penalty: float

    def to_dict(self) -> dict:
        """Shape matching the public API contract: {"final_score": float}."""
        return {"final_score": self.final_score}


class NegativeMarkingEngine:
    """
    Rule-based negative marking engine.

    Parameters
    ----------
    penalty_per_wrong: float
        Points deducted per wrong answer. Must be >= 0. Defaults to 0.25.
    """

    def __init__(self, penalty_per_wrong: float = DEFAULT_PENALTY_PER_WRONG) -> None:
        if not isinstance(penalty_per_wrong, (int, float)) or penalty_per_wrong < 0:
            raise ValueError("penalty_per_wrong must be a non-negative number")
        self.penalty_per_wrong = float(penalty_per_wrong)

    def calculate(
        self,
        correct: Optional[Number] = None,
        wrong: Optional[Number] = None,
    ) -> ScoreResult:
        """
        Calculate the final score for a given number of correct/wrong answers.

        Missing values (`None`) default to 0 — a candidate who answered
        nothing has 0 correct and 0 wrong, not an error.

        Raises
        ------
        InvalidScoreInputError
            If `correct` or `wrong` is negative or not numeric.
        """
        correct = 0 if correct is None else correct
        wrong = 0 if wrong is None else wrong

        for name, value in (("correct", correct), ("wrong", wrong)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise InvalidScoreInputError(f"'{name}' must be a number, got {type(value).__name__}")
            if value < 0:
                raise InvalidScoreInputError(f"'{name}' cannot be negative, got {value}")

        total_penalty = wrong * self.penalty_per_wrong
        # round() avoids float artifacts like 7.499999999999999
        final_score = round(correct - total_penalty, 4)

        return ScoreResult(
            final_score=final_score,
            correct=int(correct) if float(correct).is_integer() else correct,
            wrong=int(wrong) if float(wrong).is_integer() else wrong,
            penalty_per_wrong=self.penalty_per_wrong,
            total_penalty=round(total_penalty, 4),
        )


# A ready-to-use default engine for simple, functional-style calls.
_default_engine = NegativeMarkingEngine()


def calculate_score(
    correct: Optional[Number] = None,
    wrong: Optional[Number] = None,
    penalty_per_wrong: Optional[float] = None,
) -> dict:
    """
    Convenience function returning the public API response shape directly:
        {"final_score": <float>}
    """
    engine = _default_engine if penalty_per_wrong is None else NegativeMarkingEngine(penalty_per_wrong)
    return engine.calculate(correct, wrong).to_dict()
