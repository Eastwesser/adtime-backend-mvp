from enum import Enum
from hashlib import new
from typing import Dict, List, Optional, Any

from alembic.command import current
from pydantic import BaseModel, ConfigDict

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class OrderStatus(str, Enum):
    """Централизованное перечисление статусов заказа, используемое во всей системе.

    Этот Enum служит единственным источником истины для всех статусов заказа в системе.
    Все другие модули (модели, схемы API) должны импортировать и использовать эти значения.

    Статусы:
        CREATED: Начальный статус после создания заказа. Ожидает оплаты.
        PAID: Заказ оплачен, ожидает передачи в производство.
        PRODUCTION: Заказ находится в процессе производства.
        SHIPPED: Заказ произведен и отправлен клиенту.
        COMPLETED: Заказ успешно доставлен и завершен.
        CANCELLED: Заказ отменен (может быть на любом этапе).

    Пример использования:
         OrderStatus.CREATED
        <OrderStatus.CREATED: 'created'>
         OrderStatus.CREATED.value
        'created'

    Важно:
        1. Эти значения должны точно совпадать с:
           - Значениями в SQLAlchemy Enum (модели)
           - Значениями в Pydantic Enum (схемах API)
        2. При добавлении новых статусов необходимо:
           - Обновить workflow в методе get_next_statuses
           - Обновить документацию
           - Синхронизировать изменения во всех модулях
    """
    CREATED = "created"
    PAID = "paid"
    PRODUCTION = "production"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    def get_display_name(self, lang: str = "en") -> str:
        """Локализованное название статуса"""
        names = {
            "en": {
                self.CREATED: "Created",
                self.PAID: "Paid",
                self.PRODUCTION: "In Production",
                self.SHIPPED: "Shipped",
                self.COMPLETED: "Completed",
                self.CANCELLED: "Cancelled"
            },
            "ru": {
                self.CREATED: "Создан",
                self.PAID: "Оплачен",
                self.PRODUCTION: "В производстве",
                self.SHIPPED: "Отправлен",
                self.COMPLETED: "Завершен",
                self.CANCELLED: "Отменен"
            }
        }
        return names.get(lang, "en")[self]

    @classmethod
    def get_workflow(cls) -> Dict['OrderStatus', List['OrderStatus']]:
        """Возвращает граф допустимых переходов статусов."""
        return {
            cls.CREATED: [cls.PAID, cls.CANCELLED],
            cls.PAID: [cls.PRODUCTION, cls.CANCELLED],
            cls.PRODUCTION: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.COMPLETED],
        }

    @classmethod
    def is_valid(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False

    @classmethod
    def is_valid_transition(cls, current_status: str, new_status: str) -> bool:
        """Проверяет допустимость перехода между статусами.

        Args:
            current_status: Текущий статус заказа
            new_status: Новый статус для перехода

        Returns:
            bool: True если переход допустим, иначе False
        """
        try:
            current_status = cls(current)
            new_status = cls(new)
        except ValueError as e:
            raise ValueError(f"Invalid status: {e}")

        allowed = cls.get_transitions().get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition from {current} to {new}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

    @classmethod
    def get_transitions(cls) -> dict['OrderStatus', list['OrderStatus']]:
        """Returns allowed status transitions"""
        return {
            cls.CREATED: [cls.PAID, cls.CANCELLED],
            cls.PAID: [cls.PRODUCTION, cls.CANCELLED],
            cls.PRODUCTION: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.COMPLETED],
        }

    @classmethod
    def validate_transition(cls, current: str, new: str) -> None:
        """Валидация перехода статусов с исключениями"""
        try:
            current_status = cls(current)
            new_status = cls(new)
        except ValueError as e:
            raise ValueError(f"Invalid status value: {e}")

        allowed = cls.get_transitions().get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition from {current} to {new}. "
                f"Allowed: {[s.value for s in allowed]}"
            )


class StatusTransition(BaseModel):
    """Модель для описания перехода статуса"""
    
    from_status: OrderStatus
    to_status: OrderStatus
    reason: Optional[str] = None
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "from_status": "created",
                "to_status": "paid",
                "reason": "Customer made payment"
            }
        }
    )

    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
