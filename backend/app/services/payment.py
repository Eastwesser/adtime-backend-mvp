# Заглушка для Yookassa (ЮKassa интеграция)
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration
from yookassa import Payment as YooPayment

from backend.app.core.config import settings
from backend.app.repositories.payment import PaymentRepository
from backend.app.schemas.payment import PaymentResponse


class PaymentService:
    """
    Сервис для работы с платежами через ЮKassa.
    Функционал:
    - Создание платежей
    - Обработка вебхуков
    - Проверка статусов
    """

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

    async def cancel_payment(self, payment_id: UUID) -> bool:
        """Отмена платежа в ЮKassa

        Args:
            payment_id: UUID платежа в нашей системе

        Returns:
            bool: True если отмена успешна

        Raises:
            HTTPException: Если платеж не найден или уже завершен
        """
        # Получаем платеж из БД
        payment = await self.repository.get(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status in ["succeeded", "canceled"]:
            return False

        # Отменяем платеж в ЮKassa
        yoo_payment = YooPayment.cancel(payment.external_id)

        # Обновляем статус в БД
        await self.repository.update(
            payment_id,
            {"status": yoo_payment.status}
        )
        return True

    async def get_payment_history(
            self,
            user_id: UUID,
            limit: int = 100
    ) -> List[PaymentResponse]:
        """Получение истории платежей пользователя

        Args:
            user_id: UUID пользователя
            limit: Максимальное количество записей

        Returns:
            List[PaymentResponse]: Список платежей пользователя
        """
        payments = await self.repository.get_by_user(user_id, limit=limit)
        return [PaymentResponse.model_validate(p) for p in payments]

    @staticmethod
    def verify_signature(notification: dict) -> bool:
        # Implement your signature verification logic
        return True

    async def refund_payment(self, id):
        pass
