# AdTime Backend API

🚀 API Documentation для фронтенд-разработчиков

🔐 Аутентификация (Auth)

    POST /api/v1/auth/login - Вход в систему

    POST /api/v1/auth/register - Регистрация нового пользователя

💰 Баланс (Balance)

    GET /api/v1/balance - Получить текущий баланс пользователя

    POST /api/v1/balance/deposit - Пополнить баланс

🎨 Генерация изображений (Generate)

    POST /api/v1/generate - Создать новую генерацию изображения

    POST /api/v1/generate/{generation_id}/cancel - Отменить генерацию

    GET /api/v1/generate/{generation_id}/status - Проверить статус генерации

⚙️ Конфигурация генерации (Generation Config)

    GET /api/v1/generation_config/generation - Получить доступные стили, размеры и лимиты

📊 История (History)

    GET /api/v1/history/generations - Получить историю генераций пользователя

👍 Оценки (Feedback)

    POST /api/v1/feedback/generation/{generation_id} - Оценить результат генерации (лайк/дизлайк)

🛒 Маркетплейс (Marketplace)

    GET /api/v1/marketplace/items - Просмотр товаров в маркетплейсе

    POST /api/v1/marketplace/items/{item_id}/cart - Добавить товар в корзину

    POST /api/v1/marketplace/items/{item_id}/order - Создать заказ напрямую

    POST /api/v1/marketplace/cart/items - Работа с корзиной

    POST /api/v1/marketplace/orders/direct - Создать прямой заказ

📦 Заказы (Orders)

    POST /api/v1/orders - Создать новый заказ

    GET /api/v1/orders - Получить список заказов пользователя

    GET /api/v1/orders/{order_id} - Получить детали заказа

    PATCH /api/v1/orders/{order_id} - Обновить заказ

    DELETE /api/v1/orders/{order_id} - Удалить заказ

    POST /api/v1/orders/{order_id}/cancel - Отменить заказ

    POST /api/v1/orders/{order_id}/messages - Отправить сообщение по заказу

    GET /api/v1/orders/{order_id}/messages - Получить сообщения по заказу

🏭 Производство (Production)

    POST /api/v1/production/orders/{order_id}/assign - Назначить заказ на фабрику

    PATCH /api/v1/production/orders/{order_id}/status - Обновить статус производства

💳 Платежи (Payment)

    POST /api/v1/payment/create - Создать платеж

    POST /api/v1/payment/webhook - Webhook для обработки платежей

    GET /api/v1/payment/{payment_id}/redirect - Перенаправление на оплату

    GET /api/v1/payment/{payment_id}/status - Проверить статус платежа

📤 Загрузка файлов (Upload)

    POST /api/v1/upload/image - Загрузить изображение для генерации

👤 Пользователи (Users)

    GET /api/v1/users/me - Получить данные текущего пользователя

    PATCH /api/v1/users/me - Обновить данные пользователя

    GET /api/v1/users/{user_id} - Получить данные пользователя по ID

👨‍💼 Админка (Admin)

    GET /api/v1/admin/generations/stats - Статистика генераций (только для админов)

    POST /api/v1/admin/users/{user_id}/grant-admin - Дать права администратора

🩺 Системные (System)

    GET /health - Проверка здоровья сервера

    GET /metrics - Метрики Prometheus

    GET /metrics/health - Health check для метрик

📚 Документация

    GET /docs - Swagger UI документация

    GET /documentation - ReDoc документация

    GET /openapi.json - OpenAPI спецификация

