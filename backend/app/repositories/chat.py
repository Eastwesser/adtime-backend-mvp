from typing import List
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.chat import ChatMessage
from .base import BaseRepository


class ChatRepository(BaseRepository[ChatMessage]):
    """
    Репозиторий для работы с сообщениями чата заказов.

    Основная функциональность:
    - Получение истории сообщений по заказу
    - Управление статусом прочтения сообщений
    - Подсчет непрочитанных сообщений

    Особенности:
    - Сообщения всегда сортируются по дате создания (новые внизу)
    - Автоматическая обработка статуса is_read
    - Оптимизированные запросы для работы с чатом

    Используется в:
    - OrderService для общения с клиентом
    - WebSocket обработчиках чата
    """

    def __init__(self, session: AsyncSession):
        super().__init__(ChatMessage, session)

    async def get_by_order(
            self,
            order_id: UUID,
            limit: int = 100
    ) -> List[ChatMessage]:
        """Получает сообщения чата для заказа."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.order_id == order_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unread_count(
            self,
            order_id: UUID,
            user_id: UUID
    ) -> int:
        """Получает количество непрочитанных сообщений."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(
                ChatMessage.order_id == order_id,
                ChatMessage.sender_id != user_id,
                ChatMessage.is_read == False
            )
        )
        return len(result.scalars().all())

    async def mark_all_as_read(
            self,
            order_id: UUID,
            user_id: UUID
    ) -> int:
        """Помечает все сообщения как прочитанные."""
        result = await self.session.execute(
            update(ChatMessage)
            .where(
                ChatMessage.order_id == order_id,
                ChatMessage.sender_id != user_id,
                ChatMessage.is_read == False
            )
            .values(is_read=True)
            .returning(ChatMessage.id)
        )
        await self.session.commit()
        return len(result.scalars().all())
