from enum import Enum
from typing import Dict, List


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
        >>> OrderStatus.CREATED
        <OrderStatus.CREATED: 'created'>
        >>> OrderStatus.CREATED.value
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

    # @classmethod
    # def get_next_statuses(cls, current_status: Union['OrderStatus', str]) -> List['OrderStatus']:
    #     """Возвращает допустимые следующие статусы для текущего состояния заказа.
    #
    #     Метод реализует конечный автомат (state machine) для управления жизненным циклом заказа.
    #     Определяет, в какие статусы можно перевести заказ из текущего состояния.
    #
    #     Args:
    #         current_status: Текущий статус заказа (может быть строкой или OrderStatus)
    #
    #     Returns:
    #         Список допустимых следующих статусов (как объектов OrderStatus)
    #
    #     Raises:
    #         ValueError: Если передан неизвестный статус
    #
    #     Примеры:
    #         >>> OrderStatus.get_next_statuses(OrderStatus.CREATED)
    #         [<OrderStatus.PAID: 'paid'>, <OrderStatus.CANCELLED: 'cancelled'>]
    #
    #         >>> OrderStatus.get_next_statuses("created")
    #         [<OrderStatus.PAID: 'paid'>, <OrderStatus.CANCELLED: 'cancelled'>]
    #
    #     Бизнес-правила переходов:
    #         created → paid
    #         created → cancelled
    #         paid → production
    #         paid → cancelled
    #         production → shipped
    #         production → cancelled
    #         shipped → completed
    #     """
    #     # Конвертируем строковый статус в Enum при необходимости
    #     if isinstance(current_status, str):
    #         try:
    #             current_status = cls(current_status)
    #         except ValueError as e:
    #             raise ValueError(f"Unknown status: {current_status}") from e
    #
    #     workflow: Dict['OrderStatus', List['OrderStatus']] = {
    #         cls.CREATED: [cls.PAID, cls.CANCELLED],
    #         cls.PAID: [cls.PRODUCTION, cls.CANCELLED],
    #         cls.PRODUCTION: [cls.SHIPPED, cls.CANCELLED],
    #         cls.SHIPPED: [cls.COMPLETED],
    #     }
    #
    #     return workflow.get(current_status, [])

    @classmethod
    def get_workflow(cls) -> Dict['OrderStatus', List['OrderStatus']]:
        """Возвращает граф допустимых переходов статусов."""
        return {
            cls.CREATED: [cls.PAID, cls.CANCELLED],
            cls.PAID: [cls.PRODUCTION, cls.CANCELLED],
            cls.PRODUCTION: [cls.SHIPPED, cls.CANCELLED],
            cls.SHIPPED: [cls.COMPLETED],
        }

    # @classmethod
    # def is_valid_transition(cls, from_status: Union['OrderStatus', str],
    #                         to_status: Union['OrderStatus', str]) -> bool:
    #     """Проверяет, допустим ли переход между статусами.
    #
    #     Args:
    #         from_status: Исходный статус
    #         to_status: Целевой статус
    #
    #     Returns:
    #         True если переход допустим, иначе False
    #
    #     Пример:
    #         >>> OrderStatus.is_valid_transition("created", "paid")
    #         True
    #         >>> OrderStatus.is_valid_transition("created", "completed")
    #         False
    #     """
    #     try:
    #         if isinstance(from_status, str):
    #             from_status = cls(from_status)
    #         if isinstance(to_status, str):
    #             to_status = cls(to_status)
    #         return to_status in cls.get_next_statuses(from_status)
    #     except ValueError:
    #         return False
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
            current = cls(current_status)
            new = cls(new_status)
            return new in cls.get_transitions().get(current, [])
        except ValueError:
            return False

    @classmethod
    def get_transitions(cls) -> Dict['OrderStatus', List['OrderStatus']]:
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
