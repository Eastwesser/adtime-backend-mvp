from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel

from backend.app.core.config import settings


class TokenPayload(BaseModel):
    """Схема полезной нагрузки JWT токена"""
    sub: str  # User ID
    exp: datetime
    role: Optional[str] = None


def create_access_token(
        user_id: str,
        expires_delta: timedelta = None,
        role: str = None
) -> str:
    """
    Создание JWT токена доступа

    Args:
        user_id: ID пользователя
        expires_delta: Время жизни токена
        role: Роль пользователя

    Returns:
        str: Подписанный JWT токен

    Пример:
        >>> token = create_access_token("user123", timedelta(minutes=30), "admin")
    """
    to_encode = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=15)),
        "role": role
    }
    return jwt.encode(
        to_encode,
        settings.JWT_PRIVATE_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(user_id: str) -> str:
    """Создание refresh-токена (срок действия 7 дней)"""
    return create_access_token(
        user_id,
        expires_delta=timedelta(days=7),
        role="refresh"
    )


def verify_token(token: str) -> TokenPayload:
    """
    Валидация и декодирование JWT токена

    Raises:
        HTTPException: Если токен невалиден или просрочен
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_yookassa_signature(notification: dict) -> bool:
    """
    Валидация подписи уведомлений от ЮKassa

    Args:
        notification: Тело уведомления

    Returns:
        bool: True если подпись валидна

    Raises:
        HTTPException: При невалидной подписи
    """
    # Реальная реализация должна проверять HMAC-SHA256 подпись
    if not notification.get("signature"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    return True  # В продакшене заменить на реальную проверку
