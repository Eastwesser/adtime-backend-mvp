from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base import BaseRepository
from ..models import Factory


class FactoryRepository(BaseRepository[Factory]):
    """
    Репозиторий для работы с фабриками производства.

    Основная функциональность:
    - Поиск фабрик по специализации
    - Управление загрузкой фабрик (increment/decrement_load)
    - Подбор оптимальной фабрики для заказа

    Бизнес-логика:
    1. При подборе фабрики учитывает:
       - Специализацию (product_type)
       - Текущую загрузку (current_load / production_capacity)
       - Рейтинг фабрики

    2. Автоматически обновляет счетчики загрузки при назначении/отмене заказов

    Используется в:
    - ProductionService для распределения заказов
    - OrderService при назначении на производство
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Factory, session)

    async def find_available(self, specialization: Optional[str] = None) -> Optional[Factory]:
        """
        Находит доступную фабрику по специализации.

        Args:
            specialization: Опциональный тип специализации для фильтрации

        Returns:
            Optional[Factory]: Первая подходящая фабрика или None
        """
        query = select(Factory).where(Factory.production_capacity > 0)

        if specialization:
            query = query.where(Factory.specialization.ilike(f"%{specialization}%"))

        query = query.order_by(Factory.rating.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_specialization(
            self,
            product_type: str,
            limit: int = 5
    ) -> Sequence[Factory]:
        """
        Находит фабрики по специализации (типу продукции).

        Args:
            product_type: Тип продукта (например, "banner", "standee")

        Returns:
            Optional[Factory]: Фабрика с подходящей специализацией или None
        """
        stmt = (
            select(Factory)
            .where(Factory.specialization.ilike(f"%{product_type}%"))
            .order_by(
                (Factory.current_load / Factory.production_capacity).asc(),
                Factory.rating.desc()
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_specialization(self, product_type: str) -> Optional[Factory]:
        """Находит фабрику по типу продукта"""
        stmt = select(Factory).where(
            Factory.specialization.ilike(f"%{product_type}%")
        ).limit(1)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_load(self, factory_id: UUID) -> None:
        """Увеличивает текущую загрузку фабрики"""
        await self.session.execute(
            update(Factory)
            .where(Factory.id == factory_id)
            .values(current_load=Factory.current_load + 1)
        )
        await self.session.commit()

    async def decrement_load(self, factory_id: UUID) -> None:
        """Уменьшает текущую загрузку фабрики"""
        await self.session.execute(
            update(Factory)
            .where(Factory.id == factory_id)
            .values(current_load=Factory.current_load - 1)
        )
        await self.session.commit()
