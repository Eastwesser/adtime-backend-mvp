# backend/app/models/user.py
import uuid
from typing import List, Optional

from sqlalchemy import UUID, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Order, Subscription
from backend.app.models.base import Base
from backend.app.models.generation import GenerationTask


class User(Base):
    """Модель пользователя с ролями и подпиской"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "designer", "admin", name="user_roles"),
        default="user"
    )
    telegram_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )

    # Связи
    generations: Mapped[List["GenerationTask"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    subscription: Mapped["Subscription"] = relationship(back_populates="user")
