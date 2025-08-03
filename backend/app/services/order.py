# Логика заказов
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Any, Sequence
from uuid import UUID

from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.order import Order
from backend.app.repositories.generation import GenerationRepository
from backend.app.repositories.order import OrderRepository
from backend.app.schemas.order import OrderCreate, OrderResponse, ChatMessageSchema, OrderUpdate
from backend.app.services.payment import PaymentService
from ..core.order_status import OrderStatus as CoreOrderStatus


def _calculate_amount(order_in: OrderCreate) -> float:
    # Implement proper pricing logic
    base_price = 1000
    # Add calculations based on design_specs
    return base_price


class OrderService:
    """
    Комплексный сервис управления заказами.
    Обеспечивает:
    - Создание и обработку заказов
    - Интеграцию с платежами
    - Управление статусами
    """

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

    async def add_order_message(
            self,
            order_id: UUID,
            user_id: UUID,
            message: str,
            attachments: List[str] = None
    ) -> ChatMessageSchema:
        """
        Добавляет сообщение в чат заказа.

        Параметры:
            order_id: UUID заказа
            user_id: UUID пользователя-отправителя
            message: Текст сообщения
            attachments: Список URL вложений (необязательно)

        Возвращает:
            ChatMessageSchema: Схема созданного сообщения

        Исключения:
            ValueError: Если заказ не найден
            PermissionError: Если пользователь не имеет доступа к заказу
        """
        # Проверяем существование заказа и доступ пользователя
        order = await self.get_order(order_id)
        if order.user_id != user_id:
            raise PermissionError("User can only add messages to own orders")

        # Создаем данные сообщения
        message_data = {
            "order_id": order_id,
            "sender_id": user_id,
            "message": message,
            "attachments": attachments or []
        }

        # В реальной реализации здесь будет вызов репозитория для сохранения сообщения
        # Например:
        # db_message = await self.chat_repo.create(message_data)
        # return ChatMessageSchema.model_validate(db_message)

        # Заглушка для примера:
        return ChatMessageSchema(
            id=uuid.uuid4(),
            order_id=order_id,
            sender_id=user_id,
            message=message,
            attachments=attachments or [],
            created_at=datetime.now(),
            is_read=False
        )

    async def get_order_messages(
            self,
            order_id: UUID,
            limit: int = 100
    ) -> List[ChatMessageSchema]:
        """
        Получает историю сообщений чата заказа.

        Параметры:
            order_id: UUID заказа
            limit: Максимальное количество сообщений (по умолчанию 100)

        Возвращает:
            List[ChatMessageSchema]: Список сообщений, отсортированный по дате создания

        Исключения:
            ValueError: Если заказ не найден
        """
        # Проверяем существование заказа
        await self.get_order(order_id)

        # В реальной реализации здесь будет запрос к репозиторию:
        # messages = await self.chat_repo.get_by_order(order_id, limit=limit)
        # return [ChatMessageSchema.model_validate(m) for m in messages]

        # Заглушка для примера:
        return [
            ChatMessageSchema(
                id=uuid.uuid4(),
                order_id=order_id,
                sender_id=uuid.uuid4(),
                message=f"Тестовое сообщение {i}",
                attachments=[],
                created_at=datetime.now(),
                is_read=True
            )
            for i in range(3)
        ]

    async def get_user_orders(
            self,
            user_id: UUID,
            status: Optional[str] = None
    ) -> Sequence[Row[Any] | RowMapping | Any]:
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

    async def assign_to_factory(
            self,
            order_id: UUID,
            factory_id: Optional[UUID] = None
    ) -> Order:
        """
        Назначает заказ на производство (фабрику).

        Параметры:
            order_id: UUID заказа
            factory_id: UUID фабрики (если None - выбирается автоматически)

        Возвращает:
            Order: Обновленный заказ

        Исключения:
            ValueError: Если заказ не найден или не может быть назначен
            PermissionError: Если пользователь не имеет прав
        """
        async with self.session.begin():
            order = await self.get_order(order_id)

            # Проверка статуса заказа
            if order.status != CoreOrderStatus.PAID:
                raise ValueError("Only PAID orders can be assigned to factory")

            # Если фабрика не указана - находим подходящую
            if not factory_id:
                # Здесь должна быть логика автоматического выбора фабрики
                # Например, через ProductionService
                factory_id = uuid.uuid4()  # Заглушка

            # Обновляем заказ
            updated_order = await self.order_repo.update(
                order_id,
                {
                    "factory_id": factory_id,
                    "status": CoreOrderStatus.PRODUCTION,
                    "production_deadline": datetime.now() + timedelta(days=7)  # +7 дней на производство
                }
            )

            # Здесь можно добавить вызов API фабрики для уведомления

            return updated_order

    async def complete_order(
            self,
            order_id: UUID,
            user_id: Optional[UUID] = None
    ) -> Order:
        """
        Завершает заказ после выполнения.

        Параметры:
            order_id: UUID заказа
            user_id: UUID пользователя (для проверки прав)

        Возвращает:
            Order: Завершенный заказ

        Исключения:
            ValueError: Если заказ не найден или не может быть завершен
            PermissionError: Если пользователь не имеет прав
        """
        async with self.session.begin():
            order = await self.get_order(order_id)

            if user_id and order.user_id != user_id:
                raise PermissionError("User can only complete own orders")

            if order.status != CoreOrderStatus.SHIPPED:
                raise ValueError("Only SHIPPED orders can be completed")

            updated_order = await self.order_repo.update(
                order_id,
                {
                    "status": CoreOrderStatus.COMPLETED,
                    "completed_at": datetime.now()
                }
            )

            return updated_order

    async def cancel_order(
            self,
            order_id: UUID,
            user_id: Optional[UUID] = None,
            reason: Optional[str] = None
    ) -> Order:
        """
        Отменяет заказ.

        Параметры:
            order_id: UUID заказа
            user_id: UUID пользователя (для проверки прав)
            reason: Причина отмены (необязательно)

        Возвращает:
            Order: Отмененный заказ

        Исключения:
            ValueError: Если заказ не найден или не может быть отменен
            PermissionError: Если пользователь не имеет прав
        """
        async with self.session.begin():
            order = await self.get_order(order_id)

            if user_id and order.user_id != user_id:
                raise PermissionError("User can only cancel own orders")

            if order.status not in {CoreOrderStatus.CREATED, CoreOrderStatus.PAID}:
                raise ValueError("Only CREATED or PAID orders can be cancelled")

            updates = {
                "status": CoreOrderStatus.CANCELLED,
                "cancelled_at": datetime.now()
            }

            if reason:
                updates["cancellation_reason"] = reason

            # Если был платеж - инициируем возврат
            if order.status == CoreOrderStatus.PAID and order.payment:
                await self.payment_service.refund_payment(order.payment.id)

            return await self.order_repo.update(order_id, updates)

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
