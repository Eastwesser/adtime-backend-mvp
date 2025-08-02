#!/bin/bash
set -e

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing migrations"
alembic upgrade head

exec "$@"