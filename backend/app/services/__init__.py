"""
Инициализация сервисного слоя приложения.

Содержит все бизнес-сервисы, которые инкапсулируют:
- Основную бизнес-логику
- Интеграции с внешними сервисами
- Координацию между репозиториями

Сервисы:
- AuthService: Аутентификация и авторизация
- GenerationService: Генерация контента через Kandinsky
- OrderService: Управление заказами
- PaymentService: Платежи и транзакции
- SubscriptionService: Управление подписками
"""
from .auth import AuthService
from .generation import GenerationService
from .order import OrderService
from .payment import PaymentService
from .subscription import SubscriptionService

__all__ = [
    'AuthService',
    'GenerationService',
    'OrderService',
    'PaymentService',
    'SubscriptionService'
]
