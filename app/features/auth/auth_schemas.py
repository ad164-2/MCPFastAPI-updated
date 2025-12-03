"""
User schemas for validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., min_length=3)
    password: str = Field(...)


class UserUpdate(BaseModel):
    """Schema for updating user."""

    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    role: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
