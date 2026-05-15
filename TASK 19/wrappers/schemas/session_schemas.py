"""Pydantic v2 schemas for the Session module."""
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="MongoDB ID of the user starting the session")
    topic: str = Field(..., description="Interview topic for this session")
    difficulty: Optional[str] = Field(None, description="Desired difficulty level")
    max_questions: Optional[int] = Field(None, ge=1, description="Max questions for the session")


class UpdateSessionRequest(BaseModel):
    session_id: str = Field(..., description="MongoDB ID of the session to update")
    questions_asked: Optional[int] = Field(None, ge=0)
    current_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    status: Optional[str] = Field(None, description="Session status: active | paused | completed")
    metadata: Optional[dict[str, Any]] = None


class CloseSessionRequest(BaseModel):
    session_id: str = Field(..., description="MongoDB ID of the session to close")
    final_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    summary: Optional[str] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="Newly created session ID")
    user_id: str
    topic: str
    status: str
    created_at: str


class UpdateSessionResponse(BaseModel):
    session_id: str
    updated: bool
    status: Optional[str] = None


class CloseSessionResponse(BaseModel):
    session_id: str
    closed: bool
    final_score: Optional[float] = None
    summary: Optional[str] = None
