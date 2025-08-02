from typing import Dict

from pydantic import BaseModel


class GenerationStatsResponse(BaseModel):
    """
    Статистика по генерациям изображений для админ-панели.

    Attributes:
        total_generations (int): Общее количество генераций
        avg_processing_time (float): Среднее время обработки в секундах
        by_status (Dict[str, int]): Количество генераций по статусам
    """
    total_generations: int
    avg_processing_time: float
    by_status: Dict[str, int]


class UserStatsResponse(BaseModel):
    """
    Статистика по пользователям для админ-панели.

    Attributes:
        total_users (int): Общее количество пользователей
        active_users (int): Количество активных пользователей (за последний месяц)
        by_role (Dict[str, int]): Распределение пользователей по ролям
    """
    total_users: int
    active_users: int
    by_role: Dict[str, int]


class SystemHealthResponse(BaseModel):
    """
    Информация о состоянии системы для мониторинга.

    Attributes:
        status (str): Общий статус системы (up, degraded, down)
        database (bool): Доступность базы данных
        redis (bool): Доступность Redis
        external_services (Dict[str, str]): Статусы внешних сервисов
    """
    status: str
    database: bool
    redis: bool
    external_services: Dict[str, str]
