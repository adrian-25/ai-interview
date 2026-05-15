"""Pydantic v2 schemas for the Scoring module."""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class ScoreAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session ID")
    question_id: str = Field(..., description="MongoDB ID of the question being answered")
    answer_text: str = Field(..., min_length=1, description="Candidate's answer text")
    expected_keywords: Optional[list[str]] = Field(
        None, description="Keywords the scoring engine should look for"
    )


class SessionScoreRequest(BaseModel):
    session_id: str = Field(..., description="Completed or active session ID")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ScoreAnswerResponse(BaseModel):
    question_id: str
    score: float = Field(..., ge=0.0, le=10.0, description="Score for this answer (0–10)")
    feedback: Optional[str] = None
    matched_keywords: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class SessionScoreResponse(BaseModel):
    session_id: str
    total_questions: int = Field(..., ge=0)
    average_score: float = Field(..., ge=0.0, le=10.0)
    scores: list[ScoreAnswerResponse]
