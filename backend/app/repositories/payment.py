from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.payment import Payment
from .base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_by_order(
            self,
            session: AsyncSession,
            order_id: UUID
    ) -> Optional[Payment]:
        result = await session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(
            self,
            session: AsyncSession,
            external_id: str
    ) -> Optional[Payment]:
        result = await session.execute(
            select(Payment).where(Payment.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def create(
            self,
            session: AsyncSession,
            payment_data: dict
    ) -> Payment:
        payment = self.model(**payment_data)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    async def get_by_id(
            self,
            session: AsyncSession,
            payment_id: UUID
    ) -> Optional[Payment]:
        result = await session.execute(
            select(self.model).where(self.model.id == payment_id)
        )
        return result.scalar_one_or_none()
