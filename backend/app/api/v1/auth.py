# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.core.dependencies import get_auth_service
from backend.app.schemas.auth import TokenResponse, UserLoginResponse
from backend.app.schemas.user import UserCreate
from backend.app.services.auth import AuthService

router = APIRouter(tags=["Authentication"])


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="User Login",
    description="Authenticate user and return JWT tokens",
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

    token = auth_service.create_access_token(user)
    return UserLoginResponse(
        user=user,
        token=TokenResponse(
            access_token=token,
            token_type="bearer"
        )
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
    except EmailExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return UserLoginResponse(
        user=user,
        token=TokenResponse(
            access_token=token,
            token_type="bearer"
        )
    )
