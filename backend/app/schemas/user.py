import uuid
from datetime import datetime
from typing import Literal, Optional 

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Define allowed roles as a Literal type
UserRole = Literal["user", "designer", "admin"]


class UserBase(BaseModel):
    """Базовая схема пользователя.

    Attributes:
        email (EmailStr): Email пользователя (валидируется)
        role (UserRole): Роль пользователя (по умолчанию USER)
    """
    email: EmailStr = Field(..., max_length=255)
    role: Literal["user", "designer", "admin"] = Field(default="user")
    created_at: Optional[datetime] = Field(default=None)
    

class UserCreate(UserBase):
    """Схема для создания пользователя.

    Добавляет к UserBase поле password.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Must contain at least 8 characters"
    )
    telegram_id: Optional[str] = Field(None, max_length=100)
    
class UserResponse(UserBase):
    """Схема для ответа с данными пользователя.

    Наследует UserBase и добавляет:
        id (UUID): Уникальный идентификатор пользователя
        telegram_id (Optional[str]): ID в Telegram (если привязан)
        created_at (datetime): Дата регистрации
    """
    id: uuid.UUID
    telegram_id: Optional[str] = Field(None, max_length=100)
    created_at: Optional[datetime] = None
    balance: Optional[int] = 0  # ← ADD THIS LINE
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-5678-9012-3456-789012345678",
                "email": "user@example.com",
                "role": "user",
                "telegram_id": "123456789",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
    )


class UserUpdate(BaseModel):
    """Модель для обновления данных пользователя.

    Все поля опциональны - обновляются только переданные значения.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=50)
    telegram_id: Optional[str] = None
