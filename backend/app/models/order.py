"""
Модель заказа на производство (updated to use strings instead of enums)
"""
from __future__ import annotations 

import uuid
from datetime import datetime
from typing import Optional, Dict, List

from app.models.chat import ChatMessage
from app.models.factory import Factory
from app.models.generation import GenerationTask
from app.models.marketplace import MarketItem
from app.models.payment import Payment
from app.models.review import Review
from app.models.user import User
from sqlalchemy import UUID, String, ForeignKey, JSON, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
        String(50),  # Increased length for potential future statuses
        default="created",
        doc="Статус заказа. Допустимые значения: created, paid, production, shipped, completed, cancelled"
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    design_specs: Mapped[Dict] = mapped_column(JSON, nullable=False)
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
        CheckConstraint(
            "jsonb_typeof(design_specs) = 'object'",
            name="check_design_specs_is_object"
        ),
        CheckConstraint(
            "design_specs ?& array['size', 'material']",
            name="check_required_specs_fields"
        )
    )
    