import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Literal

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator

from ..core.order_status import OrderStatus as CoreOrderStatus


class OrderCreate(BaseModel):
    """Схема для создания нового заказа.

    Используется при:
    - Создании заказа через API
    - Инициализации платежа
    - Передаче в сервисный слой
    """
    generation_id: Optional[uuid.UUID] = Field(
        None,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="ID связанной генерации изображения (если требуется генерация)",
        json_schema_extra={
            "nullable": True
        }
    )
    design_specs: Dict = Field(
        ...,
        example={
            "size": "A4",
            "material": "premium_paper",
            "color_profile": "CMYK"
        },
        description="Технические параметры заказа в JSON-формате",
        json_schema_extra={
            "minProperties": 1
        }
    )
    factory_id: Optional[uuid.UUID] = Field(
        None,
        example="b2c3d4e5-6789-0123-4567-890123456789",
        description="ID фабрики для производства (если известен)",
    )
    market_item_id: Optional[uuid.UUID] = Field(
        default=None,
        example="c3d4e5f6-7890-1234-5678-901234567890",
        description="ID товара из маркетплейса (если заказ на готовый продукт)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generation_id": "a1b2c3d4-5678-9012-3456-789012345678",
                "design_specs": {
                    "size": "A4",
                    "material": "glossy_paper",
                    "finish": "matte"
                },
                "factory_id": "b2c3d4e5-6789-0123-4567-890123456789"
            }
        }
    )

    @model_validator(mode='after')
    def validate_references(self) -> 'OrderCreate':
        """Проверяет взаимную исключительность generation_id и market_item_id"""
        if self.generation_id and self.market_item_id:
            raise ValueError("Заказ не может одновременно ссылаться и на генерацию, и на товар")
        if not self.generation_id and not self.market_item_id:
            raise ValueError("Заказ должен ссылаться либо на генерацию, либо на товар")
        return self

    @field_validator('design_specs')
    def validate_design_specs(self, v):
        required_fields = {'size', 'material'}
        if not required_fields.issubset(v.keys()):
            raise ValueError(f"Design specs must contain {required_fields}")
        return v


class OrderStatus(str, Enum):
    """Перечисление статусов для API, дублирует CoreOrderStatus.

    Необходимо для валидации входных/выходных данных API.
    Всегда должен синхронизироваться с:
    - app.core.order_status.OrderStatus
    - models.order.Order.status enum
    """
    CREATED = CoreOrderStatus.CREATED
    PAID = CoreOrderStatus.PAID
    PRODUCTION = CoreOrderStatus.PRODUCTION
    SHIPPED = CoreOrderStatus.SHIPPED
    COMPLETED = CoreOrderStatus.COMPLETED
    CANCELLED = CoreOrderStatus.CANCELLED


class OrderBase(BaseModel):
    """Базовая схема для создания/обновления заказа."""
    generation_id: Optional[uuid.UUID] = Field(
        None,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="ID связанной генерации изображения",
    )
    design_specs: Dict = Field(
        ...,
        example={
            "size": "A4",
            "material": "premium_paper",
            "color_profile": "CMYK"
        },
        description="Технические параметры заказа в JSON-формате",
    )


class OrderResponse(OrderBase):
    """Схема для возврата данных о заказе через API."""
    id: uuid.UUID = Field(
        ...,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="Уникальный идентификатор заказа",
    )
    status: OrderStatus = Field(
        ...,
        example=OrderStatus.CREATED,
        description="Текущий статус заказа",
    )
    amount: float = Field(
        ...,
        example=1500.0,
        ge=0,
        description="Сумма заказа в рублях",
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания заказа (UTC)",
    )
    production_deadline: Optional[datetime] = Field(
        None,
        example="2026-01-10T12:00:00Z",
        description="Планируемая дата завершения производства",
    )
    production_errors: Optional[List[str]] = Field(
        None,
        example=["Не хватило материала", "Задержка поставки"],
        description="Ошибки производства",
    )
    user_id: uuid.UUID = Field(
        ...,
        example="b2c3d4e5-6789-0123-4567-890123456789",
        description="ID пользователя-заказчика",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-5678-9012-3456-789012345678",
                "status": "created",
                "amount": 1500.0,
                "created_at": "2023-01-01T12:00:00Z",
                "generation_id": "c3d4e5f6-7890-1234-5678-901234567890",
                "design_specs": {
                    "size": "A4",
                    "material": "premium_paper"
                },
                "production_deadline": "2023-01-10T12:00:00Z",
                "production_errors": None,
                "user_id": "b2c3d4e5-6789-0123-4567-890123456789"
            }
        }
    )


