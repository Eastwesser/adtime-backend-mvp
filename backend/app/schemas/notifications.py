from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

NotificationTypeValues = Literal["system", "order", "payment", "support"]
NotificationStatusValues = Literal["unread", "read", "archived"]

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
    type: NotificationTypeValues = "system"
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
    status: NotificationStatusValues = "unread"
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    

NotificationType = NotificationTypeValues
NotificationStatus = NotificationStatusValues    