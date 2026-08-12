"""
Pydantic schemas for User authentication and profiles.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Payload for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserLogin(BaseModel):
    """Payload for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserOut(BaseModel):
    """Public user profile response."""
    id: uuid.UUID
    email: str
    name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    """Decoded JWT payload data."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
