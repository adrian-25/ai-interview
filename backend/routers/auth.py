"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status
from models.user import UserCreate, UserLogin, UserResponse
from services.auth_service import auth_service
from database import get_database
from datetime import datetime
from utils.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Create a new user account."""
    db = get_database()
    
    # Validate email format
    if not auth_service.validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("Invalid email format", "INVALID_EMAIL")
        )
    
    # Validate password strength
    is_valid, error_msg = auth_service.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(error_msg, "WEAK_PASSWORD")
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("Email already registered", "EMAIL_EXISTS")
        )
    
    # Hash password and create user
    password_hash = auth_service.hash_password(user_data.password)
    
    user_doc = {
        "email": user_data.email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Generate JWT token
    token = auth_service.create_jwt(user_id)
    
    logger.info(f"User created: {user_data.email}")
    
    return success_response({
        "user_id": user_id,
        "email": user_data.email,
        "token": token
    }, "Account created successfully")


@router.post("/login")
async def login(credentials: UserLogin):
    """Authenticate a user and return JWT token."""
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("Invalid email or password", "INVALID_CREDENTIALS")
        )
    
    # Verify password
    if not auth_service.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("Invalid email or password", "INVALID_CREDENTIALS")
        )
    
    # Generate JWT token
    user_id = str(user["_id"])
    token = auth_service.create_jwt(user_id)
    
    logger.info(f"User logged in: {credentials.email}")
    
    return success_response({
        "user_id": user_id,
        "email": user["email"],
        "token": token
    }, "Login successful")


@router.get("/verify")
async def verify_token(token: str):
    """Verify a JWT token."""
    user_id = auth_service.verify_jwt(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("Invalid or expired token", "INVALID_TOKEN")
        )
    
    return success_response({
        "valid": True,
        "user_id": user_id
    })
