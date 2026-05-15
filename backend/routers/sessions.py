"""Session management endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from models.session import (
    SessionCreate, StartSessionResponse, AnswerRequest,
    AnswerResponse, SessionResponse, MessageType
)
from services.session_service import session_service
from services.ai_service import ai_service
from routers.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    session_data: SessionCreate,
    user_id: str = Depends(get_current_user)
):
    """Start a new interview session."""
    try:
        # Create session
        session_id = await session_service.create_session(
            user_id=user_id,
            role=session_data.role.value
        )
        
        # Generate first question
        first_question = await ai_service.generate_question(
            role=session_data.role.value,
            conversation_history=None
        )
        
        # Add question to conversation
        await session_service.add_conversation_entry(
            session_id=session_id,
            entry_type=MessageType.QUESTION,
            content=first_question
        )
        
        logger.info(f"Started session {session_id} for user {user_id}")
        
        return StartSessionResponse(
            session_id=session_id,
            first_question=first_question
        )
        
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@router.post("/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    answer_data: AnswerRequest,
    user_id: str = Depends(get_current_user)
):
    """Submit an answer and get evaluation + next question."""
    try:
        # Get session and verify ownership
        session = await session_service.get_session(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not in progress"
            )
        
        # Get the last question from conversation
        last_question = None
        for entry in reversed(session.conversation):
            if entry.type == MessageType.QUESTION:
                last_question = entry.content
                break
        
        if not last_question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No question to answer"
            )
        
        # Add answer to conversation
        await session_service.add_conversation_entry(
            session_id=session_id,
            entry_type=MessageType.ANSWER,
            content=answer_data.answer
        )
        
        # Evaluate answer
        evaluation = await ai_service.evaluate_answer(
            question=last_question,
            answer=answer_data.answer,
            role=session.role
        )
        
        # Add evaluation to conversation
        await session_service.add_conversation_entry(
            session_id=session_id,
            entry_type=MessageType.EVALUATION,
            content="",  # Evaluation stored in evaluation field
            evaluation=evaluation
        )
        
        # Generate next question
        # Build conversation history for context
        conversation_history = []
        current_qa = {}
        for entry in session.conversation:
            if entry.type == MessageType.QUESTION:
                current_qa = {"question": entry.content}
            elif entry.type == MessageType.ANSWER and current_qa:
                current_qa["answer"] = entry.content
                conversation_history.append(current_qa)
                current_qa = {}
        
        next_question = await ai_service.generate_question(
            role=session.role,
            conversation_history=conversation_history
        )
        
        # Add next question to conversation
        await session_service.add_conversation_entry(
            session_id=session_id,
            entry_type=MessageType.QUESTION,
            content=next_question
        )
        
        logger.info(f"Processed answer for session {session_id}")
        
        return AnswerResponse(
            evaluation=evaluation,
            next_question=next_question
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process answer"
        )


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """End an interview session."""
    try:
        # Verify session ownership
        session = await session_service.get_session(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Complete session
        success = await session_service.complete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to end session"
            )
        
        logger.info(f"Ended session {session_id}")
        
        return {"session_id": session_id, "status": "completed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific session."""
    session = await session_service.get_session(session_id, user_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionResponse(
        session_id=session.id,
        role=session.role,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        conversation=session.conversation,
        average_score=session.average_score
    )


@router.get("/resume/current", response_model=SessionResponse)
async def resume_session(user_id: str = Depends(get_current_user)):
    """Get the user's in-progress session if one exists."""
    session = await session_service.get_in_progress_session(user_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No in-progress session found"
        )
    
    return SessionResponse(
        session_id=session.id,
        role=session.role,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        conversation=session.conversation,
        average_score=session.average_score
    )
