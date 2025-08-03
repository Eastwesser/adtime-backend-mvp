from typing import Optional
import redis.asyncio as redis
from pydantic import RedisDsn

from backend.app.core.config import settings
from backend.app.core.logger import logger


class RedisClient:
    """
    Обертка для асинхронного клиента Redis с:
    - Подключением при инициализации
    - Автоматическим реконнектом
    - Логированием ошибок

    Пример использования:
        >>> redis = RedisClient()
        >>> await redis.set("key", "value")
    """

    _instance: Optional['RedisClient'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.client = redis.from_url(
            str(settings.REDIS_URL),
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            decode_responses=True
        )
        logger.info("Redis client initialized")

    async def ping(self) -> bool:
        """Проверка подключения к Redis"""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def close(self):
        """Корректное закрытие подключения"""
        await self.client.close()
        logger.info("Redis connection closed")


# Глобальный экземпляр
redis_client = RedisClient()