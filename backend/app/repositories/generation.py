import uuid
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.generation import Generation
from .base import BaseRepository
from ..schemas import GenerationResponse


class GenerationRepository(BaseRepository[Generation]):
    """
    Репозиторий для работы с генерациями изображений.

    Основная функциональность:
    - Управление историей генераций пользователя
    - Проверка квот генераций
    - Получение генераций по статусу

    Интеграции:
    - Работает в паре с SubscriptionRepository для контроля квот
    - Связан с KandinskyAPI через GenerationService

    Особенности:
    - Поддерживает пагинацию для больших списков генераций
    - Отдельные методы для работы со статусами (pending, processing, completed)
    - Валидация квот перед созданием новой генерации

    Используется в:
    - GenerationService для основного workflow
    - Admin API для статистики
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Generation, session)
        self.generation_repo = None

    async def get_by_user(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[Generation]:
        """Получает список генераций пользователя с пагинацией.

        Args:
            user_id: UUID пользователя
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            List[Generation]: Список генераций
        """
        result = await self.session.execute(
            select(Generation)
            .where(Generation.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Generation]:
        """Получает генерации по статусу.

        Args:
            status: Статус генерации (pending, processing, completed и т.д.)

        Returns:
            List[Generation]: Список генераций с указанным статусом
        """
        result = await self.session.execute(
            select(Generation).where(Generation.status == status)
        )
        return result.scalars().all()

    async def get_by_user_paginated(
            self,
            user_id: UUID,
            limit: int = 100,
            offset: int = 0
    ) -> List[Generation]:
        """Альтернативный метод получения генераций с пагинацией.

        Args:
            user_id: UUID пользователя
            limit: Лимит записей
            offset: Смещение

        Returns:
            List[Generation]: Список генераций
        """
        return await self.get_by_user(user_id, skip=offset, limit=limit)

    async def check_quota(self, user_id: uuid.UUID) -> bool:
        """Проверяет, есть ли у пользователя квота для генерации."""
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription or subscription.remaining_generations <= 0:
            return False
        return True

    # async def get_user_generations(
    #         self,
    #         user_id: uuid.UUID,
    #         limit: int = 100
    # ) -> List[GenerationResponse]:
    #     """Получает список генераций пользователя."""
    #     generations = await self.generation_repo.get_by_user(user_id, limit=limit)
    #     return [GenerationResponse.model_validate(g) for g in generations]

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        order_by_desc: bool = True
    ) -> List[Generation]:
        """Получает список генераций пользователя с пагинацией."""
        query = select(Generation).where(Generation.user_id == user_id)
        
        if order_by_desc:
            query = query.order_by(Generation.created_at.desc())
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    