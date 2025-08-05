"""
Модель платежа через ЮKassa.

Содержит:
- Данные платежа
- Статусы оплаты
- Связь с заказом
"""
from __future__ import annotations 
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, String, Enum, ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Payment(Base):
    """Модель платежа через платежную систему ЮKassa"""
    __tablename__ = "payments"

    # Основные поля платежа
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # ID в ЮKassa
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "succeeded", "canceled", name="payment_status"),
        default="pending"
    )
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payment_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Доп. данные платежа
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Связи
    order: Mapped["Order"] = relationship(back_populates="payment")
