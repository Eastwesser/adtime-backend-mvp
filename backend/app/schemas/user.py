# schemas/user.py
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    DESIGNER = "designer"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)


class UserResponse(UserBase):
    id: uuid.UUID
    telegram_id: Optional[str]
    created_at: datetime
    role: str

    class Config:
        from_attributes = True  # Для совместимости с ORM (альтернатива orm_mode)
