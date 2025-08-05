from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.subscription import Subscription
from .base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """
    Репозиторий для работы с подписками пользователей.

    Основная функциональность:
    - Управление подписками (free, pro, premium)
    - Контроль квот генераций
    - Проверка и обновление статусов подписок

    Тарифные планы:
    - free: 5 генераций
    - pro: 50 генераций
    - premium: 200 генераций

    Особенности:
    - Автоматическое уменьшение квоты при генерации
    - Возврат квоты при отмене генерации
    - Проверка срока действия подписки (expires_at)

    Используется в:
    - GenerationService для контроля квот
    - SubscriptionService для управления подписками
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_by_user(self, user_id: UUID) -> Optional[Subscription]:
        """Получает подписку пользователя по его ID.

        Args:
            user_id: UUID пользователя

        Returns:
            Optional[Subscription]: Объект подписки или None если не найдена
        """
        result = await self.session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def decrement_quota(self, user_id: UUID) -> None:
        """Уменьшает квоту генераций в подписке пользователя.

        Args:
            user_id: UUID пользователя

        Raises:
            ValueError: Если подписка не найдена
        """
        subscription = await self.get_by_user(user_id)
        if not subscription:
            raise ValueError("Subscription not found")

        subscription.remaining_generations -= 1
        await self.session.commit()

    async def increment_quota(self, user_id: UUID) -> None:
        """Увеличивает квоту генераций в подписке пользователя.

        Args:
            user_id: UUID пользователя

        Raises:
            ValueError: Если подписка не найдена
        """
        subscription = await self.get_by_user(user_id)
        if not subscription:
            raise ValueError("Subscription not found")

        subscription.remaining_generations += 1
        await self.session.commit()
