# AdTime Backend API

Download dependencies
```bash
poetry install  # if using Poetry
# or
pip install -r requirements.txt
```

Alembic DB Migrations:

```bash
docker-compose run backend alembic upgrade head
```

Run:

```bash
docker-compose down -v && docker-compose up --build

# OR
docker-compose down
docker-compose build --no-cache backend
docker-compose up
```

Clear:

```bash
docker-compose down --remove-orphans -v
docker system prune -f
```

## Project Tree:

```text
adtime-mvp/
├── backend/
│   ├── .env
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── run_migrations.sh
│   ├── migrate.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── security.py
│   │   │   ├── celery.py
│   │   │   ├── storage.py
│   │   │   └── monitoring/
│   │   │       ├── __init__.py
│   │   │       ├── monitoring.py
│   │   │       └── prometheus.yml
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── generate.py
│   │   │       ├── payment.py
│   │   │       ├── users.py
│   │   │       ├── admin.py
│   │   │       └── marketplace.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── generation.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── subscription.py
│   │   │   └── marketplace.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── generation.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── subscription.py
│   │   │   ├── marketplace.py
│   │   │   └── factory.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── generation.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── subscription.py
│   │   │   ├── marketplace.py
│   │   │   ├── admin.py
│   │   │   └── errors.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── auth.py
│   │   │   ├── generation.py
│   │   │   ├── kandinsky.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   ├── subscription.py
│   │   │   ├── marketplace.py
│   │   │   └── production.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── payment_tasks.py
│   └── migrations/
│       ├── versions/
│       │   └── ... (файлы миграций)
│       └── env.py
└── docker-compose.yml
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