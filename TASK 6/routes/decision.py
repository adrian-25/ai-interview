"""
Decision Routes — Blueprint for decision-related endpoints.
Can be mounted to main FastAPI app.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from decision_engine import DecisionEngine, DecisionResult, Action, Adjustment, DifficultyLevel


router = APIRouter(prefix="/decision", tags=["decision"])


class DecisionRequest(BaseModel):
    """Request model for decision endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Candidate answer score (0.0 - 1.0)")


class DecisionResponse(BaseModel):
    """Response model for decision endpoint."""
    next_action: str = Field(..., description="continue or end")
    difficulty: str = Field(..., description="Current difficulty level")
    difficulty_adjustment: str = Field(..., description="increase, decrease, or maintain")
    question_number: int = Field(..., description="Current question count")
    reason: str = Field(..., description="Human-readable decision explanation")
    low_score_streak: int = Field(..., description="Consecutive low score count")
    session_id: str = Field(..., description="Session identifier")


# In-memory session store (replace with Redis/DB in production)
sessions: Dict[str, DecisionEngine] = {}


@router.post("/next", response_model=DecisionResponse)
async def get_next_decision(request: DecisionRequest):
    """
    Submit a score and receive the next interview decision.
    
    Creates new session if session_id not found.
    """
    if request.session_id not in sessions:
        sessions[request.session_id] = DecisionEngine(request.session_id)
    
    engine = sessions[request.session_id]
    
    try:
        result = engine.evaluate(request.score)
        return _convert_result(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/thresholds")
async def get_thresholds():
    """Get current decision thresholds."""
    return {
        "increase_threshold": 0.70,
        "decrease_threshold": 0.40,
        "low_score_threshold": 0.40,
        "max_questions_default": 10,
        "consecutive_low_limit": 2
    }


def _convert_result(result: DecisionResult) -> DecisionResponse:
    """Convert internal result to response model."""
    return DecisionResponse(
        next_action=result.next_action.value,
        difficulty=result.difficulty.value,
        difficulty_adjustment=result.difficulty_adjustment.value,
        question_number=result.question_number,
        reason=result.reason,
        low_score_streak=result.low_score_streak,
        session_id=result.session_id
    )
