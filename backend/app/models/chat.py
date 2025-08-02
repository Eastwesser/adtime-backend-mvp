import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Order, User
from .base import Base


class ChatMessage(Base):
    """Модель сообщений в чате заказа"""
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    attachments: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    is_read: Mapped[bool] = mapped_column(default=False)

    # Связи с другими моделями
    order: Mapped["Order"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()
