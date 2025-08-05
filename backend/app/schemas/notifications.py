from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    """
    Типы системных уведомлений.

    Values:
        SYSTEM: Системное уведомление
        ORDER: Уведомление о заказе
        PAYMENT: Уведомление о платеже
        SUPPORT: Ответ поддержки
    """
    SYSTEM = "system"
    ORDER = "order"
    PAYMENT = "payment"
    SUPPORT = "support"


class NotificationStatus(str, Enum):
    """
    Статусы уведомлений.

    Values:
        UNREAD: Не прочитано
        READ: Прочитано
        ARCHIVED: В архиве
    """
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class NotificationBase(BaseModel):
    """
    Базовая схема уведомления.

    Attributes:
        user_id (UUID): ID пользователя-получателя
        type (NotificationType): Тип уведомления
        title (str): Заголовок уведомления
        message (str): Текст уведомления
        payload (Optional[dict]): Дополнительные данные
    """
    user_id: UUID
    type: NotificationType = NotificationType.SYSTEM
    title: str = Field(..., max_length=100)
    message: str = Field(..., max_length=1000)
    payload: Optional[dict] = None


class NotificationResponse(NotificationBase):
    """
    Схема для ответа с уведомлением.

    Attributes:
        id (UUID): ID уведомления
        status (NotificationStatus): Текущий статус
        created_at (datetime): Дата создания
        read_at (Optional[datetime]): Дата прочтения
    """
    id: UUID
    status: NotificationStatus = NotificationStatus.UNREAD
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes = True
    )
    