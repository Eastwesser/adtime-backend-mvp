from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.schemas.user import UserResponse


class Token(BaseModel):
    """Модель токена аутентификации.

    Attributes:
        access_token (str): JWT токен для аутентификации
        token_type (str): Тип токена (по умолчанию 'bearer')
        expires_in (Optional[int]): Время жизни токена в секундах (опционально)
    """
    access_token: str = Field(
        ...,
        description="JWT токен для аутентификации",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        ...,
        description="Тип токена",
        example="bearer"
    )
    expires_in: Optional[int] = Field(
        None,
        description="Время жизни токена в секундах",
        example=3600
    )


class TokenResponse(Token):
    """Расширенная модель ответа с токеном аутентификации.

    Наследует все поля Token и добавляет:
        refresh_token (Optional[str]): Токен для обновления (опционально)
        issued_at (datetime): Время выдачи токена
        token_id (str): Уникальный идентификатор токена
        scopes (List[str]): Список разрешений токена
    """
    refresh_token: Optional[str] = Field(
        None,
        description="Токен для обновления доступа",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        json_schema_extra={"secure": True}
    )
    issued_at: datetime = Field(
        default_factory=datetime.now,
        description="Время выдачи токена",
        example="2025-01-01T00:00:00Z"
    )
    token_id: str = Field(
        ...,
        description="Уникальный идентификатор токена",
        example="tok_1MqLW2P4zWv4g4Xs4Z6Xz4W4"
    )
    scopes: list[str] = Field(
        default_factory=list,
        description="Список разрешений токена",
        example=["read", "write"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "issued_at": "2025-01-01T00:00:00Z",
                "token_id": "tok_1MqLW2P4zWv4g4Xs4Z6Xz4W4",
                "scopes": ["read", "write"]
            }
        }


class AuthRequest(BaseModel):
    """Модель запроса аутентификации по email и паролю.

    Attributes:
        email (str): Email пользователя
        password (str): Пароль пользователя
        device_id (Optional[str]): Идентификатор устройства (опционально)
    """
    email: str = Field(
        ...,
        example="user@example.com",
        description="Email пользователя",
        max_length=255
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Пароль пользователя",
        json_schema_extra={"secure": True}
    )
    device_id: Optional[str] = Field(
        None,
        description="Идентификатор устройства для привязки токена",
        example="device_12345",
    )


class UserLoginResponse(BaseModel):
    """Комбинированный ответ с данными пользователя и токеном.

    Attributes:
        user (UserResponse): Данные пользователя
        token (TokenResponse): Токен аутентификации
        requires_2fa (bool): Требуется ли двухфакторная аутентификация
    """
    user: UserResponse = Field(
        ...,
        description="Данные пользователя",
    )
    token: TokenResponse = Field(
        ...,
        description="Токен аутентификации",
    )
    requires_2fa: bool = Field(
        default=False,
        description="Требуется ли двухфакторная аутентификация"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "a1b2c3d4-5678-9012-3456-789012345678",
                    "email": "user@example.com",
                    "role": "user",
                    "created_at": "2025-01-01T00:00:00Z"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "issued_at": "2025-01-01T00:00:00Z",
                    "token_id": "tok_1MqLW2P4zWv4g4Xs4Z6Xz4W4",
                    "scopes": ["read", "write"]
                },
                "requires_2fa": False
            }
        }
