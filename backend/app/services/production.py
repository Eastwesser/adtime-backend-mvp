from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from tenacity import stop_after_attempt, wait_exponential, retry

from app.core.monitoring.monitoring import ORDER_STATUS_TRANSITIONS
from app.models.factory import Factory
from app.core.logger import get_logger
from app.models.order import OrderStatus, Order
from app.repositories.factory import FactoryRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderResponse
from app.core.errors import (
    NotFoundError, 
    PermissionDeniedError,
    APIError
)
from app.schemas.errors import ErrorResponse

logger = get_logger(__name__)


class ProductionService:
    """
    Сервис управления производственными процессами и фабриками.

    Отвечает за:
    - Распределение заказов по фабрикам
    - Контроль сроков производства
    - Обработку ошибок производства
    """

    def __init__(
            self,
            session: AsyncSession,
            order_repo: OrderRepository,
            factory_repo: FactoryRepository
    ):
        self.session = session
        self.order_repo = order_repo
        self.factory_repo = factory_repo

    async def assign_to_factory(
            self,
            order_id: UUID,
            factory_id: Optional[UUID] = None
    ) -> OrderResponse:
        """
        Назначает заказ на фабрику и обновляет статус заказа.

        Позволяет:
        - Явно указать фабрику для назначения (через factory_id)
        - Автоматически подобрать фабрику по типу продукта из заказа
        - Уведомить фабрику через API (если указан api_url)
        - Обновить статус и сроки производства заказа

        Args:
            order_id: UUID заказа
            factory_id: Опциональный UUID фабрики для прямого назначения

        Returns:
            OrderResponse: Обновленный заказ с данными о назначенной фабрике

        Raises:
            HTTPException: С различными статус кодами при ошибках:
                - 404: Если заказ или фабрика не найдены
                - 400: Если не указан тип продукта или нет подходящих фабрик
                - 500: При внутренних ошибках сервера
        """
        async with self.session.begin():
            try:
                order = await self._validate_order(order_id)
                factory = await self._get_factory(order, factory_id)
                updated_order = await self._update_order_status(order_id, factory)
                await self._notify_factory_if_needed(factory, order_id)
                return OrderResponse.model_validate(updated_order)
            except NotFoundError as e:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message=str(e),
                        code="not_found"
                    ).model_dump()
                )
            except APIError as e:
                raise 

    async def _validate_order(self, order_id: UUID) -> Order:
        """Проверяет существование заказа."""
        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def _get_factory(self, order: Order, factory_id: Optional[UUID]) -> DeclarativeBase | Factory:
        """Находит подходящую фабрику для заказа."""
        if factory_id:
            return await self._get_specific_factory(factory_id)
        return await self._find_available_factory(order)

    async def _get_specific_factory(self, factory_id: UUID) -> DeclarativeBase:
        """Получает конкретную фабрику по ID."""
        factory = await self.factory_repo.get(factory_id)
        if not factory:
            raise HTTPException(status_code=404, detail="Factory not found")
        return factory

    async def _find_available_factory(self, order: Order) -> Factory:
        """Улучшенный алгоритм поиска фабрики."""
        product_type = order.design_specs.get("product_type")
        if not product_type:
            raise HTTPException(
                status_code=400,
                detail="Product type not specified in design specs"
            )

        # Ищем фабрику по специализации
        factory = await self.factory_repo.find_by_specialization(product_type)
        if not factory:
            raise HTTPException(
                status_code=404,
                detail=f"No available factories for product type: {product_type}"
            )

        # Проверяем загрузку фабрики
        if factory.current_load >= factory.production_capacity:
            raise HTTPException(
                status_code=429,
                detail="Factory is at full capacity"
            )

        return factory

    async def _update_order_status(self, order_id: UUID, factory: Factory) -> Order:
        """Обновляет статус заказа после назначения фабрики."""
        return await self.order_repo.update(
            order_id,
            {
                "factory_id": factory.id,
                "status": OrderStatus.PRODUCTION.value,
                "production_deadline": datetime.now() + timedelta(days=7),
                "production_status": "pending"
            }
        )

    async def _notify_factory(self, factory: Factory, order_id: UUID) -> bool:
        """Улучшенная реализация уведомления фабрики."""
        if not factory.api_url:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{factory.api_url}/api/orders",
                    json={
                        "order_id": str(order_id),
                        "factory_id": str(factory.id),
                        "details": {
                            "assigned_at": datetime.now().isoformat(),
                            "expected_deadline": (datetime.now() + timedelta(days=7)).isoformat()
                        }
                    },
                    headers={"Authorization": f"Bearer {factory.api_key}"} if factory.api_key else None
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to notify factory: {str(e)}"
            )

    async def _notify_factory_if_needed(self, factory: Factory, order_id: UUID) -> None:
        """Отправляет уведомление фабрике, если настроен API."""
        if getattr(factory, 'api_url', None):
            try:
                await self._notify_factory(factory, order_id)
            except Exception as e:
                logger.warning(f"Factory notification failed: {str(e)}")

    async def update_production_status(
            self,
            order_id: UUID,
            status: str,
            notes: str = None
    ) -> bool:
        """Обновление статуса производства заказа

        Args:
            order_id: UUID заказа
            status: Новый статус производства
            notes: Дополнительные заметки (необязательно)

        Returns:
            bool: True если обновление успешно

        Raises:
            ValueError: Если заказ не найден или статус невалиден
        """
        order = await self.order_repo.get(order_id)
        if not order:
            raise ValueError("Order not found")

        valid_statuses = ["in_progress", "completed", "failed", "shipped"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Allowed: {valid_statuses}")

        updates = {"production_status": status}
        if notes:
            updates["production_notes"] = notes

        if status == "completed":
            updates["completed_at"] = datetime.now()
        elif status == "failed":
            updates["failed_at"] = datetime.now()

        await self.order_repo.update(order_id, updates)
        return True

    async def get_factory_orders(
            self,
            factory_id: UUID,
            status: str = None
    ) -> List[OrderResponse]:
        """Получение заказов фабрики с фильтрацией по статусу

        Args:
            factory_id: UUID фабрики
            status: Статус заказов для фильтрации (необязательно)

        Returns:
            List[OrderResponse]: Список заказов фабрики
        """
        orders = await self.order_repo.get_by_factory(factory_id, status)
        return [OrderResponse.model_validate(o) for o in orders]

    async def _handle_assign_error(self, order_id: UUID, error: Exception) -> None:
        """Обрабатывает ошибки при назначении заказа на фабрику.

        Args:
            order_id: UUID заказа, который не удалось назначить
            error: Исключение, которое возникло

        Raises:
            HTTPException: Всегда вызывает 500 ошибку с деталями
        """
        logger.error(f"Failed to assign order {order_id}: {str(error)}",
                     exc_info=True,
                     extra={"order_id": order_id})

        await self.session.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Internal server error during factory assignment",
                "order_id": str(order_id),
                "error": str(error)
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def submit_to_factory(self, order: Order):
        """Отправка заказа на фабрику с автоматическими повторами"""
        try:
            factory = await self._get_factory_for_order(order)
            result = await self._call_factory_api(factory, order)

            ORDER_STATUS_TRANSITIONS.labels(
                from_status=order.status,
                to_status="production"
            ).inc()

            return result
        except Exception as e:
            logger.error(f"Factory submission failed: {str(e)}")
            raise

    async def _get_factory_for_order(self, order: Order) -> Factory:
        """Находит подходящую фабрику для заказа с учетом типа продукта и загрузки."""
        if not order.design_specs or not order.design_specs.get("product_type"):
            raise ValueError("Order missing product type specification")

        product_type = order.design_specs["product_type"]
        factories = await self.factory_repo.find_by_specialization(product_type)

        if not factories:
            raise ValueError(f"No factories found for product type: {product_type}")

        # Выбираем фабрику с наименьшей загрузкой
        return min(factories, key=lambda f: f.current_load / f.production_capacity)

    async def _call_factory_api(self, factory: Factory, order: Order) -> dict:
        """Вызывает API фабрики для создания производственного задания."""
        if not factory.api_url:
            raise ValueError("Factory API URL not configured")

        payload = {
            "order_id": str(order.id),
            "product_type": order.design_specs["product_type"],
            "specifications": order.design_specs,
            "deadline": order.production_deadline.isoformat() if order.production_deadline else None,
            "priority": "high" if order.design_specs.get("urgent", False) else "normal"
        }

        headers = {"Content-Type": "application/json"}
        if factory.api_key:
            headers["Authorization"] = f"Bearer {factory.api_key}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{factory.api_url}/orders",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        