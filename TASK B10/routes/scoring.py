"""
Scoring Routes — Blueprint for the negative-marking endpoint.
Can be mounted into a larger FastAPI app, e.g.:

    from routes import scoring_router
    app.include_router(scoring_router)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from negative_marking_engine import NegativeMarkingEngine, InvalidScoreInputError

router = APIRouter(prefix="/score", tags=["scoring"])

engine = NegativeMarkingEngine()


class ScoreRequest(BaseModel):
    correct: Optional[int] = Field(default=0, ge=0, description="Number of correct answers")
    wrong: Optional[int] = Field(default=0, ge=0, description="Number of wrong answers")

    @field_validator("correct", "wrong", mode="before")
    @classmethod
    def none_becomes_zero(cls, v):
        return 0 if v is None else v


class ScoreResponse(BaseModel):
    final_score: float


@router.post("", response_model=ScoreResponse)
async def calculate_negative_marking_score(request: ScoreRequest):
    """Calculate final_score = correct - (wrong * penalty_per_wrong)."""
    try:
        result = engine.calculate(request.correct, request.wrong)
    except InvalidScoreInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ScoreResponse(final_score=result.final_score)


@router.get("/config")
async def get_scoring_config():
    """Return the current negative-marking configuration."""
    return {"penalty_per_wrong": engine.penalty_per_wrong}
