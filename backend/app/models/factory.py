"""
Модели для маркетплейса:
- Factory: производственные предприятия
"""
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.order import Order
from backend.app.models.base import Base

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
    production_capacity: Mapped[int] = mapped_column(Integer)
    api_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Связи
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="factory",
        lazy="dynamic"
    )
