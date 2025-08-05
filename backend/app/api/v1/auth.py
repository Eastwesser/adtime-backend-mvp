# backend/app/api/v1/auth.py
from datetime import timedelta

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


class EmailExistsError:
    pass


@router.post(
    "/register",
    response_model=UserLoginResponse,
    summary="User Registration",
    description="Create new user account",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already exists"},
        422: {"description": "Validation error"}
    },
    tags=["Authentication"]
)
async def register(
        user_create: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Register new user and return tokens"""
    user = await auth_service.register_user(user_create)
    token = auth_service.create_access_token(user)

    try:
        user = await auth_service.register_user(user_create)
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return UserLoginResponse(
            user=user,
            access_token=TokenResponse(
                access_token=access_token,
                token_type="bearer"
            ),
            refresh_token=refresh_token
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
