from datetime import datetime
from typing import Optional, Sequence, List
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.payment import Payment
from .base import BaseRepository
from ..models import Order


class PaymentRepository(BaseRepository[Payment]):
    """
    Репозиторий для работы с платежами.

    Основная функциональность:
    - Создание и отслеживание платежей
    - Обновление статусов (pending, succeeded, refunded)
    - Работа с внешними платежными системами (ЮKassa)

    Особенности:
    - Поддерживает все этапы жизненного цикла платежа
    - Хранит внешние идентификаторы платежей
    - Автоматически проставляет временные метки:
      - created_at - при создании
      - captured_at - при успешной оплате
      - refunded_at - при возврате

    Интеграции:
    - Основной репозиторий для PaymentService
    - Тесно связан с OrderRepository
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_by_order(
            self,
            order_id: UUID,
    ) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(
            self,
            session: AsyncSession,
            external_id: str,
    ) -> Optional[Payment]:
        result = await session.execute(
            select(Payment).where(Payment.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def create(
            self,
            session: AsyncSession,
            payment_data: dict,
    ) -> Payment:
        payment = self.model(**payment_data)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

    async def get_by_id(
            self,
            session: AsyncSession,
            payment_id: UUID,
    ) -> Optional[Payment]:
        result = await session.execute(
            select(self.model).where(self.model.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
            self,
            user_id: UUID,
            limit: int = 100,
    ) -> List[Payment]:
        result = await self.session.execute(
            select(self.model)
            .join(Order)
            .where(Order.user_id == user_id)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        return result.scalars().all()

    async def update_by_external_id(
            self,
            session: AsyncSession,
            external_id: str,
            updates: dict,
    ) -> None:
        await session.execute(
            update(self.model)
            .where(self.model.external_id == external_id)
            .values(**updates)
        )
        await session.commit()

    async def update_status(
            self,
            payment_id: UUID,
            new_status: str,
    ) -> Optional[Payment]:
        """Обновляет статус платежа"""
        updates = {"status": new_status}

        if new_status == "succeeded":
            updates["captured_at"] = datetime.now()
        elif new_status == "refunded":
            updates["refunded_at"] = datetime.now()

        return await self.update(payment_id, updates)

    async def get_last_user_payment(
            self,
            user_id: UUID,
            limit: int = 10,
    ) -> Sequence[Payment]:
        """Получает последние платежи пользователя"""
        result = await self.session.execute(
            select(Payment)
            .join(Order)
            .where(Order.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
