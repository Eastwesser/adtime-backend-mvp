from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.core.order_status import OrderStatus  # Add this import at the top
ProductTypeValues = Literal["banner", "standee", "billboard", "digital"]

class MarketItem(BaseModel):
    """Marketplace item model"""
    id: UUID = Field(..., example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8")
    title: str = Field(..., max_length=100, example="Summer Sale Banner")
    description: str = Field(..., max_length=1000)
    item_type: ProductTypeValues = Field(..., example="banner")
    price: float = Field(..., gt=0, example=49.99)
    preview_url: str = Field(...)
    rating: float = Field(..., ge=0, le=5, example=4.5)
    designer_id: UUID = Field(...)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                "title": "Summer Sale Banner",
                "description": "Vibrant summer-themed banner design",
                "item_type": "banner",
                "price": 49.99,
                "preview_url": "https://example.com/preview.jpg",
                "rating": 4.5,
                "designer_id": "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9"
            }
        }
    )

class MarketFilters(BaseModel):
    """Marketplace filters"""
    item_type: Optional[ProductTypeValues] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, gt=0)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    search: Optional[str] = None

class CartItem(BaseModel):
    """Shopping cart item"""
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
        use_enum_values=True,
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
        example=OrderStatus.CREATED,
        enum=[OrderStatus.CREATED, "paid", "processing"]
    )
    payment_url: str = Field(
        ...,
        description="URL для перенаправления на оплату",
        example="https://payment.example.com/checkout/123"
    )
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra = {
            "example": {
                "order_id": "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
                "payment_id": "c3d4e5f6-g7h8-9012-i3j4-k5l6m7n8o9p0",
                "status": "created",
                "payment_url": "https://payment.example.com/checkout/123"
            }
        }
    )
