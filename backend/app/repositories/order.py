from __future__ import annotations

from os.path import exists
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.order import Order
from .base import BaseRepository
from ..core.order_status import OrderStatus as CoreOrderStatus


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

    async def update_status(
            self,
            order_id: UUID,
            new_status: str,
            session: AsyncSession
    ) -> Order:
        """Безопасное обновление статуса заказа"""
        order = await self.get(order_id, session)
        if not CoreOrderStatus.is_valid_transition(order.status, new_status):
            raise ValueError(f"Invalid status transition: {order.status} → {new_status}")

        order.status = new_status
        await session.commit()
        return order

    async def exists(self, order_id: UUID) -> bool:
        result = await self.session.execute(
            select(exists().where(Order.id == order_id))
        return result.scalar()
