import uuid
from typing import TypeVar, Generic, Optional, List

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, session: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            session: AsyncSession,
            id: uuid.UUID,
            obj_in: dict
    ) -> Optional[ModelType]:
        await session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
        )
        await session.commit()
        return await self.get(session, id)

    async def delete(self, session: AsyncSession, id: uuid.UUID) -> bool:
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await session.commit()
        return result.rowcount > 0

    async def list(
            self,
            session: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[ModelType]:
        result = await session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
