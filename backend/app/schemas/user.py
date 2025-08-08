import uuid
from datetime import datetime
from typing import ClassVar, Literal, Optional 

from pydantic import BaseModel, ConfigDict, EmailStr, Field



UserRoleValues = Literal["user", "designer", "admin"]

class UserRole(BaseModel):
    """Роли пользователей в системе.

    Values:
        USER: Обычный пользователь
        DESIGNER: Дизайнер (может публиковать работы в маркетплейсе)
        ADMIN: Администратор системы
    """
    USER: ClassVar[str] = "user"
    DESIGNER: ClassVar[str] = "designer"
    ADMIN: ClassVar[str] = "admin"


class UserBase(BaseModel):
    """Базовая схема пользователя.

    Attributes:
        email (EmailStr): Email пользователя (валидируется)
        role (UserRole): Роль пользователя (по умолчанию USER)
    """
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="Роль пользователя в системе"
    )



class UserCreate(UserBase):
    """Схема для создания пользователя.

    Добавляет к UserBase поле password.
    """
    password: str = Field(..., min_length=8, max_length=50)


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя.

    Наследует UserBase и добавляет:
        id (UUID): Уникальный идентификатор пользователя
        telegram_id (Optional[str]): ID в Telegram (если привязан)
        created_at (datetime): Дата регистрации
    """
    id: uuid.UUID = Field(..., example="a1b2c3d4-5678-9012-3456-789012345678")
    telegram_id: Optional[str] = Field(None, example="123456789")
    created_at: datetime = Field(..., example="2023-01-01T00:00:00Z")

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
    email: Optional[EmailStr] = Field(None, example="new.email@example.com")
    password: Optional[str] = Field(None, min_length=8, max_length=50)
    telegram_id: Optional[str] = Field(None, example="987654321")
