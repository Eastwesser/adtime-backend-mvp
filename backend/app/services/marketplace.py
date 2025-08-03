from __future__ import annotations

from typing import List, Any, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Row, RowMapping

from backend.app.core.storage import S3Storage
from backend.app.repositories.marketplace import MarketplaceRepository
from backend.app.repositories.user import UserRepository
from backend.app.schemas.marketplace import MarketItem, MarketFilters


class MarketplaceService:
    """
    Сервис для работы с маркетплейсом дизайнов.
    Включает:
    - Поиск и фильтрацию товаров
    - Работу с корзиной
    - Создание заказов из товаров
    """
    def __init__(self, repo: MarketplaceRepository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo
        self.storage = S3Storage()

    async def get_items(self, filters: MarketFilters) -> Sequence[Row[Any] | RowMapping | Any]:
        return await self.repo.get_filtered_items(
            item_type=filters.item_type,
            min_price=filters.min_price,
            max_price=filters.max_price,
            rating=filters.min_rating,
            search=filters.search
        )

    async def add_to_cart(self, user_id: UUID, item_id: UUID, quantity: int):
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(404, "Item not found")

        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        return await self.repo.add_to_user_cart(user_id, item_id, quantity)

    async def create_order_from_item(self, user_id: UUID, item_id: UUID):
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(404, "Item not found")

        return await self.repo.create_order(
            user_id=user_id,
            item_id=item_id,
            amount=item.price,
            specs=item.specs
        )

    async def get_item_details(self, item_id: UUID) -> MarketItem:
        """Получение полной информации о товаре включая отзывы и рейтинг

        Args:
            item_id: UUID товара

        Returns:
            MarketItem: Полная информация о товаре

        Raises:
            HTTPException: Если товар не найден
        """
        item = await self.repo.get_item_with_details(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Получаем отзывы
        reviews = await self.repo.get_item_reviews(item_id)

        # Рассчитываем средний рейтинг
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

        return MarketItem(
            **item.dict(),
            reviews=reviews,
            average_rating=round(avg_rating, 1),
            review_count=len(reviews)
        )

    async def remove_from_cart(self, user_id: UUID, item_id: UUID) -> None:
        """Удаление товара из корзины пользователя

        Args:
            user_id: UUID пользователя
            item_id: UUID товара

        Raises:
            HTTPException: Если товар не найден в корзине
        """
        cart_item = await self.repo.get_cart_item(user_id, item_id)
        if not cart_item:
            raise HTTPException(
                status_code=404,
                detail="Item not found in cart"
            )

        await self.repo.remove_from_cart(user_id, item_id)
