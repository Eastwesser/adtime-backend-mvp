import logging
import sys
from typing import Optional

# Create and configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Module-level logger instance
logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)

def error(message: str, exc_info=None, context: dict = None) -> None:
    """Log error with context."""
    extra = context or {}
    logger.error(message, exc_info=exc_info, extra={"context": extra})

def critical(message: str, exc_info: Optional[BaseException] = None, 
            context: Optional[dict] = None, stack_info: bool = False) -> None:
    """Log critical error with full context."""
    extra = context or {}
    if exc_info:
        extra['exception_type'] = exc_info.__class__.__name__
    logger.critical(
        message,
        exc_info=exc_info,
        extra={"context": extra},
        stack_info=stack_info
    )

def setup_logger(name: str) -> logging.Logger:
    """Alias for get_logger for backward compatibility"""
    return get_logger(name)

