import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Статусы платежа в системе.

    Values:
        PENDING: Платеж ожидает обработки
        SUCCEEDED: Платеж успешно завершен
        CANCELED: Платеж отменен
    """
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class PaymentCreate(BaseModel):
    """Схема для создания нового платежа.

    Attributes:
        order_id (UUID): ID связанного заказа
        amount (float): Сумма платежа в рублях (должна быть > 0)
        metadata (Optional[Dict]): Дополнительные данные платежа
    """
    order_id: uuid.UUID = Field(
        ...,
        description="ID связанного заказа",
        example="a1b2c3d4-5678-9012-3456-789012345678"
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Сумма платежа в рублях",
        example=1500.00
    )
    metadata: Optional[Dict] = Field(
        None,
        description="Дополнительные метаданные платежа в формате JSON",
        example={"promo_code": "SUMMER2023"}
    )


class PaymentResponse(PaymentCreate):
    """Расширенная схема с данными о платеже для ответа API.

    Наследует все поля PaymentCreate и добавляет:
        id (UUID): Внутренний ID платежа в системе
        external_id (str): ID платежа в платежной системе (ЮKassa)
        status (PaymentStatus): Текущий статус платежа
        created_at (datetime): Дата и время создания платежа
    """
    id: uuid.UUID = Field(
        ...,
        description="Внутренний идентификатор платежа",
        example="b2c3d4e5-6789-0123-4567-890123456789"
    )
    external_id: str = Field(
        ...,
        description="Идентификатор платежа в платежной системе",
        example="pay_123456789"
    )
    status: PaymentStatus = Field(
        ...,
        description="Текущий статус платежа",
        example=PaymentStatus.PENDING
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания платежа",
        example="2023-01-01T12:00:00Z"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "b2c3d4e5-6789-0123-4567-890123456789",
                "order_id": "a1b2c3d4-5678-9012-3456-789012345678",
                "amount": 1500.00,
                "external_id": "pay_123456789",
                "status": "pending",
                "created_at": "2023-01-01T12:00:00Z",
                "metadata": {"promo_code": "SUMMER2023"}
            }
        }


class PaymentNotification(BaseModel):
    """Схема для обработки вебхуков от платежной системы ЮKassa.

    Attributes:
        event (str): Тип события (например, 'payment.succeeded')
        payment_id (str): ID платежа в ЮKassa (алиас 'object.id')
        status (PaymentStatus): Статус платежа
        amount (float): Сумма платежа
        metadata (Dict): Дополнительные данные платежа
    """
    event: str = Field(
        ...,
        description="Тип события от платежной системы",
        example="payment.succeeded"
    )
    payment_id: str = Field(
        ...,
        alias="object.id",
        description="Идентификатор платежа в ЮKassa",
        example="pay_123456789"
    )
    status: PaymentStatus = Field(
        ...,
        description="Статус платежа",
        example=PaymentStatus.SUCCEEDED
    )
    amount: float = Field(
        ...,
        description="Сумма платежа",
        example=1500.00
    )
    metadata: Dict = Field(
        ...,
        description="Метаданные платежа",
        example={"order_id": "a1b2c3d4-5678-9012-3456-789012345678"}
    )
