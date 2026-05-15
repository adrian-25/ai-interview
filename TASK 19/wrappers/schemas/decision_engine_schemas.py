"""Pydantic v2 schemas for the Decision Engine module."""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class NextQuestionRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session ID (MongoDB str)")
    topic: str = Field(..., description="Topic area for the next question")
    difficulty: Optional[str] = Field(None, description="Desired difficulty: easy | medium | hard")
    previous_question_ids: list[str] = Field(
        default_factory=list,
        description="IDs of questions already asked in this session",
    )


class StopDecisionRequest(BaseModel):
    session_id: str = Field(..., description="Active interview session ID")
    questions_asked: int = Field(..., ge=0, description="Total questions asked so far")
    average_score: float = Field(..., ge=0.0, le=10.0, description="Running average score (0–10)")
    elapsed_seconds: int = Field(..., ge=0, description="Elapsed session time in seconds")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class NextQuestionResponse(BaseModel):
    question_id: str = Field(..., description="MongoDB ID of the selected question")
    question_text: str
    topic: str
    difficulty: str
    metadata: Optional[dict[str, Any]] = None


class StopDecisionResponse(BaseModel):
    should_stop: bool = Field(..., description="True if the session should end")
    reason: Optional[str] = Field(None, description="Human-readable reason for the decision")
