"""
Модель системных уведомлений.

Содержит:
- Основные данные уведомления
- Связи с пользователем
- Статусы уведомлений
"""
import uuid
from datetime import datetime
from typing import Optional, Dict

from sqlalchemy import UUID, Enum, ForeignKey, JSON, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.user import User
from ..schemas.notifications import NotificationType, NotificationStatus


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

    # Основные поля
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор уведомления"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        comment="ID пользователя-получателя"
    )
    type: Mapped[str] = mapped_column(
        Enum(
            NotificationType.SYSTEM,
            NotificationType.ORDER,
            NotificationType.PAYMENT,
            NotificationType.SUPPORT,
            name="notification_type"
        ),
        default=NotificationType.SYSTEM,
        comment=f"Тип уведомления: {', '.join(NotificationType)}"
    )
    status: Mapped[str] = mapped_column(
        Enum(
            NotificationStatus.UNREAD,
            NotificationStatus.READ,
            NotificationStatus.ARCHIVED,
            name="notification_status"
        ),
        default=NotificationStatus.UNREAD,
        comment=f"Статус уведомления: {', '.join(NotificationStatus)}"
    )
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Заголовок уведомления"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст уведомления"
    )
    payload: Mapped[Optional[Dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Дополнительные данные в формате JSON"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        comment="Дата создания уведомления"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата прочтения уведомления"
    )

    # Связи
    user: Mapped["User"] = relationship(back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} ({self.type}) for user {self.user_id}>"