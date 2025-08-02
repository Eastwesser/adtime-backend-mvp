from typing import Optional
from uuid import UUID

from backend.app.models.subscription import Subscription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_by_user(
            self,
            session: AsyncSession,
            user_id: UUID
    ) -> Optional[Subscription]:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def decrement_quota(self, user_id):
        pass
