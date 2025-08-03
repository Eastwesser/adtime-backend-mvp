"""
Модели для маркетплейса:
- ProductType: типы продуктов (enum)
- MarketItem: товары на маркетплейсе
- Factory: производственные предприятия
"""
from enum import Enum
from uuid import UUID

from sqlalchemy import String, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import User, Order
from backend.app.models.base import Base


class ProductType(str, Enum):
    """Типы продуктов для маркетплейса"""
    BANNER = "banner"  # Баннеры
    STANDEE = "standee"  # Стенды
    BILLBOARD = "billboard"  # Билборды
    DIGITAL = "digital"  # Цифровые продукты


class MarketItem(Base):
    """Модель товара на маркетплейсе"""
    __tablename__ = "market_items"

    # Основные характеристики товара
    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    item_type: Mapped[ProductType] = mapped_column(SQLEnum(ProductType))
    price: Mapped[float] = mapped_column(Float)
    preview_url: Mapped[str] = mapped_column(String(500))
    specs: Mapped[dict] = mapped_column(JSON)  # Технические характеристики
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    designer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Связи
    designer: Mapped["User"] = relationship()  # Дизайнер, создавший товар
    orders: Mapped[list["Order"]] = relationship(back_populates="market_item")
