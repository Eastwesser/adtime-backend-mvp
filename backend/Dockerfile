FROM python:3.12-slim

WORKDIR /app

# Set Python path
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install project dependencies (without root)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --only main --no-root

# Copy application code including README.md
COPY . .

# Install the package
RUN poetry install --no-interaction --only main

EXPOSE 8042

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8042/health || exit 1

RUN chmod +x /app/run_migrations.sh

CMD ["sh", "-c", "alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8042"]