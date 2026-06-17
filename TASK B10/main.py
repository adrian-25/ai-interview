"""
FastAPI Application — Negative Marking Engine API
Exposes the negative marking engine via a REST endpoint.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import logging

from negative_marking_engine import (
    NegativeMarkingEngine,
    InvalidScoreInputError,
    DEFAULT_PENALTY_PER_WRONG,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ScoreRequest(BaseModel):
    """Request body for POST /score. Missing fields default to 0."""
    correct: Optional[int] = Field(default=0, ge=0, description="Number of correct answers")
    wrong: Optional[int] = Field(default=0, ge=0, description="Number of wrong answers")

    @field_validator("correct", "wrong", mode="before")
    @classmethod
    def none_becomes_zero(cls, v):
        return 0 if v is None else v


class ScoreResponse(BaseModel):
    """Response body for POST /score — matches the required API contract."""
    final_score: float


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Negative Marking Engine API",
    description="Calculates penalties for incorrect answers using configurable negative marking.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = NegativeMarkingEngine()


@app.get("/")
async def root():
    """Health check / API info."""
    return {
        "status": "healthy",
        "service": "Negative Marking Engine",
        "version": "1.0.0",
        "penalty_per_wrong": DEFAULT_PENALTY_PER_WRONG,
        "endpoints": {
            "score": "POST /score",
            "config": "GET /config",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/config")
async def get_config():
    """Expose the current penalty configuration for transparency."""
    return {"penalty_per_wrong": engine.penalty_per_wrong}


@app.post("/score", response_model=ScoreResponse)
async def score(request: ScoreRequest):
    """
    Calculate final_score = correct - (wrong * penalty_per_wrong).

    - Missing `correct`/`wrong` default to 0.
    - Negative input counts are rejected with 400 (Pydantic also rejects
      them at the schema level with 422).
    - A negative `final_score` in the response is expected behaviour,
      not an error — that's what negative marking means.
    """
    try:
        result = engine.calculate(request.correct, request.wrong)
    except InvalidScoreInputError as exc:
        logger.error("Invalid score input: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))

    return ScoreResponse(final_score=result.final_score)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
