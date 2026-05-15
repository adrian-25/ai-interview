"""Session management service."""
from database import get_database
from models.session import (
    SessionInDB, ConversationEntry, MessageType, Evaluation
)
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Handle session operations."""
    
    @staticmethod
    async def create_session(user_id: str, role: str) -> str:
        """
        Create a new interview session.
        
        Returns:
            session_id
        """
        db = get_database()
        
        session_doc = {
            "user_id": user_id,
            "role": role,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "conversation": [],
            "average_score": None
        }
        
        result = await db.sessions.insert_one(session_doc)
        logger.info(f"Created session {result.inserted_id} for user {user_id}")
        return str(result.inserted_id)
    
    @staticmethod
    async def get_session(session_id: str, user_id: str) -> Optional[SessionInDB]:
        """
        Get a session by ID with authorization check.
        
        Returns:
            SessionInDB or None if not found/unauthorized
        """
        db = get_database()
        
        try:
            session_doc = await db.sessions.find_one({
                "_id": ObjectId(session_id),
                "user_id": user_id
            })
            
            if not session_doc:
                return None
            
            session_doc["_id"] = str(session_doc["_id"])
            return SessionInDB(**session_doc)
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    @staticmethod
    async def add_conversation_entry(
        session_id: str,
        entry_type: MessageType,
        content: str,
        evaluation: Optional[Evaluation] = None
    ) -> bool:
        """
        Add an entry to the conversation history.
        
        Returns:
            True if successful
        """
        db = get_database()
        
        try:
            entry = {
                "type": entry_type.value,
                "content": content,
                "timestamp": datetime.utcnow(),
                "evaluation": evaluation.model_dump() if evaluation else None
            }
            
            result = await db.sessions.update_one(
                {"_id": ObjectId(session_id)},
                {"$push": {"conversation": entry}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error adding conversation entry: {e}")
            return False
    
    @staticmethod
    async def complete_session(session_id: str) -> bool:
        """
        Mark a session as completed and calculate average score.
        
        Returns:
            True if successful
        """
        db = get_database()
        
        try:
            # Get session to calculate average score
            session_doc = await db.sessions.find_one({"_id": ObjectId(session_id)})
            if not session_doc:
                return False
            
            # Calculate average score from evaluations
            scores = []
            for entry in session_doc.get("conversation", []):
                if entry.get("evaluation") and entry["evaluation"].get("score") is not None:
                    scores.append(entry["evaluation"]["score"])
            
            average_score = sum(scores) / len(scores) if scores else None
            
            # Update session
            result = await db.sessions.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "average_score": average_score
                    }
                }
            )
            
            logger.info(f"Completed session {session_id} with average score {average_score}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error completing session: {e}")
            return False
    
    @staticmethod
    async def get_user_sessions(
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[SessionInDB]:
        """
        Get all sessions for a user with pagination.
        
        Returns:
            List of SessionInDB objects
        """
        db = get_database()
        
        try:
            cursor = db.sessions.find(
                {"user_id": user_id}
            ).sort("started_at", -1).skip(offset).limit(limit)
            
            sessions = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                sessions.append(SessionInDB(**doc))
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    @staticmethod
    async def get_in_progress_session(user_id: str) -> Optional[SessionInDB]:
        """
        Get the user's in-progress session if one exists.
        
        Returns:
            SessionInDB or None
        """
        db = get_database()
        
        try:
            session_doc = await db.sessions.find_one({
                "user_id": user_id,
                "status": "in_progress"
            })
            
            if not session_doc:
                return None
            
            session_doc["_id"] = str(session_doc["_id"])
            return SessionInDB(**session_doc)
            
        except Exception as e:
            logger.error(f"Error getting in-progress session: {e}")
            return None


session_service = SessionService()
