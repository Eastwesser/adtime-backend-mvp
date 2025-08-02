from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.generation import Generation
from .base import BaseRepository


class GenerationRepository(BaseRepository[Generation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Generation, session)

    async def get_by_user(
            self,
            session: AsyncSession,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[Generation]:
        result = await session.execute(
            select(Generation)
            .where(Generation.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
            self,
            session: AsyncSession,
            status: str
    ) -> List[Generation]:
        result = await session.execute(
            select(Generation).where(Generation.status == status)
        )
        return result.scalars().all()