class OrderUpdate(BaseModel):
    """Схема для обновления заказа"""
    status: Optional[OrderStatus] = Field(
        None,
        description="Новый статус заказа"
    )
    production_deadline: Optional[datetime] = Field(
        None,
        description="Обновленный срок производства"
    )

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if not any([self.status, self.production_deadline]):
            raise ValueError("At least one field must be provided for update")
        return self


class ChatMessageSchema(BaseModel):
    """Схема сообщения в чате заказа.

    Используется для отображения истории переписки по заказу.
    """
    id: uuid.UUID = Field(
        default=...,
        example="d3e4f5g6-7890-1234-5678-901234567890",
        description="Уникальный идентификатор сообщения"
    )
    order_id: uuid.UUID = Field(
        default=...,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="ID связанного заказа"
    )
    sender_id: uuid.UUID = Field(
        default=...,
        example="b2c3d4e5-6789-0123-4567-890123456789",
        description="ID отправителя (пользователя)"
    )
    sender_role: Literal["customer", "designer", "support"] = Field(
        default=...,
        example="customer",
        description="Роль отправителя"
    )
    message: str = Field(
        default=...,
        example="Когда будет готов мой заказ?",
        description="Текст сообщения",
        min_length=1,
        max_length=2000
    )
    attachments: List[str] = Field(
        default=...,
        default_factory=list,
        example=["https://storage.example.com/files/123.pdf"],
        description="Ссылки на прикрепленные файлы"
    )
    created_at: datetime = Field(
        default=...,
        example="2023-01-01T12:00:00Z",
        description="Дата и время отправки (UTC)"
    )
    is_read: bool = Field(
        default=False,
        description="Флаг прочтения сообщения"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "d3e4f5g6-7890-1234-5678-901234567890",
                "order_id": "a1b2c3d4-5678-9012-3456-789012345678",
                "sender_id": "b2c3d4e5-6789-0123-4567-890123456789",
                "sender_role": "customer",
                "message": "Когда будет готов мой заказ?",
                "attachments": ["https://storage.example.com/files/123.pdf"],
                "created_at": "2023-01-01T12:00:00Z",
                "is_read": False
            }
        }
    )


class OrderWithMessages(OrderResponse):
    """Расширенная схема заказа с историей сообщений чата.

    Содержит:
    - Все поля OrderResponse
    - Полную историю переписки по заказу
    - Информацию о прочтении сообщений
    """
    messages: List[ChatMessageSchema] = Field(
        default_factory=list,
        description="История сообщений по заказу (отсортированы по дате создания)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-5678-9012-3456-789012345678",
                "status": "production",
                "amount": 1500.0,
                "created_at": "2023-01-01T12:00:00Z",
                "messages": [
                    {
                        "id": "d3e4f5g6-7890-1234-5678-901234567890",
                        "order_id": "a1b2c3d4-5678-9012-3456-789012345678",
                        "sender_id": "b2c3d4e5-6789-0123-4567-890123456789",
                        "sender_role": "customer",
                        "message": "Когда будет готов заказ?",
                        "attachments": [],
                        "created_at": "2023-01-02T10:00:00Z",
                        "is_read": True
                    },
                    {
                        "id": "e4f5g6h7-8901-2345-6789-012345678901",
                        "order_id": "a1b2c3d4-5678-9012-3456-789012345678",
                        "sender_id": "f3e4d5c6-7890-1234-5678-901234567890",
                        "sender_role": "support",
                        "message": "Заказ будет готов к 15 января",
                        "attachments": ["https://storage.example.com/files/progress.pdf"],
                        "created_at": "2023-01-02T11:30:00Z",
                        "is_read": True
                    }
                ]
            }
        }
    )
