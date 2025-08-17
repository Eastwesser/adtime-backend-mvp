"""
Модели для маркетплейса:
- Factory: производственные предприятия
"""
from __future__ import annotations 
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Factory(Base):
    current_load = None

    def __init__(self, **kw: Any):
        super().__init__()
        self.api_url = None

    """Модель производственного предприятия"""
    __tablename__ = "factories"

    # Основные данные фабрики
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(200))
    specialization: Mapped[str] = mapped_column(String(100))
    rating: Mapped[float] = mapped_column(Float)
    contact_email: Mapped[str] = mapped_column(String(100))
    production_capacity: Mapped[int] = mapped_column(Integer, default=10)
    api_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_load: Mapped[int] = mapped_column(Integer, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7)  # Default production time
    api_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # For factory API integration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    service_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-3 priority scale
    
    # Связи - используем ТОЛЬКО строковую ссылку
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="factory",
        lazy="dynamic"
    )
