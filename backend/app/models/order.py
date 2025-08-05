"""
Модель заказа на производство.

Содержит:
- Основные данные заказа
- Связи с пользователем, генерацией, оплатой и производством
- Статусы заказа
"""
from __future__ import annotations 

import uuid
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import UUID, Enum, ForeignKey, JSON, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from ..core.order_status import OrderStatus as CoreOrderStatus


class Order(Base):
    """Основная модель заказа в базе данных.

    Соответствует таблице 'orders' и содержит:
    - Все основные поля заказа
    - Связи с другими моделями через ForeignKey
    - SQLAlchemy Enum для статусов (должен дублировать значения из OrderStatus)

    Атрибуты:
        id: Уникальный идентификатор заказа
        user_id: ID пользователя, создавшего заказ
        generation_id: ID связанной генерации (если есть)
        status: Текущий статус заказа из OrderStatus
        amount: Общая сумма заказа в рублях
        design_specs: Техническое задание в формате JSON
        production_deadline: Крайний срок производства
        production_errors: Ошибки при производстве

    Связи:
        user: Пользователь, создавший заказ
        generation: Связанная генерация изображения
        payment: Данные об оплате
        factory: Производственное предприятие
        market_item: Товар из маркетплейса (если заказ на готовый товар)
        messages: История сообщений в чате заказа
        review: Отзыв о выполненном заказе
    """
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
        Enum(*[s.value for s in CoreOrderStatus], name="order_status"),
        default=CoreOrderStatus.CREATED.value,
        doc=f"Статус заказа. Допустимые значения: {list(CoreOrderStatus)}"
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

    # Сообщения в чате
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    # Связи с производством
    factory: Mapped[Optional["Factory"]] = relationship(
        back_populates="orders"
    )
    market_item: Mapped[Optional["MarketItem"]] = relationship(back_populates="orders")
    review: Mapped[Optional["Review"]] = relationship(back_populates="order")
    __table_args__ = (
        CheckConstraint(
            "jsonb_typeof(design_specs) = 'object'",
            name="check_design_specs_is_object"
        ),
        CheckConstraint(
            "design_specs ?& array['size', 'material']",
            name="check_required_specs_fields"
        )
    )


class OrderStatus(str, Enum):
    """Статусы заказов в системе."""
    CREATED = "created"
    PAID = "paid"
    PRODUCTION = "production"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
