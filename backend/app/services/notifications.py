from datetime import datetime
from typing import Optional
from uuid import UUID

from app.repositories.notification import NotificationRepository
from app.schemas.notifications import (
    NotificationType,
    NotificationResponse
)


class NotificationService:
    """
    Сервис для работы с уведомлениями пользователей.
    Обеспечивает:
    - Отправку уведомлений
    - Пометку прочитанных
    - Получение списка уведомлений
    """

    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def send(
            self,
            user_id: UUID,
            title: str,
            message: str,
            notification_type: NotificationType = "system",
            payload: Optional[dict] = None
    ) -> NotificationResponse:
        """Отправляет уведомление пользователю."""
        notification_data = {
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "payload": payload or {}
        }

        notification = await self.repository.create(notification_data)
        return NotificationResponse.from_orm(notification)

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Помечает уведомление как прочитанное."""
        notification = await self.repository.get(notification_id)
        if not notification or notification.user_id != user_id:
            return False

        await self.repository.update(
            notification_id,
            {
                "status": "read",
                "read_at": datetime.now()
            }
        )
        return True

    async def get_user_notifications(
            self,
            user_id: UUID,
            unread_only: bool = False,
            limit: int = 100
    ) -> list[NotificationResponse]:
        """Получает уведомления пользователя."""
        filters = {"user_id": user_id}
        if unread_only:
            filters["status"] = "unread"

        notifications = await self.repository.list(
            filters=filters,
            limit=limit
        )
        return [NotificationResponse.from_orm(n) for n in notifications]
