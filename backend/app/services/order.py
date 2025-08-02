# Логика заказов
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.order import Order
from backend.app.repositories.generation import GenerationRepository
from backend.app.repositories.order import OrderRepository
from backend.app.schemas.order import OrderCreate, OrderResponse
from backend.app.services.payment import PaymentService


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
