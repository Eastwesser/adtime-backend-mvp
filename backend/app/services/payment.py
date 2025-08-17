# Yookassa (ЮKassa интеграция)
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration
from yookassa import Payment as YooPayment

from app.core.monitoring.monitoring import PAYMENT_METRICS
from app.core.order_status import OrderStatus
from app.services.yookassa_adapter import YooKassaAdapter, PaymentError
from app.core.config import settings
from app.core.logger import get_logger
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentResponse

logger = get_logger(__name__)


class PaymentService:
    """
    Сервис для работы с платежами через ЮKassa.
    Функционал:
    - Создание платежей
    - Обработка вебхуков
    - Проверка статусов
    - Fiscalisation receipt
    """

    def __init__(self, repository: PaymentRepository):
        self.repository = repository
        self.yookassa = YooKassaAdapter(
            shop_id=settings.YOOKASSA_SHOP_ID,
            secret_key=settings.YOOKASSA_SECRET_KEY
        )

    async def create_payment(
            self,
            session: AsyncSession,
            order_id: UUID,
            amount: int,
            description: str = ""
    ) -> PaymentResponse:
        """Создание платежа с полной валидацией"""
        if amount <= 0:
            raise HTTPException(400, "Amount must be positive")
        if amount > 1_000_000:  # Лимит 1 млн руб
            raise HTTPException(400, "Amount exceeds maximum limit")

        PAYMENT_METRICS['amounts'].observe(amount)

        try:
            payment = await self.yookassa.create_payment(
                amount=amount,
                order_id=str(order_id),
                description=description,
                return_url=settings.YOOKASSA_RETURN_URL
            )

            db_payment = await self.repository.create(
                session,
                {
                    "order_id": order_id,
                    "external_id": payment.id,
                    "amount": float(payment.amount.value),
                    "status": payment.status,
                    "description": description
                }
            )

            logger.info(f"Created payment {payment.id} for order {order_id}")
            return PaymentResponse.model_validate(db_payment)

        except PaymentError as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise HTTPException(500, "Payment processing failed")

    async def find_payment(self, payment_id: str) -> Optional[dict]:
        """Поиск платежа в ЮKassa"""
        try:
            return await self.yookassa.get_payment(payment_id)
        except Exception as e:
            PAYMENT_METRICS['errors'].labels(type="lookup_error").inc()
            logger.error(f"Payment lookup failed: {str(e)}")
            return None

    async def process_webhook(
            self,
            session: AsyncSession,
            payload: dict,
            ipn_signature: str
    ) -> bool:
        """Обработка вебхука с проверкой подписи"""
        payment_data = self.yookassa.parse_webhook(payload, ipn_signature)
        if not payment_data:
            raise HTTPException(401, "Invalid signature")

        if payload.get('event') == 'payment.succeeded':
            await self._process_successful_payment(session, payment_data)
            return True

        logger.info(f"Received webhook: {payload.get('event')}")
        return False

    async def _process_successful_payment(
            self,
            session: AsyncSession,
            payment: dict
    ) -> None:
        """Обработка успешного платежа"""
        try:
            await self.repository.update_by_external_id(
                session,
                payment.id,
                {
                    "status": payment.status,
                    "captured_at": datetime.now()
                }
            )
            logger.info(f"Payment {payment.id} processed successfully")
        except Exception as e:
            logger.error(f"Failed to process payment: {str(e)}")
            raise

    async def confirm_payment(self, payment_id: UUID):
        payment = await self.repository.get(payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")

        try:
            OrderStatus.validate_transition(payment.order.status, OrderStatus.PAID)
            await self._process_payment(payment_id)
        except ValueError as e:
            await self._cancel_payment(payment_id)
            raise HTTPException(400, str(e))

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
        """Отмена платежа с проверкой статуса"""
        payment = await self.repository.get(payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")

        if payment.status not in [OrderStatus.PENDING, "waiting_for_capture"]:
            return False

        try:
            yoo_payment = await self.yookassa.cancel_payment(payment.external_id)
            await self.repository.update(
                payment_id,
                {"status": yoo_payment.status}
            )
            PAYMENT_METRICS['status_changes'].labels(status="cancelled").inc()
            return True
        except PaymentError as e:
            PAYMENT_METRICS['errors'].labels(type="lookup_error").inc()
            logger.error(f"Payment cancellation failed: {str(e)}")
            raise HTTPException(500, "Cancellation failed")

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

    async def refund_payment(self, payment_id: UUID) -> bool:
        """Оформление возврата платежа через ЮKassa.

        Args:
            payment_id: UUID платежа в нашей системе

        Returns:
            bool: True если возврат успешно инициирован

        Raises:
            HTTPException: Если платеж не найден или возврат невозможен
        """
        payment = await self.repository.get(payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")

        if payment.status != OrderStatus.SUCCEEDED: 
            raise HTTPException(400, "Only succeeded payments can be refunded")

        try:
            refund = YooPayment.refund.create({
                "payment_id": payment.external_id,
                "amount": {"value": payment.amount, "currency": "RUB"}
            })

            await self.repository.update(
                payment_id,
                {
                    "status": "refunded",
                    "refunded_at": datetime.now(),
                    "refund_id": refund.id
                }
            )
            return True
        except Exception as e:
            logger.error(f"Refund failed: {str(e)}")
            raise HTTPException(500, "Refund processing failed")

    @staticmethod
    def verify_signature(notification: dict) -> bool:
        """Проверка подписи уведомления от ЮKassa.

        Args:
            notification: Данные уведомления

        Returns:
            bool: True если подпись валидна
        """
        try:
            # Получаем подпись из заголовков
            signature = notification.get("signature", "")

            # Формируем строку для проверки
            data = f"{notification['id']}&{notification['event']}&{notification['object']['id']}"

            # Проверяем подпись
            return Configuration.verify_signature(data, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    @staticmethod
    def _verify_signature(payload: dict, signature: str) -> bool:
        """Проверка подписи уведомления"""
        try:
            # Для Python 3.7+ можно использовать Configuration из SDK
            from yookassa.configuration import Configuration
            return Configuration.verify_signature(
                payload,
                signature
            )
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    async def _process_payment(self, payment_id: UUID) -> None:
        """Обработка успешного платежа и подтверждение заказа"""
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")

        try:
            # Подтверждаем платеж в ЮKassa
            yoo_payment = YooPayment.capture(payment.external_id)

            # Обновляем статус платежа в БД
            await self.repository.update(
                payment_id,
                {
                    "status": yoo_payment.status,
                    
                    "captured_at": datetime.now()
                }
            )
            logger.info(f"Payment {payment_id} processed successfully")
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise HTTPException(500, "Payment processing failed")

    async def _cancel_payment(self, payment_id: UUID) -> None:
        """Отмена платежа с полным возвратом"""
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")

        try:
            # Отменяем платеж в ЮKassa
            yoo_payment = YooPayment.cancel(payment.external_id)

            # Обновляем статус в БД
            await self.repository.update(
                payment_id,
                {
                    "status": yoo_payment.status,
                    "cancelled_at": datetime.now()
                }
            )
            logger.info(f"Payment {payment_id} cancelled successfully")
        except Exception as e:
            logger.error(f"Payment cancellation failed: {str(e)}")
            raise HTTPException(500, "Payment cancellation failed")
