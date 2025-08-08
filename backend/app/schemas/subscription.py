import uuid
from datetime import datetime
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

SubscriptionPlanValues = Literal["free", "pro", "premium"]

class SubscriptionPlan(BaseModel):
    """Доступные тарифные планы подписки.

    Values:
        FREE: Бесплатный тариф с базовыми возможностями
        PRO: Профессиональный тариф с расширенными возможностями
        PREMIUM: Премиальный тариф с полным доступом
    """
    FREE: ClassVar[str] = 'free'
    PRO: ClassVar[str] = 'pro'
    PREMIUM: ClassVar[str] = 'premium'


class SubscriptionCreate(BaseModel):
    """Схема для создания новой подписки.

    Attributes:
        plan (SubscriptionPlan): Выбранный тарифный план
    """
    plan: SubscriptionPlanValues = Field(default="free", description="Subscription plan")


class SubscriptionResponse(SubscriptionCreate):
    """Схема с полными данными о подписке для ответа API.

    Наследует SubscriptionCreate и добавляет:
        id (UUID): Уникальный идентификатор подписки
        expires_at (datetime): Дата и время истечения подписки
        remaining_generations (int): Оставшееся количество генераций
        user_id (UUID): ID пользователя-владельца подписки
    """
    id: uuid.UUID = Field(..., description="Subscription ID")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    remaining_generations: int = Field(..., description="Remaining generations")
    user_id: uuid.UUID = Field(..., description="User ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "c3d4e5f6-7890-1234-5678-901234567890",
                "plan": "pro",
                "expires_at": "2024-01-01T00:00:00Z",
                "remaining_generations": 100,
                "user_id": "a1b2c3d4-5678-9012-3456-789012345678"
            }
        }
    )
    