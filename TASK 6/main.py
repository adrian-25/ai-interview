"""
FastAPI Application — Decision Engine API
Exposes the decision engine via REST endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import uuid

from decision_engine import DecisionEngine, DecisionResult, Action, Adjustment, DifficultyLevel


# Request/Response Models
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


class SessionSummary(BaseModel):
    """Session state summary."""
    session_id: str
    question_count: int
    current_difficulty: str
    score_history: list[float]
    low_score_streak: int
    max_questions: int


# FastAPI App
app = FastAPI(
    title="AI Interview Decision Engine API",
    description="Rule-based decision layer for AI Voice Interview System. Determines difficulty adjustment and session flow.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in-memory for demo; use Redis/DB in production)
sessions: Dict[str, DecisionEngine] = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Interview Decision Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "decision": "POST /decision/next",
            "session": "GET /session/{session_id}"
        }
    }


@app.post("/decision/next", response_model=DecisionResponse)
async def get_next_decision(request: DecisionRequest):
    """
    Submit a score and receive the next interview decision.
    
    - Creates new session if session_id not found
    - Evaluates score against thresholds
    - Returns difficulty adjustment and continuation decision
    - Provides human-readable reasoning
    
    Thresholds:
    - score > 0.70 → increase difficulty
    - 0.40 <= score <= 0.70 → maintain difficulty
    - score < 0.40 → decrease difficulty
    
    Stopping:
    - 2 consecutive scores < 0.40 → session ends (struggle detection)
    - 10 questions reached → session ends
    """
    # Get or create session
    if request.session_id not in sessions:
        sessions[request.session_id] = DecisionEngine(request.session_id)
    
    engine = sessions[request.session_id]
    
    try:
        result = engine.evaluate(request.score)
        return _convert_result_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/session/{session_id}", response_model=SessionSummary)
async def get_session_summary(session_id: str):
    """Get current state of a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    summary = sessions[session_id].get_session_summary()
    return SessionSummary(**summary)


@app.delete("/session/{session_id}")
async def reset_session(session_id: str):
    """Reset/delete a session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/thresholds")
async def get_thresholds():
    """Get current threshold configuration."""
    return {
        "increase_threshold": 0.70,
        "decrease_threshold": 0.40,
        "low_score_threshold": 0.40,
        "max_questions": 10,
        "consecutive_low_limit": 2,
        "difficulty_progression": "Easy → Medium → Hard"
    }


def _convert_result_to_response(result: DecisionResult) -> DecisionResponse:
    """Convert internal DecisionResult to API response model."""
    return DecisionResponse(
        next_action=result.next_action.value,
        difficulty=result.difficulty.value,
        difficulty_adjustment=result.difficulty_adjustment.value,
        question_number=result.question_number,
        reason=result.reason,
        low_score_streak=result.low_score_streak,
        session_id=result.session_id
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
