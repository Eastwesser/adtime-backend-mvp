"""
Модель генерации изображений.

Содержит:
- Основные параметры генерации (prompt, model_version и т.д.)
- Связи с пользователем и заказом
- Статусы выполнения генерации
"""
from __future__ import annotations 
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, UUID as SQLUUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Generation(Base):
    def __init__(self):
        super().__init__()
        self.external_task_id = None

    """Модель задачи генерации изображения"""
    __tablename__ = "generations"

    # Основные поля
    id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id")
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )
    prompt: Mapped[str] = mapped_column(String(1000))
    enhanced_prompt: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    model_version: Mapped[str] = mapped_column(
        String(50),
        default="kandinsky-2.1"
    )
    result_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    external_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="generations")
    order: Mapped[Optional["Order"]] = relationship(back_populates="generation")


# Псевдоним для обратной совместимости
GenerationTask = Generation
