"""
schemas/user.py - Pydantic Schemas for User & Authentication
=============================================================
These schemas define:
  - What data the API accepts (request bodies)
  - What data the API returns (response bodies)

Pydantic v2 is used. Note: 'model_config' replaces the old class Config.
"""

from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, field_validator, model_validator


# ── Request Schemas (what the client sends) ───────────────────────────────────

class UserCreate(BaseModel):
    """Schema for user registration. Validates passwords match and are strong enough."""
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank.")
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @model_validator(mode="after")
    def passwords_must_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


# ── Response Schemas (what the API returns) ───────────────────────────────────

class UserResponse(BaseModel):
    """
    Safe user response — never includes password_hash.
    Returned after login, register, and GET /auth/me.
    """
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # Allows ORM → Pydantic conversion


class TokenResponse(BaseModel):
    """Returned after successful login or registration."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic success/info message response."""
    message: str
    detail: Optional[str] = None
