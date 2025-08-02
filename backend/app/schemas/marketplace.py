from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductType(str, Enum):
    BANNER = "banner"
    STANDEE = "standee"
    BILLBOARD = "billboard"
    DIGITAL = "digital"


class MarketItem(BaseModel):
    id: UUID = Field(..., example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8")
    title: str = Field(..., example="Summer Sale Banner", max_length=100)
    description: str = Field(..., example="Vibrant summer-themed banner design", max_length=1000)
    item_type: ProductType = Field(..., example="banner")
    price: float = Field(..., example=49.99, gt=0)
    preview_url: str = Field(..., example="https://storage.example.com/previews/summer-banner.jpg")
    rating: float = Field(..., example=4.5, ge=0, le=5)
    designer_id: UUID = Field(..., example="b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9")

    class Config:
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
        }

    class Config:
        from_attributes = True


class MarketFilters(BaseModel):
    item_type: Optional[ProductType] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, gt=0)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    search: Optional[str] = None


class CartItem(BaseModel):
    item_id: UUID
    quantity: int = Field(1, gt=0)
