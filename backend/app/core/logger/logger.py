import logging
import sys
from typing import Optional


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(handler)
    return logger


def error(message: str, exc_info=None, context: dict = None) -> None:
    """Логирует ошибку с дополнительным контекстом.

    Args:
        message: Основное сообщение об ошибке
        exc_info: Информация об исключении (если есть)
        context: Дополнительный контекст для логирования
    """
    logger = logging.getLogger(__name__)
    extra = context or {}
    logger.error(
        msg=message,
        exc_info=exc_info,
        extra={"context": extra}
    )


def critical(
        message: str,
        exc_info: Optional[BaseException] = None,
        context: Optional[dict] = None,
        stack_info: bool = False,
) -> None:
    """Логирует критическую ошибку с полным контекстом.

    Используется для фатальных ошибок, требующих немедленного внимания.

    Args:
        message: Основное сообщение об ошибке
        exc_info: Исключение (если есть), будет добавлен traceback
        context: Дополнительный контекст в формате словаря
        stack_info: Флаг для вывода полного стека вызовов
    """
    logger = logging.getLogger(__name__)
    extra = context or {}

    # Добавляем информацию об исключении, если оно есть
    if exc_info:
        extra['exception_type'] = exc_info.__class__.__name__

    logger.critical(
        msg=message,
        exc_info=exc_info,
        extra={"context": extra},
        stack_info=stack_info
    )
