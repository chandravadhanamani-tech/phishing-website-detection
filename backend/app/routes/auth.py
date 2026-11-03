"""
routes/auth.py - Authentication Endpoints
==========================================
Provides:
  POST /auth/register  - Register a new user account
  POST /auth/login     - Login with email/password, receive JWT
  GET  /auth/me        - Get current logged-in user's profile
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import MessageResponse, TokenResponse, UserCreate, UserLogin, UserResponse

logger   = logging.getLogger(__name__)
settings = get_settings()
router   = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Creates a new user account and returns a JWT token for immediate login.",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - Validates that email is not already taken
    - Hashes the password before storage (never stored as plain text)
    - Returns a JWT token so the user is logged in immediately
    """
    # Check for duplicate email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Create new user
    new_user = User(
        name          = user_data.name.strip(),
        email         = user_data.email.lower().strip(),
        password_hash = hash_password(user_data.password),
        role          = "user",
        is_active     = True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    logger.info(f"New user registered: {new_user.email}")

    return TokenResponse(
        access_token = token,
        token_type   = "bearer",
        user         = UserResponse.model_validate(new_user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticates the user and returns a JWT Bearer token.",
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint.
    
    - Finds user by email
    - Verifies password against bcrypt hash
    - Returns JWT token on success
    - Returns 401 on invalid credentials (same message for security — don't reveal which part was wrong)
    """
    user = db.query(User).filter(
        User.email == credentials.email.lower().strip()
    ).first()

    # Validate credentials (same error message regardless of which part failed)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    # Generate JWT token
    token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token = token,
        token_type   = "bearer",
        user         = UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile.
    Requires a valid JWT Bearer token in the Authorization header.
    """
    return UserResponse.model_validate(current_user)
