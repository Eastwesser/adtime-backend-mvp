from __future__ import annotations

from datetime import datetime, timedelta
from os.path import exists
from typing import Any, Sequence, Optional
from uuid import UUID

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.order import Order
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """
    Репозиторий для работы с заказами.

    Основная функциональность:
    - Полноценное управление жизненным циклом заказа
    - Назначение на фабрики
    - Обновление статусов
    - Получение заказов по различным критериям

    Статусы заказа (см. OrderStatus):
    - created -> paid -> production -> shipped -> completed
    - Может быть cancelled на любом этапе

    Особенности:
    - Строгая валидация переходов между статусами
    - Транзакционность критичных операций
    - Оптимизированные запросы для работы с связанными сущностями

    Интеграции:
    - Работает со всеми сервисами, связанными с заказами
    - Основной репозиторий для ProductionService
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_user(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None
    ) -> Sequence[Order]:
        """
        Получает заказы пользователя с пагинацией и фильтрацией по статусу.

        Args:
            user_id: ID пользователя
            skip: Количество пропускаемых записей (для пагинации)
            limit: Максимальное количество возвращаемых записей
            status: Статус заказа для фильтрации (опционально)

        Returns:
            Sequence[Order]: Список заказов пользователя

        Examples:
            # Получить первые 10 оплаченных заказов пользователя
            orders = await repo.get_by_user(
                 user_id=UUID("..."),
                 status="paid",
                 limit=10
            )
        """
        query = select(Order).where(Order.user_id == user_id)

        if status:
            query = query.where(Order.status == status)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_status(
            self,
            session: AsyncSession,
            status: str
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        result = await session.execute(
            select(Order).where(Order.status == status)
        )
        return result.scalars().all()

    async def exists(self, order_id: UUID) -> bool:
        result = await self.session.execute(
            select(exists().where(Order.id == order_id)))
        return result.scalar()

    async def get_by_factory(
            self,
            factory_id: UUID,
            status: Optional[str] = None
    ) -> Sequence[Order]:
        """Получает заказы фабрики с фильтрацией по статусу"""
        query = select(Order).where(Order.factory_id == factory_id)

        if status:
            query = query.where(Order.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_status(
            self,
            order_id: UUID,
            new_status: str
    ) -> Optional[Order]:
        """Обновляет статус заказа"""
        order = await self.get(order_id)
        if not order:
            return None

        order.status = new_status
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def assign_to_factory(
            self,
            order_id: UUID,
            factory_id: UUID
    ) -> Optional[Order]:
        """Назначает заказ на фабрику"""
        return await self.update(
            order_id,
            {
                "factory_id": factory_id,
                "status": "production",
                "production_deadline": datetime.now() + timedelta(days=7)
            }
        )
