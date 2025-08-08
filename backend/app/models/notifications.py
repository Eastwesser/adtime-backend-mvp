"""
Модель системных уведомлений.

Содержит:
- Основные данные уведомления
- Связи с пользователем
- Статусы уведомлений
"""
from __future__ import annotations 
import uuid
from datetime import datetime
from typing import Optional, Dict

# from app.models.user import User
from sqlalchemy import UUID, String, Text, ForeignKey, JSON, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Notification(Base):
    """Модель уведомления в базе данных.

    Соответствует таблице 'notifications' и содержит:
    - Все основные поля уведомления
    - Связи с пользователем через ForeignKey
    - SQLAlchemy Enum для типов и статусов

    Атрибуты:
        id: Уникальный идентификатор уведомления
        user_id: ID пользователя-получателя
        type: Тип уведомления из NotificationType
        status: Текущий статус из NotificationStatus
        title: Заголовок уведомления
        message: Текст уведомления
        payload: Дополнительные данные в JSON
        created_at: Дата создания
        read_at: Дата прочтения

    Связи:
        user: Пользователь, которому адресовано уведомление
    """
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "type IN ('system', 'order', 'payment', 'support')",
            name="check_notification_type"
        ),
        CheckConstraint(
            "status IN ('unread', 'read', 'archived')",
            name="check_notification_status"
        ),
    )


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
    type: Mapped[str] = mapped_column(String(50), default="system")
    status: Mapped[str] = mapped_column(String(50), default="unread")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} ({self.type}) for user {self.user_id}>"
