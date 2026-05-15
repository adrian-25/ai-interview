"""Dashboard endpoints."""
from fastapi import APIRouter, Depends
from services.session_service import session_service
from routers.dependencies import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/sessions")
async def get_sessions(
    limit: int = 10,
    offset: int = 0,
    user_id: str = Depends(get_current_user)
):
    """Get user's sessions with pagination."""
    sessions = await session_service.get_user_sessions(
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    
    # Format response
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            "id": session.id,
            "role": session.role,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "average_score": session.average_score,
            "question_count": len([e for e in session.conversation if e.type == "question"])
        })
    
    return {
        "sessions": sessions_data,
        "total": len(sessions_data)
    }


@router.get("/analytics")
async def get_analytics(user_id: str = Depends(get_current_user)):
    """Get user's analytics and statistics."""
    sessions = await session_service.get_user_sessions(
        user_id=user_id,
        limit=100,  # Get more for analytics
        offset=0
    )
    
    if not sessions:
        return {
            "total_questions": 0,
            "average_score": None,
            "total_sessions": 0,
            "completed_sessions": 0
        }
    
    # Calculate statistics
    total_questions = 0
    scores = []
    completed_count = 0
    
    for session in sessions:
        question_count = len([e for e in session.conversation if e.type == "question"])
        total_questions += question_count
        
        if session.status == "completed" and session.average_score is not None:
            scores.append(session.average_score)
            completed_count += 1
    
    average_score = sum(scores) / len(scores) if scores else None
    
    return {
        "total_questions": total_questions,
        "average_score": round(average_score, 2) if average_score else None,
        "total_sessions": len(sessions),
        "completed_sessions": completed_count
    }
