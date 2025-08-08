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
