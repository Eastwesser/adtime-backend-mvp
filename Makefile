# make adtime # to run full app
# make backend # to run backend only
# make frontend # to run frontend only

up:  ## Запуск всех сервисов
    docker-compose up -d

migrate:  ## Применить миграции
    docker-compose exec backend alembic upgrade head

logs:  ## Просмотр логов
    docker-compose logs -f

monitoring:  ## Запуск Grafana + Prometheus
    docker-compose -f docker-compose.monitoring.yml up
