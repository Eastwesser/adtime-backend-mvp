from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.marketplace import Factory
from .base import BaseRepository


class FactoryRepository(BaseRepository[Factory]):
    def __init__(self, session: AsyncSession):
        super().__init__(Factory, session)

    async def find_available(self, specialization: Optional[str] = None) -> Optional[Factory]:
        query = select(Factory).where(Factory.production_capacity > 0)
        if specialization:
            query = query.where(Factory.specialization == specialization)

        query = query.order_by(Factory.rating.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
