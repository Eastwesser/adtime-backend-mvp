"""
Модели для маркетплейса:
- ProductType: типы продуктов (enum)
- MarketItem: товары на маркетплейсе
- Factory: производственные предприятия
"""
from __future__ import annotations 
from uuid import UUID

# from app.models.order import Order
# from app.models.user import User
from sqlalchemy import String, ForeignKey, JSON, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# class ProductType(Base):
#     """Типы продуктов для маркетплейса"""
#     BANNER = "banner"  # Баннеры
#     STANDEE = "standee"  # Стенды
#     BILLBOARD = "billboard"  # Билборды
#     DIGITAL = "digital"  # Цифровые продукты


class MarketItem(Base):
    """Модель товара на маркетплейсе"""
    __tablename__ = "market_items"
    __table_args__ = (
        CheckConstraint(
            "item_type IN ('BANNER', 'STANDEE', 'BILLBOARD', 'DIGITAL')",
            name="check_product_type"
        ),
    )

    # Основные характеристики товара
    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    item_type: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Float)
    preview_url: Mapped[str] = mapped_column(String(500))
    specs: Mapped[dict] = mapped_column(JSON)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    designer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Связи
    designer: Mapped["User"] = relationship()
    orders: Mapped[list["Order"]] = relationship(back_populates="market_item")
