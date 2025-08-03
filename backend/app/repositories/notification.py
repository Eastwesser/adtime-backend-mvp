from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.notifications import Notification
from .base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """
    Репозиторий для работы с уведомлениями пользователей.

    Основная функциональность:
    - Отправка уведомлений
    - Пометка прочитанных
    - Получение списка уведомлений

    Статусы уведомлений:
    - unread - непрочитанное (по умолчанию)
    - read - прочитанное

    Особенности:
    - Оптимизированные запросы для массовых операций
    - Поддержка фильтрации по статусу
    - Автоматическое проставление read_at при пометке прочитанным

    Используется в:
    - NotificationService для основного workflow
    - WebSocket обработчиках для real-time уведомлений
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.status == "unread"
            )
        )
        return result.scalar()

    async def mark_all_as_read(self, user_id: UUID) -> int:
        result = await self.session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.status == "unread"
            )
            .values(status="read", read_at=datetime.now())
            .returning(Notification.id)
        )
        await self.session.commit()
        return len(result.scalars().all())

    async def get_user_notifications(
            self,
            user_id: UUID,
            unread_only: bool = False,
            limit: int = 100
    ) -> Sequence[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )

        if unread_only:
            query = query.where(Notification.status == "unread")

        result = await self.session.execute(query)
        return result.scalars().all()
