"""Shared dependencies for routers."""
from fastapi import Header, HTTPException, status
from services.auth_service import auth_service


async def get_current_user(authorization: str = Header(...)) -> str:
    """
    Extract and verify JWT token from Authorization header.
    
    Returns:
        user_id if token is valid
        
    Raises:
        HTTPException if token is invalid or missing
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = auth_service.verify_jwt(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_id
