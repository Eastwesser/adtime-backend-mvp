# Логика заказов
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.order import Order
from backend.app.repositories.generation import GenerationRepository
from backend.app.repositories.order import OrderRepository
from backend.app.schemas.order import OrderCreate, OrderResponse
from backend.app.services.payment import PaymentService
from ..core.order_status import OrderStatus as CoreOrderStatus


def _calculate_amount(order_in: OrderCreate) -> float:
    # Implement proper pricing logic
    base_price = 1000
    # Add calculations based on design_specs
    return base_price


class OrderService:
    def __init__(
            self,
            session: AsyncSession,
            order_repo: OrderRepository,
            payment_service: PaymentService,
            generation_repo: GenerationRepository = None
    ):
        self.session = session
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.generation_repo = generation_repo

    async def create_order(
            self,
            user_id: UUID,
            order_in: OrderCreate
    ) -> Order:
        order_data = {
            **order_in.model_dump(),
            "user_id": user_id,
            "status": "created",
            "amount": _calculate_amount(order_in)
        }
        return await self.order_repo.create(order_data)

    async def create_order_with_payment(
            self,
            user_id: UUID,
            order_in: OrderCreate
    ) -> dict:
        async with self.session.begin():
            order = await self.create_order(user_id, order_in)
            payment = await self.payment_service.create_payment(
                order_id=order.id,
                amount=order.amount,
                session=self.session,
            )
            return {
                "order": OrderResponse.model_validate(order),
                "payment": payment
            }

    async def update_order_status(
            self,
            order_id: UUID,
            new_status: str,
            user_id: Optional[UUID] = None
    ) -> Order:
        """Безопасное обновление статуса заказа"""
        async with self.session.begin():
            order = await self.order_repo.get(order_id)

            if user_id and order.user_id != user_id:
                raise PermissionError("User can only update own orders")

            return await self.order_repo.update_status(
                order_id,
                new_status,
                self.session
            )

    async def get_user_orders(
            self,
            user_id: UUID,
            status: Optional[str] = None
    ) -> List[Order]:
        """Получение заказов пользователя с фильтром по статусу"""
        query = select(Order).where(Order.user_id == user_id)

        if status:
            if status not in CoreOrderStatus:
                raise ValueError(f"Invalid status: {status}")
            query = query.where(Order.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_order(self, order_id: UUID) -> Order:
        """Получение заказа по ID"""
        order = await self.order_repo.get(order_id)
        if not order:
            raise ValueError("Order not found")
        return order

    async def update_order(
            self,
            order_id: UUID,
            update_data: OrderUpdate,
            user_id: Optional[UUID] = None
    ) -> Order:
        """Обновление данных заказа"""
        async with self.session.begin():
            order = await self.get_order(order_id)

            if user_id and order.user_id != user_id:
                raise PermissionError("User can only update own orders")

            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(order, field, value)

            await self.session.commit()
            return order

    async def delete_order(self, order_id: UUID, user_id: Optional[UUID] = None) -> None:
        """Удаление заказа"""
        async with self.session.begin():
            order = await self.get_order(order_id)

            if user_id and order.user_id != user_id:
                raise PermissionError("User can only delete own orders")

            if order.status not in {CoreOrderStatus.CREATED, CoreOrderStatus.CANCELLED}:
                raise ValueError("Only CREATED or CANCELLED orders can be deleted")

            await self.order_repo.delete(order_id)
