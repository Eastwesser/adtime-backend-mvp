import uuid
from datetime import datetime
from typing import Any, Optional, Dict, List, Literal

from pydantic import BaseModel, Field, ConfigDict, computed_field, model_validator, field_validator
from app.core.order_status import OrderStatus  # Add this import
# Define status values as Literal type
OrderStatusValues = Literal[OrderStatus.CREATED, "paid", "production", "shipped", "completed", "cancelled"]

class OrderCreate(BaseModel):
    """Схема для создания нового заказа."""
    generation_id: Optional[uuid.UUID] = Field(
        None,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="ID связанной генерации изображения (если требуется генерация)",
        json_schema_extra={"nullable": True}
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

    @computed_field
    @property
    def webhooks(self) -> list[str]:
        """Available webhook events for this resource"""
        return [
            "order.created",
            "order.updated",
            "order.completed"
        ]

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
    id: uuid.UUID = Field(...)
    status: OrderStatusValues = Field(...)
    amount: int = Field(
        ...,
        example=150000,  # 1500.00 RUB
        ge=0,
        description="Order amount in kopecks",
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
    user_id: uuid.UUID = Field(
        ...,
        example="b2c3d4e5-6789-0123-4567-890123456789",
        description="ID пользователя-заказчика",
    )
    links: Dict[str, Any] = Field(
        default_factory=lambda: {
            "self": {"href": "/orders/{id}"},
            "factory": {"href": "/factories/{factory_id}"}
        }
    )

    @computed_field
    @property
    def links(self) -> dict:
        base = {
            "self": {"href": f"/orders/{self.id}", "method": "GET"},
            "update": {"href": f"/orders/{self.id}", "method": "PATCH"}
        }
        
        if self.factory_id:
            base["factory"] = {
                "href": f"/factories/{self.factory_id}",
                "method": "GET"
            }
            
        if self.status == "created":
            base["pay"] = {
                "href": f"/orders/{self.id}/payments",
                "method": "POST"
            }
            
        return base
    
    @computed_field
    @property
    def rate_limit(self) -> dict:
        return {
            "remaining": {"header": "X-RateLimit-Remaining"},
            "reset": {"header": "X-RateLimit-Reset"}
        }

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "status": OrderStatus.CREATED,
                "amount": 1500.0,
                "created_at": "2023-01-01T12:00:00Z",
                "generation_id": "c3d4e5f6-7890-1234-5678-901234567890",
                "design_specs": {
                    "size": "A4",
                    "material": "premium_paper"
                },
                "production_deadline": "2023-01-10T12:00:00Z",
                "user_id": "b2c3d4e5-6789-0123-4567-890123456789"
            }
        }
    )

class OrderUpdate(BaseModel):
    """Схема для обновления заказа"""
    status: Optional[OrderStatusValues] = Field(
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
    """Схема сообщения в чате заказа."""
    id: uuid.UUID = Field(
        ...,
        example="d3e4f5g6-7890-1234-5678-901234567890",
        description="Уникальный идентификатор сообщения"
    )
    order_id: uuid.UUID = Field(
        ...,
        example="a1b2c3d4-5678-9012-3456-789012345678",
        description="ID связанного заказа"
    )
    sender_id: uuid.UUID = Field(
        ...,
        example="b2c3d4e5-6789-0123-4567-890123456789",
        description="ID отправителя (пользователя)"
    )
    sender_role: Literal["customer", "designer", "support"] = Field(
        ...,
        example="customer",
        description="Роль отправителя"
    )
    message: str = Field(
        ...,
        example="Когда будет готов мой заказ?",
        description="Текст сообщения",
        min_length=1,
        max_length=2000
    )
    attachments: List[str] = Field(
        default_factory=list,
        example=["https://storage.example.com/files/123.pdf"],
        description="Ссылки на прикрепленные файлы"
    )
    created_at: datetime = Field(
        ...,
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
    """Расширенная схема заказа с историей сообщений чата."""
    messages: List[ChatMessageSchema] = Field(
        default_factory=list,
        description="История сообщений по заказу"
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
                    }
                ]
            }
        }
    )
    