🎯 Приоритетные эндпоинты для разработки:

    Срочно: /balance, /generate, /upload/image - основные функции

    Важно: /auth/*, /users/me - авторизация и профиль

    Далее: /marketplace/*, /orders/* - маркетплейс и заказы

    Дополнительно: Остальные эндпоинты


For Fronetnders:
To check all existing routes type these:
```bash
cd backend
python list_routes.py

# This will show you such list of routes (available since 21.08.2025)
2025-08-21 15:17:49,631 - app.core.logger.logger - INFO - Redis client initialized
🌐 Все доступные роуты API:
==================================================
GET                  /
GET                  /api/v1/admin/generations/stats
POST                 /api/v1/admin/users/{user_id}/grant-admin
POST                 /api/v1/auth/login
POST                 /api/v1/auth/register
GET                  /api/v1/balance
POST                 /api/v1/balance/deposit
POST                 /api/v1/feedback/generation/{generation_id}
POST                 /api/v1/generate
POST                 /api/v1/generate/{generation_id}/cancel
GET                  /api/v1/generate/{generation_id}/status
GET                  /api/v1/generation_config/generation
GET                  /api/v1/history/generations
POST                 /api/v1/marketplace/cart/items
GET                  /api/v1/marketplace/items
POST                 /api/v1/marketplace/items/{item_id}/cart
POST                 /api/v1/marketplace/items/{item_id}/order
POST                 /api/v1/marketplace/orders/direct
POST                 /api/v1/orders
GET                  /api/v1/orders
GET                  /api/v1/orders/{order_id}
PATCH                /api/v1/orders/{order_id}
DELETE               /api/v1/orders/{order_id}
POST                 /api/v1/orders/{order_id}/cancel
POST                 /api/v1/orders/{order_id}/messages
GET                  /api/v1/orders/{order_id}/messages
POST                 /api/v1/payment/create
POST                 /api/v1/payment/webhook
GET                  /api/v1/payment/{payment_id}/redirect
GET                  /api/v1/payment/{payment_id}/status
POST                 /api/v1/production/orders/{order_id}/assign
PATCH                /api/v1/production/orders/{order_id}/status
POST                 /api/v1/upload/image
GET                  /api/v1/users/me
PATCH                /api/v1/users/me
GET                  /api/v1/users/{user_id}
GET | HEAD           /docs
GET | HEAD           /docs/oauth2-redirect
GET | HEAD           /documentation
GET                  /health
GET                  /metrics
GET                  /metrics/health
GET | HEAD           /openapi.json

# for HTML
python api_documentation.py
```

Build:
```bash
docker-compose up --build  # Builds images and starts all services

# FOR DEVELOPMENT
docker-compose -f docker-compose.dev.yml up --build

# Backend: http://localhost:8042
# Prometheus: http://localhost:9090
```

Alembic DB Migrations:
```bash
docker-compose run backend alembic upgrade head
```

Complete start:
```bash
# While server is ONLINE
docker-compose exec backend alembic revision --autogenerate -m "fix_relationships"
docker-compose exec backend alembic upgrade head

docker-compose down -v --remove-orphans
docker volume prune -f
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
docker-compose up
```

Run:
```bash
docker-compose down -v && docker-compose up --build

# Or with full clear before run
docker-compose down --remove-orphans -v
docker system prune -f
docker-compose down
docker-compose build --no-cache backend
docker-compose up
```


## Project Tree:
To get it run : 
```bash
tree -L 5
```

Our project's current tree:
```text
.
├── backend
│   ├── alembic.ini
│   ├── API_DOCUMENTATION.html
│   ├── api_documentation.py
│   ├── app
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   └── __init__.cpython-312.pyc
│   │   │   └── v1
│   │   │       ├── admin.py
│   │   │       ├── auth.py
│   │   │       ├── balance.py
│   │   │       ├── feedback.py
│   │   │       ├── generate.py
│   │   │       ├── generation_config.py
│   │   │       ├── history.py
│   │   │       ├── __init__.py
│   │   │       ├── marketplace.py
│   │   │       ├── orders.py
│   │   │       ├── payment.py
│   │   │       ├── production.py
│   │   │       ├── __pycache__
│   │   │       ├── upload.py
│   │   │       └── users.py
│   │   ├── core
│   │   │   ├── chat.py
│   │   │   ├── config.py
│   │   │   ├── currency.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── errors.py
│   │   │   ├── factory_client.py
│   │   │   ├── __init__.py
│   │   │   ├── logger
│   │   │   │   ├── __init__.py
│   │   │   │   ├── logger.py
│   │   │   │   └── __pycache__
│   │   │   ├── monitoring
│   │   │   │   ├── __init__.py
│   │   │   │   ├── monitoring.py
│   │   │   │   ├── prometheus.yml
│   │   │   │   └── __pycache__
│   │   │   ├── order_status.py
│   │   │   ├── __pycache__
│   │   │   │   ├── config.cpython-312.pyc
│   │   │   │   ├── database.cpython-312.pyc
│   │   │   │   ├── dependencies.cpython-312.pyc
│   │   │   │   ├── errors.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── order_status.cpython-312.pyc
│   │   │   │   ├── rate_limiter.cpython-312.pyc
│   │   │   │   ├── redis.cpython-312.pyc
│   │   │   │   ├── responses.cpython-312.pyc
│   │   │   │   ├── security.cpython-312.pyc
│   │   │   │   ├── storage.cpython-312.pyc
│   │   │   │   ├── webhooks.cpython-312.pyc
│   │   │   │   └── websocket_manager.cpython-312.pyc
│   │   │   ├── rate_limiter.py
│   │   │   ├── redis.py
│   │   │   ├── responses.py
│   │   │   ├── retry.py
│   │   │   ├── security.py
│   │   │   ├── statuses.py
│   │   │   ├── storage.py
│   │   │   ├── testing.py
│   │   │   ├── webhooks.py
│   │   │   ├── webhook_validation.py
│   │   │   └── websocket_manager.py
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── base.py
│   │   │   ├── chat.py
│   │   │   ├── factory.py
│   │   │   ├── generation.py
│   │   │   ├── __init__.py
│   │   │   ├── marketplace.py
│   │   │   ├── notifications.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── __pycache__
│   │   │   │   ├── base.cpython-312.pyc
│   │   │   │   ├── chat.cpython-312.pyc
│   │   │   │   ├── factory.cpython-312.pyc
│   │   │   │   ├── generation.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── marketplace.cpython-312.pyc
│   │   │   │   ├── notifications.cpython-312.pyc
│   │   │   │   ├── order.cpython-312.pyc
│   │   │   │   ├── payment.cpython-312.pyc
│   │   │   │   ├── review.cpython-312.pyc
│   │   │   │   ├── subscription.cpython-312.pyc
│   │   │   │   └── user.cpython-312.pyc
│   │   │   ├── review.py
│   │   │   ├── subscription.py
│   │   │   └── user.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── main.cpython-312.pyc
│   │   ├── repositories
│   │   │   ├── base.py
│   │   │   ├── chat.py
│   │   │   ├── factory.py
│   │   │   ├── generation.py
│   │   │   ├── __init__.py
│   │   │   ├── marketplace.py
│   │   │   ├── notification.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── __pycache__
│   │   │   │   ├── base.cpython-312.pyc
│   │   │   │   ├── chat.cpython-312.pyc
│   │   │   │   ├── factory.cpython-312.pyc
│   │   │   │   ├── generation.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── marketplace.cpython-312.pyc
│   │   │   │   ├── notification.cpython-312.pyc
│   │   │   │   ├── order.cpython-312.pyc
│   │   │   │   ├── payment.cpython-312.pyc
│   │   │   │   ├── subscription.cpython-312.pyc
│   │   │   │   └── user.cpython-312.pyc
│   │   │   ├── subscription.py
│   │   │   └── user.py
│   │   ├── schemas
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── balance.py
│   │   │   ├── errors.py
│   │   │   ├── generation.py
│   │   │   ├── __init__.py
│   │   │   ├── marketplace.py
│   │   │   ├── notifications.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── __pycache__
│   │   │   │   ├── admin.cpython-312.pyc
│   │   │   │   ├── auth.cpython-312.pyc
│   │   │   │   ├── balance.cpython-312.pyc
│   │   │   │   ├── errors.cpython-312.pyc
│   │   │   │   ├── generation.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── marketplace.cpython-312.pyc
│   │   │   │   ├── notifications.cpython-312.pyc
│   │   │   │   ├── order.cpython-312.pyc
│   │   │   │   ├── payment.cpython-312.pyc
│   │   │   │   ├── schemas.cpython-312.pyc
│   │   │   │   ├── subscription.cpython-312.pyc
│   │   │   │   └── user.cpython-312.pyc
│   │   │   ├── schemas.py
│   │   │   ├── subscription.py
│   │   │   └── user.py
│   │   └── services
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── base.py
│   │       ├── generation.py
│   │       ├── __init__.py
│   │       ├── kandinsky.py
│   │       ├── marketplace.py
│   │       ├── notifications.py
│   │       ├── order.py
│   │       ├── payment.py
│   │       ├── production.py
│   │       ├── __pycache__
│   │       │   ├── admin.cpython-312.pyc
│   │       │   ├── auth.cpython-312.pyc
│   │       │   ├── generation.cpython-312.pyc
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   ├── kandinsky.cpython-312.pyc
│   │       │   ├── marketplace.cpython-312.pyc
│   │       │   ├── notifications.cpython-312.pyc
│   │       │   ├── order.cpython-312.pyc
│   │       │   ├── payment.cpython-312.pyc
│   │       │   ├── production.cpython-312.pyc
│   │       │   ├── storage.cpython-312.pyc
│   │       │   ├── subscription.cpython-312.pyc
│   │       │   ├── user.cpython-312.pyc
│   │       │   └── yookassa_adapter.cpython-312.pyc
│   │       ├── storage.py
│   │       ├── subscription.py
│   │       ├── user.py
│   │       └── yookassa_adapter.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── list_routes.py
│   ├── migrate.py
│   ├── migrations
│   │   ├── env.py
│   │   ├── __pycache__
│   │   │   └── env.cpython-312.pyc
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions
│   │       ├── 12e666579334_add_is_liked_to_generations.py
│   │       ├── 222222222222_consolidated_user_timestamps.py
│   │       ├── 333333333333_convert_to_kopecks.py
│   │       ├── 466b80ceb431_initial_migration.py
│   │       └── __pycache__
│   │           ├── 12e666579334_add_is_liked_to_generations.cpython-312.pyc
│   │           ├── 1d3e005ea667_add_created_at_to_users.cpython-312.pyc
│   │           ├── 222222222222_consolidated_user_timestamps.cpython-312.pyc
│   │           ├── 333333333333_convert_to_kopecks.cpython-312.pyc
│   │           ├── 3d2db5f4c33c_make_created_at_timezone_aware.cpython-312.pyc
│   │           ├── 466b80ceb431_initial_migration.cpython-312.pyc
│   │           ├── 863ffe69d8af_add_created_at_to_users.cpython-312.pyc
│   │           ├── 88684a029245_fix_created_at_default.cpython-312.pyc
│   │           ├── 8ca3efe506e0_fix_generation_order_relationship.cpython-312.pyc
│   │           ├── abc0300889f0_convert_currency_fields_to_kopecks.cpython-312.pyc
│   │           ├── consolidated_user_timestamps.cpython-312.pyc
│   │           ├── convert_currency_to_kopecks.cpython-312.pyc
│   │           └── ee7e2eccb06f_fix_relationships.cpython-312.pyc
│   ├── poetry.lock
│   ├── private.pem
│   ├── public.pem
│   ├── __pycache__
│   ├── pyproject.toml
│   ├── README.md
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── run_migrations.py
│   ├── run_migrations.sh
│   ├── tests
│   │   ├── conftest.py
│   │   ├── test_order.py
│   │   ├── test_payments.py
│   │   └── test_production.py
│   ├── uploads
│   │   └── images
│   └── venv
│       ├── bin
│       │   ├── activate
│       │   ├── activate.csh
│       │   ├── activate.fish
│       │   ├── Activate.ps1
│       │   ├── alembic
│       │   ├── black
│       │   ├── blackd
│       │   ├── distro
│       │   ├── dmypy
│       │   ├── dotenv
│       │   ├── email_validator
│       │   ├── faker
│       │   ├── fastapi
│       │   ├── httpx
│       │   ├── isort
│       │   ├── isort-identify-imports
│       │   ├── jp.py
│       │   ├── mako-render
│       │   ├── mypy
│       │   ├── mypyc
│       │   ├── netaddr
│       │   ├── normalizer
│       │   ├── pip
│       │   ├── pip3
│       │   ├── pip3.12
│       │   ├── pygmentize
│       │   ├── pyrsa-decrypt
│       │   ├── pyrsa-encrypt
│       │   ├── pyrsa-keygen
│       │   ├── pyrsa-priv2pub
│       │   ├── pyrsa-sign
│       │   ├── pyrsa-verify
│       │   ├── py.test
│       │   ├── pytest
│       │   ├── python -> python3
│       │   ├── python3 -> /usr/bin/python3
│       │   ├── python3.12 -> python3
│       │   ├── stubgen
│       │   ├── stubtest
│       │   └── uvicorn
│       ├── include
│       │   ├── python3.12
│       │   └── site
│       │       └── python3.12
│       ├── lib
│       │   └── python3.12
│       │       └── site-packages
│       ├── lib64 -> lib
│       └── pyvenv.cfg
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements-dev.txt
└── requirements.txt

40 directories, 246 files
```

## Ключевые файлы:

## Конфигурация (Configuration):
    .env - in root
    backend/app/core/config.py - main config
    backend/alembic.ini - Migrations config

## Основное приложение (Main Application):
    backend/app/main.py - FastAPI entry point
    backend/app/core/database.py - PostgreSQL connection
    backend/app/core/redis.py - Redis connection

## API Endpoints:
    backend/app/api/v1/auth.py - Authentication
    backend/app/api/v1/marketplace.py - Marketplace
    backend/app/api/v1/payment.py - Payments
    backend/app/api/v1/generate.py - Image generation
    backend/app/api/v1/orders.py - Orders
    backend/app/api/v1/users.py - Users
    backend/app/api/v1/admin.py - Admin

## Data Layer:
    Модели: backend/app/models/
    Репозитории: backend/app/repositories/

## Бизнес-логика (Business Logic / Use Cases):
    Сервисы: backend/app/services/ ✓ (complete set)

## Документация (Documentation):
    Схемы Pydantic: backend/app/schemas/
    Swagger: Auto-generated from FastAPI

## Инфраструктура (Infrastructure):
    backend/Dockerfile - Backend image
    docker-compose.yml - All services

## QUERY EXAMPLE
```bash
{
  "email": "RNBuser@example.com",
  "role": "user",
  "created_at": "2025-08-17T21:14:36.858Z",
  "password": "RNBbrother",
  "telegram_id": "RNBbro"
}
```

## RESPONSE EXAMPLE
```bash
{
  "user": {
    "email": "RNBuser@example.com",
    "role": "user",
    "created_at": "2025-08-17T21:15:15.204546Z",
    "id": "ea1b23bb-c3a1-4585-9c08-42b23255392d",
    "telegram_id": "RNBbro"
  },
  "token": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTFiMjNiYi1jM2ExLTQ1ODUtOWMwOC00MmIyMzI1NTM5MmQiLCJleHAiOjE3NTU0NjcxMTUsInJvbGUiOiJ1c2VyIn0.TIUoa13TlTNP9ps90z4WWtXeaTIp1B26_0qE64Hw6mqM8j5oGjJT8xseT1Z8EaIOLD7e1E191_7fI-pLbqhHzKdk37iXOLuf98V1QwEascTbIeUWn_Af9EVX_pm8Qof04ZcKCnK9UF3ckvQZm-lz-NHrs_5KfCVs1YCAIzA17fq8vPHJcpCev9QcNKK2QP0pln1ZEiqTaw4SW_GEnwFkjToQMIho5kcYqbm2HLdOAwEGS4-QK-6HaaaU1_9bhIsxIfzsNRqZyms6Tli1In64h3vqbymGy859_QqfNDymO6Y_Tvb6fweF3TDlVCcJovoEMaykL3K4Jf2uJ1jOC9OPp0nQcxcKjUgPGY9t5Yd-xcX_gioRYWzcv2z2rlM2SaqwmRchty_cAJXqPJE4hMM2ESjrPzhMs6Y4ZergnddTrvBoZ8TGYbshCKQePhc01qr3EdOnFGuvqsKG18ZJjCQqjIvjmOR1mFl8CUfBIkLFz4IYI_aSBoq53K9eDuj8-B5Ro5dKb5rh7K54upHCeXQL51W3lIVFXsc4pjHLljCSn97afhZkRPFPb0pt6MFZMH_jo8kDGbya5ifwNzUjqnr9cPewGwgj4W7_bxOhuuKfvCQkghqrXWhqqWhkNW5xlye5NvwVogJxXAZ9yHCmVymNjnpYYLlVIEE-pXFrrVeCgrA",
    "token_type": "bearer",
    "expires_in": 1800,
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTFiMjNiYi1jM2ExLTQ1ODUtOWMwOC00MmIyMzI1NTM5MmQiLCJleHAiOjE3NTYwNzAxMTUsInJvbGUiOiJyZWZyZXNoIn0.K-NbqkxYHd44XtDY8zcWbMoB5uC61YAQ3lCqftHN7NZcA9j5oclHIByZEltXXTAUGU9dhi1_NaXjPk5jJZCj2uy44E-6FKxg24h2mpEBKMDCAZTeigoKd9eVD5yWnGR3CYeDYfevETds8rp1vMb-KYL1mZ6cbb824xL0V0ol4J_LAoQhzLVOy_Q-I5QDhgj5IZVaBfyf3ydkXZgrx-OMwXARJxiXiAY6c9LoLpTFOf8AkUsvdj4XvzjNZ3pBaRI-0jrzp-dAWldegwqlC06CAqHFTqk94hZ9jJ3TZuz8lEalQReWrRPW3hzbiweHSOHoXgtnPNERE-d9hqxazdHfg3V_XAYx9kKK2uL-f0vYZ60GdOAgAxOU8S42qEllU9BPDbl8HdtvNDWXH3wz6uxRnW_ba6Pg5fZ7TNSZQQ6g2paIdbUfCEBKKACGDzeKgNEhYO66PWNw76hiju9QCKqt7JDMloAOG6bReLW2McxrQAT7FSJysIpcWgP2pvsRXtwYgvPsXa_Eli52Io0_VfISd3sHVyDuZhi-Dg78vAZXi5oCoRQBEVx7EBQriJP1lDgnsgReN3e-Av_SfEYds-A3mfu-HIhimVGd1XcQa3ISoJqp4pXSTnkcyDKOQ8P1Wu99EuD7RwkDDpqKkojmnSYQTsM7rQFtaMs0fcN-Zyh-ZYk",
    "issued_at": "2025-08-17T21:15:16.446491Z",
    "token_id": "b8a545e4-24fe-4a1a-86ac-644cd1fcf492",
    "scopes": [
      "read",
      "write"
    ]
  },
  "requires_2fa": false
}
```

## THE ENUM PROBLEM:

### 1. Find all Enum class definitions
```bash
grep -r "class.*Enum" app/
```

### 2. Find all enum imports
```bash
grep -r "from enum import" app/
# grep -r "import enum" app/
```

### 3. Find all Pydantic models using enums
```bash
# grep -r ":.*Enum" app/ | grep -v "OrderStatus"
# grep -r "=.*Enum" app/ | grep -v "OrderStatus"
```

### 4. Find custom JSON encoders
```bash
# grep -r "json_encoders" app/
# grep -r "json_encoder" app/
# grep -r "JSONEncoder" app/
```

### 5. Find schema modifiers
```bash
grep -r "openapi_schema" app/
grep -r "get_openapi" app/
grep -r "schema_extra" app/
grep -r "ConfigDict" app/
```

### 6. Find route response models
```bash
grep -r "response_model" app/
```

### 7. Find all enum usage in models
```bash
grep -r "Enum" app/core/ app/api/v1/ | grep -i "model"
```

### 8. Find any remaining enum serialization
```bash
# grep -r "\.value" app/ | grep "Enum"
```

## Tips for effective searching:


### Use -n flag to show line numbers:
```bash
grep -rn "Enum" app/
```

### Search specific directories:
```bash
grep -r "Enum" app/core/ app/api/v1/schemas/
```

### Exclude specific files:
```bash
grep -r "Enum" app/ --exclude="order_status.py"
```

### Case insensitive search:
```bash
grep -ri "enum" app/
```

### Count occurrences:
```bash
grep -r "Enum" app/ | wc -l
```

### Clear PyCache:
```bash
sudo find . -name "__pycache__" -exec rm -rf {} +
```

## DB ACCESS:
```bash
docker exec -it ddc9dd1533d8 psql -U postgres -d adtime
# OR
docker exec -it adtime_postgres psql -U postgres -d adtime

# -- List all tables
\dt

# -- List all databases
\l

# -- View users table
SELECT * FROM users;

# -- Quit psql
\q
```
## Clean the pycache directories
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

## SECURITY

```bash
# For testing only - use proper secrets in production
echo "dev_postgres_password" > secrets/postgres_password.txt
echo "dev_redis_password" > secrets/redis_password.txt
echo "dev_jwt_secret_$(openssl rand -hex 32)" > secrets/jwt_secret.txt
echo "test_kandinsky_key" > secrets/kandinsky_api_key.txt
echo "test_kandinsky_secret" > secrets/kandinsky_secret_key.txt
echo "test_yookassa_shop" > secrets/yookassa_shop_id.txt
echo "test_yookassa_secret" > secrets/yookassa_secret_key.txt
echo "test_s3_access" > secrets/s3_access_key.txt
echo "test_s3_secret" > secrets/s3_secret_key.txt

# Set permissions again
chmod 600 secrets/*.txt
```