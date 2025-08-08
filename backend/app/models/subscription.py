"""
Модель подписки пользователя.

Содержит:
- Типы подписок
- Лимиты генераций
- Срок действия подписки
"""
from __future__ import annotations 
import uuid
from datetime import datetime, timedelta, timezone

# from app.models.user import User
from sqlalchemy import UUID, String, ForeignKey, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Subscription(Base):
    """Модель подписки пользователя на сервис"""
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            "plan IN ('free', 'pro', 'premium')",
            name="check_subscription_plan"
        ),
        CheckConstraint(
            "NOT (plan = 'free' AND remaining_generations > 5)",
            name="check_free_plan_limits"
        ),
    )

    # Основные поля подписки
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True
    )
    plan: Mapped[str] = mapped_column(String(50), default="free")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )
    remaining_generations: Mapped[int] = mapped_column(Integer, default=5)

    # Связи
    user: Mapped["User"] = relationship(back_populates="subscription", cascade="all, delete-orphan")
