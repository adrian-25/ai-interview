"""User data models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation request model."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    """User model as stored in database."""
    id: str = Field(alias="_id")
    email: str
    password_hash: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """User response model (without sensitive data)."""
    user_id: str
    email: str
    token: str
