# backend/app/services/yookassa_adapter.py
from typing import Optional, Dict, Any
from uuid import uuid4

from yookassa import Configuration, Payment as YooPayment
from yookassa.domain.exceptions import BadRequestError, NotFoundError
from yookassa.domain.notification import WebhookNotification
from yookassa.domain.response import (
    PaymentResponse as YooPaymentResponse,
    RefundResponse as YooRefundResponse
)


class YooKassaAdapter:
    """
    Адаптер для работы с API ЮKassa.
    Инкапсулирует всю логику взаимодействия с платежной системой.
    """

    def __init__(self, shop_id: str, secret_key: str):
        Configuration.configure(shop_id, secret_key)

    async def create_payment(
            self,
            amount: float,
            order_id: str,
            description: str = "",
            return_url: str = None,
            metadata: Dict[str, Any] = None
    ) -> YooPaymentResponse:
        """
        Создание платежа в ЮKassa.

        Args:
            amount: Сумма платежа
            order_id: Идентификатор заказа
            description: Описание платежа
            return_url: URL для возврата после оплаты
            metadata: Дополнительные метаданные

        Returns:
            Объект платежа от ЮKassa
        """
        params = {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": metadata or {"order_id": order_id}
        }

        try:
            return YooPayment.create(params, str(uuid4()))
        except BadRequestError as e:
            raise PaymentError(f"Invalid payment request: {str(e)}")

    async def capture_payment(self, payment_id: str) -> YooPaymentResponse:
        """
        Подтверждение платежа (списание средств).

        Args:
            payment_id: Идентификатор платежа в ЮKassa

        Returns:
            Объект подтвержденного платежа
        """
        try:
            return YooPayment.capture(payment_id)
        except Exception as e:
            raise PaymentError(f"Capture payment failed: {str(e)}")

    async def cancel_payment(self, payment_id: str) -> YooPaymentResponse:
        """
        Отмена платежа.

        Args:
            payment_id: Идентификатор платежа

        Returns:
            Объект отмененного платежа
        """
        try:
            return YooPayment.cancel(payment_id)
        except Exception as e:
            raise PaymentError(f"Cancel payment failed: {str(e)}")

    async def get_payment(self, payment_id: str) -> Optional[YooPaymentResponse]:
        """
        Получение информации о платеже.

        Args:
            payment_id: Идентификатор платежа

        Returns:
            Информация о платеже или None если не найден
        """
        try:
            return YooPayment.find_one(payment_id)
        except NotFoundError:
            return None

    async def create_refund(
            self,
            payment_id: str,
            amount: float,
            reason: str = ""
    ) -> YooRefundResponse:
        """
        Создание возврата платежа.

        Args:
            payment_id: Идентификатор исходного платежа
            amount: Сумма возврата
            reason: Причина возврата

        Returns:
            Объект возврата
        """
        params = {
            "payment_id": payment_id,
            "amount": {"value": amount, "currency": "RUB"},
            "description": reason
        }

        try:
            return YooPayment.refund.create(params, str(uuid4()))
        except BadRequestError as e:
            raise PaymentError(f"Invalid refund request: {str(e)}")

    @staticmethod
    def parse_webhook(payload: dict, ipn_signature: str) -> Optional[dict]:
        """
        Парсинг и валидация вебхука от ЮKassa.

        Args:
            payload: Тело вебхука
            ipn_signature: Подпись уведомления

        Returns:
            Распарсенные данные платежа или None если подпись невалидна
        """
        try:
            if not Configuration.verify_signature(payload, ipn_signature):
                return None
            return WebhookNotification(payload).object
        except Exception:
            return None


class PaymentError(Exception):
    """Базовое исключение для ошибок платежей"""
    pass
