import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SubscriptionPlan(str, Enum):
    """Доступные тарифные планы подписки.

    Values:
        FREE: Бесплатный тариф с базовыми возможностями
        PRO: Профессиональный тариф с расширенными возможностями
        PREMIUM: Премиальный тариф с полным доступом
    """
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionCreate(BaseModel):
    """Схема для создания новой подписки.

    Attributes:
        plan (SubscriptionPlan): Выбранный тарифный план
    """
    plan: SubscriptionPlan = Field(
        default=SubscriptionPlan.FREE,
        description="Тарифный план подписки",
        example=SubscriptionPlan.PRO
    )


class SubscriptionResponse(SubscriptionCreate):
    """Схема с полными данными о подписке для ответа API.

    Наследует SubscriptionCreate и добавляет:
        id (UUID): Уникальный идентификатор подписки
        expires_at (datetime): Дата и время истечения подписки
        remaining_generations (int): Оставшееся количество генераций
        user_id (UUID): ID пользователя-владельца подписки
    """
    id: uuid.UUID = Field(
        ...,
        description="Уникальный идентификатор подписки",
        example="c3d4e5f6-7890-1234-5678-901234567890"
    )
    expires_at: datetime = Field(
        ...,
        description="Дата и время истечения срока действия подписки",
        example="2024-01-01T00:00:00Z"
    )
    remaining_generations: int = Field(
        ...,
        description="Оставшееся количество доступных генераций изображений",
        example=100
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Идентификатор пользователя-владельца подписки",
        example="a1b2c3d4-5678-9012-3456-789012345678"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "c3d4e5f6-7890-1234-5678-901234567890",
                "plan": "pro",
                "expires_at": "2024-01-01T00:00:00Z",
                "remaining_generations": 100,
                "user_id": "a1b2c3d4-5678-9012-3456-789012345678"
            }
        }
