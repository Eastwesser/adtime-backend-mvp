"""
Модель заказа на производство.

Содержит:
- Основные данные заказа
- Связи с пользователем, генерацией, оплатой и производством
- Статусы заказа
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import UUID, Enum, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Factory, MarketItem
from backend.app.models.base import Base
from backend.app.models.generation import GenerationTask
from backend.app.models.payment import Payment
from backend.app.models.user import User


class Order(Base):
    """Модель заказа на производство рекламного продукта"""
    __tablename__ = "orders"

    # Основные поля
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )
    generation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generations.id"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum("created", "paid", "production", "shipped", "completed", name="order_status"),
        default="created"
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    design_specs: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Техническое задание
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    production_deadline: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    production_errors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="orders")
    generation: Mapped[Optional["GenerationTask"]] = relationship(back_populates="order")
    payment: Mapped["Payment"] = relationship(back_populates="order")

    # Производственные данные
    factory_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("factories.id"), nullable=True)
    market_item_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("market_items.id"), nullable=True)

    # Связи с производством
    factory: Mapped[Optional["Factory"]] = relationship(back_populates="orders")
    market_item: Mapped[Optional["MarketItem"]] = relationship(back_populates="orders")


class OrderStatus:
    """Заглушка для будущей реализации статусов заказа"""
    pass
