"""
Модель пользователя системы.

Содержит:
- Основные данные пользователя
- Роли (user, designer, admin)
- Связи с другими моделями
"""
from __future__ import annotations
import uuid
from typing import List, Optional

from sqlalchemy import UUID, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class User(Base):
    """Модель пользователя системы с ролями и подпиской"""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'designer', 'admin')",
            name="check_user_role"
        ),
    )

    # Основные данные пользователя
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    telegram_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Связи с другими моделями (используем строковые ссылки)
    generation_tasks: Mapped[List["GenerationTask"]] = relationship(
        "GenerationTask", 
        back_populates="user"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    subscription: Mapped["Subscription"] = relationship(
        "Subscription", 
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()"
    )
    