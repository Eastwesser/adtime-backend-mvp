import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Order
from .base import Base


class Review(Base):
    """Модель отзыва о выполненном заказе.

    Атрибуты:
        id: Уникальный идентификатор отзыва
        order_id: ID связанного заказа (1-to-1)
        rating: Оценка от 1 до 5 звезд
        comment: Текстовый комментарий (опционально)
        created_at: Дата создания отзыва

    Связи:
        order: Связанный заказ
    """
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), unique=True)

    # 1-5 звезд, обязательное поле
    rating: Mapped[int] = mapped_column(Integer, doc="Оценка от 1 до 5 звезд")
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )
    # Опциональный текстовый комментарий
    comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Текстовый отзыв клиента"
    )

    # Автоматически устанавливается при создании
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        doc="Дата и время создания отзыва"
    )

    # Связь с заказом (каскадное удаление не нужно)
    order: Mapped["Order"] = relationship(back_populates="review")
