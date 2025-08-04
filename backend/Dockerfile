FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first
COPY pyproject.toml poetry.lock README.md ./

# Install dependencies only (no root package)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --only main --no-root

# Copy the rest of the application
COPY . .

# Create symlink for imports to work
RUN ln -s /app /backend

# Set PYTHONPATH
ENV PYTHONPATH=/app:/backend

EXPOSE 8042

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8042/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8042"]