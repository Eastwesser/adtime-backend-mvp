"""Модель сообщений в чате заказа.

Атрибуты:
    id (UUID): Уникальный идентификатор сообщения
    order_id (UUID): ID связанного заказа
    sender_id (UUID): ID отправителя сообщения
    message (str): Текст сообщения
    attachments (List[str]): Список URL вложений (опционально)
    created_at (datetime): Дата и время создания сообщения
    is_read (bool): Флаг прочтения сообщения

Связи:
    order (Order): Связанный заказ (обратная ссылка)
    sender (User): Пользователь-отправитель
"""
from __future__ import annotations 
import uuid
from datetime import datetime
from typing import List, Optional

from app.models.base import Base
from sqlalchemy import Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ChatMessage(Base):
    """Модель сообщений в чате заказа"""
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор сообщения"
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"),
        comment="ID связанного заказа"
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        comment="ID отправителя сообщения"
    )
    message: Mapped[str] = mapped_column(
        Text,
        comment="Текст сообщения"
    )
    attachments: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Список URL вложений (опционально)"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        comment="Дата и время создания сообщения"
    )
    is_read: Mapped[bool] = mapped_column(
        default=False,
        comment="Флаг прочтения сообщения"
    )

    # Связи с другими моделями
    order: Mapped["Order"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()
