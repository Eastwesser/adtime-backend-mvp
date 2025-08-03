from __future__ import annotations

from typing import Optional, Any, Sequence
from uuid import UUID

from secretstorage import item
from sqlalchemy import Row, RowMapping, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.marketplace import MarketItem
from backend.app.models.order import Order
from .base import BaseRepository
from ..schemas import CartItem
from ..services import PaymentService
from ..services.notifications import NotificationService


class MarketplaceRepository(BaseRepository[MarketItem]):
    """
    Репозиторий для работы с маркетплейсом дизайнов.

    Основная функциональность:
    - Управление товарами маркетплейса
    - Работа с корзиной пользователя
    - Создание заказов из товаров

    Сложная логика:
    1. Создание заказа:
       - Валидация спецификаций
       - Создание платежа
       - Уведомления участникам
       - Очистка корзины

    2. Фильтрация товаров:
       - По типу, цене, рейтингу
       - Поиск по названию
       - Сортировка по популярности

    Интеграции:
    - PaymentService для платежей
    - NotificationService для уведомлений
    - OrderService для создания заказов

    Особенности:
    - Транзакционность критичных операций
    - Валидация данных перед сохранением
    """

    def __init__(
            self,
            session: AsyncSession,
            payment_service: PaymentService,
            notification_service: NotificationService,
    ):
        super().__init__(MarketItem, session)  # Передаем session в родительский класс
        self.payment_service = payment_service
        self.notification_service = notification_service

    async def get_item(self, item_id: UUID) -> Optional[MarketItem]:
        """Получает товар по ID."""
        result = await self.session.execute(
            select(MarketItem).where(MarketItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_filtered_items(
            self,
            item_type: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            rating: Optional[float] = None,
            search: Optional[str] = None
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        query = select(MarketItem)

        if item_type:
            query = query.where(MarketItem.item_type == item_type)
        if min_price:
            query = query.where(MarketItem.price >= min_price)
        if max_price:
            query = query.where(MarketItem.price <= max_price)
        if rating:
            query = query.where(MarketItem.rating >= rating)
        if search:
            query = query.where(MarketItem.title.ilike(f"%{search}%"))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_to_user_cart(
            self,
            user_id: UUID,
            item_id: UUID,
            quantity: int
    ) -> CartItem:
        """Добавляет товар в корзину пользователя."""
        cart_item = await self.get_cart_item(user_id, item_id)
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=quantity)
            self.session.add(cart_item)

        await self.session.commit()
        return cart_item

    async def create_order(
            self,
            user_id: UUID,
            item_id: UUID,
            amount: float,
            specs: dict
    ) -> dict:
        """Создает заказ из товара маркетплейса.

        Args:
            user_id: UUID покупателя
            item_id: UUID товара
            amount: Сумма заказа
            specs: Спецификации заказа

        Returns:
            dict: Созданный заказ и информацию о платеже

        Raises:
            ValueError: Если товар не найден
        """
        try:
            async with self.session.begin():
                # Получаем товар
                item = await self.get_item(item_id)
                if not item:
                    raise ValueError("Item not found")
                if amount <= 0:
                    raise ValueError("Amount must be positive")

                # Создание заказа и платежа
                order, payment = await self._create_order_and_payment(
                    user_id, item_id, amount, specs, item.title
                )

                # Очистка корзины и отправка уведомлений
                await self._post_order_actions(user_id, item_id, user_id, item, order.id)

                return {"order": order, "payment": payment}


        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create order: {str(e)}")

    async def get_cart_item(
            self,
            user_id: UUID,
            item_id: UUID
    ) -> Optional[CartItem]:
        """Получает товар из корзины пользователя."""
        result = await self.session.execute(
            select(CartItem)
            .where(
                CartItem.user_id == user_id,
                CartItem.item_id == item_id
            )
        )
        return result.scalar_one_or_none()

    async def remove_from_cart(
            self,
            user_id: UUID,
            item_id: UUID
    ) -> None:
        """Удаляет товар из корзины пользователя."""
        await self.session.execute(
            delete(CartItem)
            .where(
                CartItem.user_id == user_id,
                CartItem.item_id == item_id
            )
        )
        await self.session.commit()

    def _validate_specs(self, specs: dict, item: MarketItem) -> None:
        """Валидирует спецификации заказа."""
        if not isinstance(specs, dict):
            raise ValueError("Specs must be a dictionary")
        # Проверяем обязательные поля
        required_fields = item.specs.get('required_fields', [])
        for field in required_fields:
            if field not in specs:
                raise ValueError(f"Missing required field: {field}")

        # Проверяем типы данных
        type_check = {
            'size': str,
            'color': str,
            'quantity': int
        }

        for field, field_type in type_check.items():
            if field in specs and not isinstance(specs[field], field_type):
                raise ValueError(f"Field {field} must be {field_type.__name__}")

    async def cancel_order(self, order_id: UUID, user_id: UUID) -> None:
        """Отменяет заказ и возвращает средства."""
        async with self.session.begin():
            order = await self.session.get(Order, order_id)
            if not order:
                raise ValueError("Order not found")

            if order.user_id != user_id:
                raise PermissionError("Cannot cancel another user's order")

            if order.status not in ["created", "pending"]:
                raise ValueError("Order cannot be canceled in current status")

            # Возврат платежа
            if order.payment:
                await self.payment_service.refund_payment(order.payment.id)

            # Обновление статуса
            order.status = "canceled"
            await self.session.commit()

            # Уведомление
            await self.notification_service.send(
                user_id=user_id,
                title="Order canceled",
                message=f"Order #{order.id} has been canceled",
                notification_type="order"
            )

            # После создания заказа:
            await self.notification_service.send(
                user_id=user_id,
                title="Order created",
                message=f"Your order #{order.id} has been created",
                notification_type="order"
            )

            # Для продавца (если у товара есть designer_id):
            if item.designer_id:
                await self.notification_service.send(
                    user_id=item.designer_id,
                    title="New order for your item",
                    message=f"Item {item.title} has been ordered",
                    notification_type="order"
                )

    async def _create_order_and_payment(self, user_id, item_id, amount, specs, item_title):
        """Создает заказ и платеж в транзакции."""
        order = Order(
            user_id=user_id,
            market_item_id=item_id,
            amount=amount,
            design_specs=specs,
            status="created"
        )
        self.session.add(order)
        await self.session.flush()

        payment = await self.payment_service.create_payment(
            order_id=order.id,
            amount=amount,
            description=f"Payment for {item_title}"
        )
        self.session.add(payment)

        return order, payment

    async def _post_order_actions(self, user_id, item_id, buyer_id, item, order_id):
        """Выполняет действия после создания заказа."""
        await self.remove_from_cart(user_id, item_id)

        # Уведомление покупателю
        await self.notification_service.send(
            user_id=buyer_id,
            title="Order created",
            message=f"Your order #{order_id} has been created",
            notification_type="order"
        )

        # Уведомление продавцу
        if item.designer_id:
            await self.notification_service.send(
                user_id=item.designer_id,
                title="New order for your item",
                message=f"Item {item.title} has been ordered (Order #{order_id})",
                notification_type="order"
            )

    def _validate_order_creation(self, user_id, item, amount, specs):
        """Валидация данных перед созданием заказа."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount != item.price:
            raise ValueError("Amount doesn't match item price")
        self._validate_specs(specs, item)
