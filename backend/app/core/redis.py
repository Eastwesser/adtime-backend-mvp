from typing import Optional
import redis.asyncio as redis
from app.core.config import settings
from app.core.logger.logger import logger  # Direct import of the logger instance

class RedisClient:
    """
    Async Redis client wrapper with connection management.
    """
    _instance: Optional['RedisClient'] = None
    _client: redis.Redis 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self._client = redis.from_url(
                str(settings.REDIS_URL),
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                decode_responses=True
            )
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise

    @property
    def client(self):
        return self._client

    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return await self._client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def close(self):
        """Properly close connection"""
        await self._client.close()
        logger.info("Redis connection closed")

    # async def ping(self) -> bool:
    #     """Check Redis connection"""
    #     try:
    #         return await self.client.ping()
    #     except Exception as e:
    #         logger.error(f"Redis ping failed: {e}")
    #         return False

    # async def close(self):
    #     """Properly close connection"""
    #     await self.client.close()
    #     logger.info("Redis connection closed")

# Global instance
redis_client = RedisClient()
