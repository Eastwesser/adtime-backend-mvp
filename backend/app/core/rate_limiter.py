import logging
from datetime import datetime

from fastapi import HTTPException

import redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Реализация rate limiting на основе Redis

    Пример использования:
         limiter = RateLimiter(redis, "10/minute")
         await limiter.check_request("user123")
    """

    def __init__(self, redis_client: redis.Redis, rate_limit: str):
        """
        Args:
            redis_client: Клиент Redis
            rate_limit: Лимит в формате "10/minute" или "100/hour"
        """
        self.redis = redis_client
        self.limit, self.period = self._parse_rate_limit(rate_limit)

    def _parse_rate_limit(self, rate_limit: str) -> tuple[int, int]:
        try:
            limit, period = rate_limit.split("/")
            limit = int(limit)

            if period == "second":
                period_seconds = 1
            elif period == "minute":
                period_seconds = 60
            elif period == "hour":
                period_seconds = 3600
            else:
                raise ValueError("Invalid period")

            return limit, period_seconds
        except Exception as e:
            raise ValueError(f"Invalid rate limit format: {rate_limit}") from e

    async def check_request(self, key: str) -> bool:
        """
        Проверяет, не превышен ли лимит запросов

        Returns:
            bool: True если запрос разрешен

        Raises:
            HTTPException: 429 если лимит превышен
        """
        now = datetime.now()
        current_window = now.replace(
            second=0,
            microsecond=0
        ).timestamp()

        redis_key = f"rate_limit:{key}:{current_window}"

        try:
            current = self.redis.incr(redis_key)
            if current == 1:
                self.redis.expire(redis_key, self.period)

            if current > self.limit:
                logger.warning(f"Rate limit exceeded for {key}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {self.limit}/{self.period}sec"
                )
            return True
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return True  # Fail open
