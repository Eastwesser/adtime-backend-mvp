from enum import Enum
from uuid import UUID

from sqlalchemy import String, ForeignKey, JSON, Float, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class ProductType(str, Enum):
    BANNER = "banner"
    STANDEE = "standee"
    BILLBOARD = "billboard"
    DIGITAL = "digital"


class MarketItem(Base):
    __tablename__ = "market_items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    item_type: Mapped[ProductType] = mapped_column(SQLEnum(ProductType))
    price: Mapped[float] = mapped_column(Float)
    preview_url: Mapped[str] = mapped_column(String(500))
    specs: Mapped[dict] = mapped_column(JSON)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    designer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    designer: Mapped["User"] = relationship()
    orders: Mapped[list["Order"]] = relationship(back_populates="market_item")


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(200))
    specialization: Mapped[str] = mapped_column(String(100))
    rating: Mapped[float] = mapped_column(Float)
    contact_email: Mapped[str] = mapped_column(String(100))
    production_capacity: Mapped[int] = mapped_column(Integer)

    orders: Mapped[list["Order"]] = relationship(back_populates="factory")
