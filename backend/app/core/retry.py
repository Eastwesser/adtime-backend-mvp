import asyncio
from typing import Callable, Awaitable, Optional
from functools import wraps
from app.core.logger.logger import logger

class RetryManager:
    """Manage retry logic for async operations"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    async def execute_with_retry(
        self, 
        func: Callable[..., Awaitable], 
        *args, 
        **kwargs
    ) -> Optional[any]:
        """Execute async function with retry logic"""
        retry_count = 0
        current_delay = self.delay
        
        while retry_count <= self.max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                if retry_count > self.max_retries:
                    logger.error(
                        f"Operation failed after {self.max_retries} retries: {e}",
                        exc_info=True,
                        extra={"function": func.__name__, "args": args, "kwargs": kwargs}
                    )
                    raise
                
                logger.warning(
                    f"Retry {retry_count}/{self.max_retries} for {func.__name__}: {e}",
                    extra={"delay": current_delay}
                )
                
                await asyncio.sleep(current_delay)
                current_delay *= self.backoff
        
        return None

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retry logic"""
    def decorator(func: Callable[..., Awaitable]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_manager = RetryManager(max_retries, delay, backoff)
            return await retry_manager.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator

# Global instance with default settings
retry_manager = RetryManager()
