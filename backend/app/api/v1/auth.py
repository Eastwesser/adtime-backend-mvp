# backend/app/api/v1/auth.py
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_auth_service
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import (
    TokenResponse,
    UserLoginResponse
)
from app.schemas.user import UserCreate
from app.services.auth import AuthService

router = APIRouter(tags=["Authentication"])


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User Login",
    description="""
    Authenticate user and return JWT tokens.

    Returns:
    - access_token: Short-lived token (15-30 min)
    - refresh_token: Long-lived token (7 days)
    - user: User data
    """,
    responses={
        200: {"description": "Successful authentication"},
        401: {"description": "Invalid credentials"},
        400: {"description": "Validation error"}
    },
    tags=["Authentication"]
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return JWT tokens with user data"""
    user = await auth_service.authenticate_user(
        email=form_data.username,  # OAuth2 uses 'username' field for email
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        str(user.id),
        expires_delta=timedelta(minutes=30),
        role=user.role
    )

    refresh_token = create_refresh_token(str(user.id))

    return UserLoginResponse(
        user=user,
        access_token=TokenResponse(
            access_token=access_token,
            token_type="bearer"
        ),
        refresh_token=refresh_token
    )


class EmailExistsError(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is already registered"
        )


@router.post(
    "/register",
    response_model=UserLoginResponse,
    summary="User Registration",
    description="Create new user account",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already exists"},
        409: {"description": "Email or Telegram ID already exists"},
        422: {"description": "Validation error"}
    },
    tags=["Authentication"]
)
async def register(
        user_create: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Register new user and return tokens"""
    if await auth_service.email_exists(user_create.email):
        raise EmailExistsError(user_create.email) 
    
    try:
        user = await auth_service.register_user(user_create)
        
        # Create tokens with all required fields
        access_token = create_access_token(
            str(user.id),
            expires_delta=timedelta(minutes=30),
            role=user.role
        )
        refresh_token = create_refresh_token(str(user.id))

        return UserLoginResponse(
            user=user,
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                token_id=str(uuid.uuid4()),
                expires_in=1800,
                issued_at=datetime.now(timezone.utc).isoformat(),
                scopes=["read", "write"],
                refresh_token=refresh_token  # Include refresh_token here
            ),
            requires_2fa=False
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    