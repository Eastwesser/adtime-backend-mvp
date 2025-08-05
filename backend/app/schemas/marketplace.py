from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductType(str, Enum):
    BANNER = "banner"
    STANDEE = "standee"
    BILLBOARD = "billboard"
    DIGITAL = "digital"


class MarketItem(BaseModel):
    id: UUID = Field(
        ...,
        example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    )
    title: str = Field(
        ...,
        example="Summer Sale Banner",
        max_length=100,
        description="Название товара",
    )
    description: str = Field(
        ...,
        example="Vibrant summer-themed banner design",
        max_length=100,
    )
    item_type: ProductType = Field(
        ...,
        example="banner",
        enum=ProductType,
    )
    price: float = Field(
        ...,
        example=49.99,
        gt=0,
    )
    preview_url: str = Field(
        ...,
        example="https://storage.example.com/previews/summer-banner.jpg",
    )
    rating: float = Field(
        ...,
        example=4.5,
        ge=0,
        le=5,
    )
    designer_id: UUID = Field(
        ...,
        example="b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                "title": "Summer Sale Banner",
                "description": "Vibrant summer-themed banner design",
                "item_type": "banner",
                "price": 49.99,
                "preview_url": "https://storage.example.com/previews/summer-banner.jpg",
                "rating": 4.5,
                "designer_id": "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9"
            }
        },
        from_attributes = True,
    )

class MarketFilters(BaseModel):
    item_type: Optional[ProductType] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, gt=0)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    search: Optional[str] = None


class CartItem(BaseModel):
    item_id: UUID
    quantity: int = Field(1, gt=0)


class CartItemAdd(BaseModel):
    """Модель для добавления товара в корзину.

    Attributes:
        item_id (UUID): Идентификатор товара
        quantity (int): Количество (по умолчанию 1)
        specs (Optional[dict]): Дополнительные спецификации
    """
    item_id: UUID = Field(
        ...,
        description="ID товара из маркетплейса",
        example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
    )
    quantity: int = Field(
        1,
        gt=0,
        le=10,
        description="Количество товара (макс. 10)",
        example=1
    )
    specs: Optional[dict] = Field(
        None,
        description="Дополнительные параметры товара",
        example={"size": "A4", "material": "glossy"}
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "item_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                "quantity": 2,
                "specs": {"size": "A3"}
            }
        }
    )

class DirectOrderResponse(BaseModel):
    """Модель ответа при создании прямого заказа.

    Attributes:
        order_id (UUID): Идентификатор созданного заказа
        payment_id (UUID): Идентификатор платежа
        status (str): Статус заказа
        payment_url (str): URL для оплаты
    """
    order_id: UUID = Field(
        ...,
        description="ID созданного заказа",
        example="b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9"
    )
    payment_id: UUID = Field(
        ...,
        description="ID платежа в платежной системе",
        example="c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0"
    )
    status: str = Field(
        ...,
        description="Статус заказа",
        example="created",
        enum=["created", "paid", "processing"]
    )
    payment_url: str = Field(
        ...,
        description="URL для перенаправления на оплату",
        example="https://payment.example.com/checkout/123"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "order_id": "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
                "payment_id": "c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0",
                "status": "created",
                "payment_url": "https://payment.example.com/checkout/123"
            }
        }
    )
