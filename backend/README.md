# AdTime Backend API

Clear all, before work:

```bash
docker-compose down --remove-orphans -v
docker system prune -f
```
Build:
```bash
docker-compose up --build  # Builds images and starts all services

# Backend: http://localhost:8042
# Prometheus: http://localhost:9090
```

Alembic DB Migrations:

```bash
docker-compose run backend alembic upgrade head

# While server is ONLINE
docker-compose exec backend alembic revision --autogenerate -m "fix_relationships"
docker-compose exec backend alembic upgrade head

docker-compose down -v
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

```text
.
├── backend
│   ├── alembic.ini
│   ├── app
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   └── v1
│   │   │       ├── admin.py
│   │   │       ├── auth.py
│   │   │       ├── generate.py
│   │   │       ├── __init__.py
│   │   │       ├── marketplace.py
│   │   │       ├── payment.py
│   │   │       └── users.py
│   │   ├── core
│   │   │   ├── chat.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── __init__.py
│   │   │   ├── logger
│   │   │   │   ├── __init__.py
│   │   │   │   └── logger.py
│   │   │   ├── monitoring
│   │   │   │   ├── __init__.py
│   │   │   │   ├── monitoring.py
│   │   │   │   └── prometheus.yml
│   │   │   ├── order_status.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── redis.py
│   │   │   ├── security.py
│   │   │   ├── storage.py
│   │   │   ├── testing.py
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
│   │   │   │   ├── factory.cpython-312.pyc
│   │   │   │   └── __init__.cpython-312.pyc
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
│   │   │   ├── subscription.py
│   │   │   └── user.py
│   │   ├── schemas
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── errors.py
│   │   │   ├── generation.py
│   │   │   ├── __init__.py
│   │   │   ├── marketplace.py
│   │   │   ├── notifications.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── subscription.py
│   │   │   └── user.py
│   │   └── services
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
│   │       ├── subscription.py
│   │       ├── user.py
│   │       └── yookassa_adapter.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── migrate.py
│   ├── migrations
│   │   ├── env.py
│   │   ├── __pycache__
│   │   │   └── env.cpython-312.pyc
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions
│   │       └── 2217af24be5b_initial_migration.py
│   ├── poetry.lock
│   ├── __pycache__
│   │   └── __init__.cpython-312.pyc
│   ├── pyproject.toml
│   ├── README.md
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── run_migrations.py
│   └── run_migrations.sh
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements-dev.txt
└── requirements.txt

18 directories, 100 files
```

## Ключевые файлы:

### Конфигурация:

    .env - переменные окружения
    config.py - настройки приложения
    alembic.ini - конфиг миграций

### Основное приложение:

    main.py - точка входа FastAPI
    database.py - подключение к PostgreSQL
    celery.py - настройка Celery

### API Endpoints:

    auth.py - аутентификация
    marketplace.py - маркетплейс
    payment.py - платежи
    generate.py - генерация изображений

### Data Layer:

    Модели в models/
    Репозитории в repositories/

### Бизнес-логика:

    Сервисы в services/
    Фоновые задачи в tasks/

### Документация:

    Схемы Pydantic в schemas/
    Описание API в Swagger (автогенерация)

### Инфраструктура:

    Dockerfile - образ backend
    docker-compose.yml - все сервисы

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

docker-compose down -v --remove-orphans
docker volume prune -f
docker-compose up -d postgres redis
docker-compose run backend alembic upgrade head
