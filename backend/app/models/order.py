from __future__ import annotations 
import uuid
from datetime import datetime
from typing import Optional, Dict, List

from app.core.order_status import OrderStatus
from sqlalchemy import UUID, String, ForeignKey, JSON, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class Order(Base):
    """Основная модель заказа в базе данных (использует строки для статусов)."""
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
        String(50),
        default=OrderStatus.CREATED,
        doc="Статус заказа. Допустимые значения: created, paid, production, shipped, completed, cancelled"
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    production_deadline: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="orders")
    generation: Mapped[Optional["GenerationTask"]] = relationship(back_populates="order")
    payment: Mapped["Payment"] = relationship(back_populates="order")

    # Производственные данные
    factory_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("factories.id"), nullable=True)
    market_item_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("market_items.id"), nullable=True)

    # Сообщения в чате
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    # Связи с производством
    factory: Mapped[Optional["Factory"]] = relationship(back_populates="orders")
    market_item: Mapped[Optional["MarketItem"]] = relationship(back_populates="orders")
    review: Mapped[Optional["Review"]] = relationship(back_populates="order")

    __table_args__ = (
        CheckConstraint(
            "status IN ('created', 'paid', 'production', 'shipped', 'completed', 'cancelled')",
            name="check_valid_order_status"
        ),
        # Removed ALL JSON constraints
    )
    