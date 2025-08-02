from __future__ import annotations

from typing import List, Optional, Any, Sequence
from uuid import UUID

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.marketplace import MarketItem
from .base import BaseRepository


class MarketplaceRepository(BaseRepository[MarketItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(MarketItem, session)

    async def get_filtered_items(
            self,
            item_type: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            rating: Optional[float] = None,
            search: Optional[str] = None
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        query = select(MarketItem)

        if item_type:
            query = query.where(MarketItem.item_type == item_type)
        if min_price:
            query = query.where(MarketItem.price >= min_price)
        if max_price:
            query = query.where(MarketItem.price <= max_price)
        if rating:
            query = query.where(MarketItem.rating >= rating)
        if search:
            query = query.where(MarketItem.title.ilike(f"%{search}%"))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_to_user_cart(self, user_id: UUID, item_id: UUID, quantity: int):
        # Реализация добавления в корзину
        pass

    async def get_item(self, item_id):
        pass

    async def create_order(self, user_id, item_id, amount, specs):
        pass
