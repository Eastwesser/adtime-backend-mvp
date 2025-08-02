import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class PaymentCreate(BaseModel):
    """Схема для создания платежа"""
    order_id: uuid.UUID = Field(..., description="ID связанного заказа")
    amount: float = Field(..., gt=0, description="Сумма в рублях")
    metadata: Optional[Dict] = Field(
        None,
        description="Дополнительные данные платежа"
    )


class PaymentResponse(PaymentCreate):
    """Схема для ответа с данными платежа"""
    id: uuid.UUID
    external_id: str = Field(..., description="ID платежа в ЮKassa")
    status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentNotification(BaseModel):
    """Схема для вебхука от ЮKassa"""
    event: str
    payment_id: str = Field(..., alias="object.id")
    status: PaymentStatus
    amount: float
    metadata: Dict
