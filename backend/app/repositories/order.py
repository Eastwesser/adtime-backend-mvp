from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.order import Order
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_user(
            self,
            session: AsyncSession,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
            self,
            session: AsyncSession,
            status: str
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        result = await session.execute(
            select(Order).where(Order.status == status)
        )
        return result.scalars().all()
