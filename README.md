``# AdTime MVP Core

> Приватный репозиторий основного продукта. Версия 1.0 (MVP)

###  🛠️ Локальный запуск

```bash
git clone git@github.com:Eastwesser/adtime-mvp.git
cd adtime-mvp
```

###  Варианты запуска (через Makefile):

```bash
make dev       # Бэкенд + фронтенд (разработка)
make prod      # Продуктовый режим
make stop      # Остановка всех сервисов
```

## Порты:
```text
:8042 — Backend API (Swagger: /docs)
:3000 — Frontend
:9091 — Мониторинг (Prometheus)
```
### 📌 Важные разделы

### 🔙 Backend (FastAPI/Python)
```bash
poetry install  # Установка зависимостей
make test       # Запуск тестов
```

### Конфигурация:

Скопируйте .env.template → .env

Креды для разработки в 1Password (запросить у @K1vv1)

### 🖥 Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### 🔒 Workflow (GitHub)

Создаем ветку от main:

```bash
git checkout -b feat/feature-name
```
Пушим и создаем Pull Request

Обязательно:
```text
1 approval от команды

Все тесты пройдены

Актуальность с main (no conflicts)
```

### 🚨 Если что-то сломалось
Проверьте логи:

```bash
make logs
```

Срочные вопросы / Критические баги — отмечать @K1vv1 с тегом [CRITICAL]

### 📍 Контакты
```text
Роль:	    Контакт:
Backend	    @K1vv1
Frontend	@FrontendDev
DevOps	    @DevOps
```

⚠️ Доступ к репозиторию предоставляется только через invite от @Eastwesser