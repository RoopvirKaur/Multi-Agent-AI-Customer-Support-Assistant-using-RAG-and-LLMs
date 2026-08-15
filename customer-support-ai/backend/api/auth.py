"""
Authentication API Endpoints
Routes: /api/auth/register, /api/auth/login, /api/auth/refresh, /api/auth/me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database import crud
from backend.database.models import User
from backend.models.user import UserCreate, UserLogin, UserOut, Token
from backend.middleware.auth_middleware import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user account:
    - Validates email and minimum password length
    - Hashes password with bcrypt
    - Returns authentication JWT token and user profile
    """
    existing_user = await crud.get_user_by_email(db, email=payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    hashed_pw = get_password_hash(payload.password)
    user = await crud.create_user(
        db,
        email=payload.email,
        password_hash=hashed_pw,
        name=payload.name,
    )

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
    }
    access_token = create_access_token(data=token_payload)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Log in and retrieve JWT access token",
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate with email and password:
    - Validates credentials against stored bcrypt hash
    - Returns JWT access token upon successful authentication
    """
    user = await crud.get_user_by_email(db, email=payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
    }
    access_token = create_access_token(data=token_payload)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh JWT access token",
)
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    Issue a new JWT token with a refreshed expiration window for the current active user.
    """
    token_payload = {
        "sub": str(current_user.id),
        "email": current_user.email,
    }
    access_token = create_access_token(data=token_payload)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(current_user),
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve profile details for the currently authenticated user.
    """
    return UserOut.model_validate(current_user)
