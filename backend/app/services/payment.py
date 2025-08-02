# Заглушка для Yookassa (ЮKassa интеграция)
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration
from yookassa import Payment as YooPayment

from backend.app.core.config import settings
from backend.app.repositories.payment import PaymentRepository
from backend.app.schemas.payment import PaymentResponse


class PaymentService:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository
        Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)

    @staticmethod
    def configure():
        YooPayment.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)

    async def handle_webhook(self, notification: dict):
        if not self.verify_signature(notification):
            raise HTTPException(status_code=401)

    async def create_payment(
            self,
            session: AsyncSession,
            order_id: UUID,
            amount: float,
            description: str = ""
    ) -> Optional[PaymentResponse]:
        payment = YooPayment.create({
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": settings.YOOKASSA_RETURN_URL},
            "metadata": {"order_id": str(order_id), "description": description}
        })

        db_payment = await self.repository.create(
            session,
            {
                "order_id": order_id,
                "external_id": payment.id,
                "amount": amount,
                "status": payment.status,
                "description": description
            }
        )
        return PaymentResponse.model_validate(db_payment)

    async def check_payment_status(
            self,
            session: AsyncSession,
            payment_id: UUID
    ) -> Optional[PaymentResponse]:
        payment = await self.repository.get_by_id(session, payment_id)
        if payment:
            return PaymentResponse.model_validate(payment)
        return None

    async def handle_webhook(
            self,
            session: AsyncSession,
            notification: dict
    ):
        if not self.verify_signature(notification):
            raise HTTPException(status_code=401)
        # Add webhook processing logic here
        return {"status": "processed"}

    @staticmethod
    def verify_signature(notification: dict) -> bool:
        # Implement your signature verification logic
        return True
