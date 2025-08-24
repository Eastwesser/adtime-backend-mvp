"""
Модель пользователя системы.

Содержит:
- Основные данные пользователя
- Роли (user, designer, admin)
- Связи с другими моделями
"""
from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import List, Optional

from app.models.generation import Generation as GenerationTask

from sqlalchemy import UUID, DateTime, String, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class User(Base):
    """Модель пользователя системы с ролями и подпиской"""
    __tablename__ = "users"
    
    # Role constants
    ROLE_USER = "user"
    ROLE_DESIGNER = "designer"
    ROLE_ADMIN = "admin"

    __table_args__ = (
        CheckConstraint(
            f"role IN ('{ROLE_USER}', '{ROLE_DESIGNER}', '{ROLE_ADMIN}')",
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
    role: Mapped[str] = mapped_column(String(50), default=ROLE_USER)
    telegram_id: Mapped[Optional[str]] = mapped_column(String(100), unique=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
        server_default=func.now(),  # Database-side default
        nullable=False,
        default=datetime.now(timezone.utc)  # Application-side fallback
    )

    # Связи с другими моделями (используем строковые ссылки)
    generation_tasks: Mapped[List["GenerationTask"]] = relationship(
        back_populates="user",
        lazy="selectin"
    )
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    subscription: Mapped["Subscription"] = relationship(
        back_populates="user",
        uselist=False
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()"
    )
    is_guest: Mapped[bool] = mapped_column(default=False)
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)