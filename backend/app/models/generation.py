import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, UUID as SQLUUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Order
from backend.app.models.base import Base
from backend.app.models.user import User


class Generation(Base):
    """Main generation model"""
    __tablename__ = "generations"

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="generations")
    order: Mapped[Optional["Order"]] = relationship(back_populates="generation")


# Add this alias for backward compatibility
GenerationTask = Generation
