from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.schemas import OrderResponse
from backend.app.models import Factory
from backend.app.models.order import OrderStatus
from backend.app.repositories.factory import FactoryRepository
from backend.app.repositories.order import OrderRepository


class ProductionService:
    """
    Сервис для управления производственным процессом.
    Отвечает за:
    - Распределение заказов по фабрикам
    - Контроль сроков производства
    - Обработку ошибок производства
    """

    def __init__(self, order_repo: OrderRepository, factory_repo: FactoryRepository):
        self.order_repo = order_repo
        self.factory_repo = factory_repo

    async def assign_to_factory(self, order_id: UUID):
        """
        Assign an order to the most suitable production factory
        
        Args:
            order_id: UUID of the order to assign
            
        Returns:
            bool: True if assignment was successful
            
        Raises:
            ValueError: If order not found or no available factories
        """
        order = await self.order_repo.get(order_id)
        if not order:
            raise ValueError("Order not found")

        factory = await self.find_best_factory()
        if not factory:
            raise ValueError("No available factories")

        await self.order_repo.update(order_id, {
            "factory_id": factory.id,
            "status": OrderStatus.PRODUCTION
        })

        # Здесь будет вызов API фабрики
        return True

    async def find_best_factory(self) -> Optional[Factory]:
        # Логика выбора фабрики по специализации и загрузке
        return await self.factory_repo.find_available()

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
