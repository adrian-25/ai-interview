"""Session data models."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """Available interview roles."""
    FRONTEND = "Frontend Developer"
    BACKEND = "Backend Developer"
    FULLSTACK = "Full Stack Developer"
    AI_ML = "AI/ML Engineer"
    DATA_ANALYST = "Data Analyst"


class MessageType(str, Enum):
    """Message types in conversation."""
    QUESTION = "question"
    ANSWER = "answer"
    EVALUATION = "evaluation"


class Evaluation(BaseModel):
    """Answer evaluation model."""
    score: float = Field(..., ge=0, le=10)
    strengths: List[str]
    improvements: List[str]
    suggestion: str


class ConversationEntry(BaseModel):
    """Single conversation entry."""
    type: MessageType
    content: str
    timestamp: datetime
    evaluation: Optional[Evaluation] = None


class SessionCreate(BaseModel):
    """Session creation request."""
    role: Role


class SessionInDB(BaseModel):
    """Session model as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    role: str
    status: str  # "in_progress" or "completed"
    started_at: datetime
    completed_at: Optional[datetime] = None
    conversation: List[ConversationEntry] = []
    average_score: Optional[float] = None
    
    class Config:
        populate_by_name = True


class SessionResponse(BaseModel):
    """Session response model."""
    session_id: str
    role: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    conversation: List[ConversationEntry] = []
    average_score: Optional[float] = None


class StartSessionResponse(BaseModel):
    """Response when starting a new session."""
    session_id: str
    first_question: str


class AnswerRequest(BaseModel):
    """Answer submission request."""
    answer: str = Field(..., min_length=1, max_length=2000)


class AnswerResponse(BaseModel):
    """Response after submitting an answer."""
    evaluation: Evaluation
    next_question: Optional[str] = None
