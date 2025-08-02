"""
Модель подписки пользователя.

Содержит:
- Типы подписок
- Лимиты генераций
- Срок действия подписки
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import UUID, Enum, ForeignKey, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.user import User


class Subscription(Base):
    """Модель подписки пользователя на сервис"""
    __tablename__ = "subscriptions"
    __table_args__ = (
        # Ограничение: бесплатная подписка не может иметь >5 генераций
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
        unique=True  # Один пользователь - одна подписка
    )
    plan: Mapped[str] = mapped_column(
        Enum("free", "pro", "premium", name="subscription_plans"),
        default="free"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30)  # По умолчанию 30 дней
    )
    remaining_generations: Mapped[int] = mapped_column(Integer, default=5)  # Остаток генераций

    # Связи
    user: Mapped["User"] = relationship(back_populates="subscription", cascade="all, delete-orphan")
