"""Pydantic v2 schemas for the Question Bank module."""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class FetchQuestionRequest(BaseModel):
    question_id: str = Field(..., description="MongoDB ID of the question to fetch")


class FetchByTopicRequest(BaseModel):
    topic: str = Field(..., description="Topic to filter questions by")
    difficulty: Optional[str] = Field(None, description="Optional difficulty filter")
    limit: int = Field(10, ge=1, le=100, description="Max number of questions to return")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FetchQuestionResponse(BaseModel):
    question_id: str
    question_text: str
    topic: str
    difficulty: str
    expected_keywords: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class FetchByTopicResponse(BaseModel):
    questions: list[FetchQuestionResponse]
    total: int = Field(..., ge=0)
