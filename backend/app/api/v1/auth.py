# backend/app/api/v1/auth.py
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.dependencies import get_auth_service, get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.password_validation import validate_password_strength
from app.core.rate_limiter import get_login_limiter, get_register_limiter
from app.core.rate_limiter import RateLimiter
from app.core.config import settings
from app.schemas.auth import (
    CheckEmailRequest,
    CheckEmailResponse,
    QuickRegisterRequest,
    QuickSessionRequest,
    QuickSessionResponse,
    TokenResponse,
    UserLoginResponse
)
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.repositories.user import UserRepository

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
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service),
        limiter: RateLimiter = Depends(get_login_limiter),
):
    """Authenticate user and return JWT tokens with user data"""
    await limiter.check_request(f"login:{form_data.username}")
    
    user = await auth_service.authenticate_user(
        email=form_data.username,
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

    # ДОБАВЛЯЕМ УСТАНОВКУ КУК
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,  # В production всегда True
        samesite="lax",
        max_age=1800,  # 30 минут
        path="/",
    )
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=604800,  # 7 дней
        path="/api/v1/auth/refresh",  # Только для refresh
    )

    return UserLoginResponse(
        user=user,
        token=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            token_id=str(uuid.uuid4()),  # ← ADDED
            expires_in=1800,  # ← ADDED (30 minutes in seconds)
            issued_at=datetime.now(timezone.utc).isoformat(),  # ← ADDED
            scopes=["read", "write"],  # ← ADDED
            refresh_token=refresh_token  # ← ADDED
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
        response: Response, 
        user_create: UserCreate,
        auth_service: AuthService = Depends(get_auth_service),
        limiter: RateLimiter = Depends(get_register_limiter)
):
    """Register new user and return tokens"""

    # Rate limiting
    await limiter.check_request(f"register:{user_create.email}")
    # Проверка пароля
    validate_password_strength(user_create.password)

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


        # После создания токенов добавляем установку кук:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=1800,
            path="/",
        )
        
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="strict",
            max_age=604800,
            path="/api/v1/auth/refresh",
        )

        return UserLoginResponse(
            user=user,
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                token_id=str(uuid.uuid4()),
                expires_in=1800,
                issued_at=datetime.now(timezone.utc).isoformat(),
                scopes=["read", "write"],
                refresh_token=refresh_token,
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


@router.post("/check-email", response_model=CheckEmailResponse)
async def check_email(
    request: CheckEmailRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    exists = await auth_service.email_exists(request.email)
    return {"exists": exists}

@router.post("/quick-session", response_model=QuickSessionResponse)
async def create_quick_session(
    request: QuickSessionRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.create_guest_session(request.device_id)

@router.post("/quick-register", response_model=UserLoginResponse)
async def quick_register(
    request: QuickRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.quick_register(
        request.device_id, 
        request.email, 
        request.phone
    )
    
    # Создать токены как в обычном login
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
            refresh_token=refresh_token
        ),
        requires_2fa=False
    )

@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token from cookies"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    try:
        # Валидируем refresh token
        payload = jwt.decode(
            refresh_token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if not user_id or payload.get("role") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        # Используем auth_service для получения пользователя
        user_repo = UserRepository(session)
        user = await user_repo.get(uuid.UUID(user_id))
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        # Создаем новые токены
        new_access_token = create_access_token(
            user_id,
            expires_delta=timedelta(minutes=30),
            role=user.role
        )
        
        new_refresh_token = create_refresh_token(user_id)
        
        # Обновляем куки
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=1800,
            path="/",
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="strict",
            max_age=604800,
            path="/api/v1/auth/refresh",
        )
        
        return {
            "message": "Tokens refreshed successfully",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(response: Response):
    """Clear authentication cookies"""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return {"message": "Logged out successfully"}
        