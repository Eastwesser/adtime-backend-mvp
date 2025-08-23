# Stage 1: Builder
FROM python:3.12-slim AS builder

ARG POETRY_VERSION=1.7.1
ARG POETRY_HOME=/opt/poetry

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.in-project true

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

# Create non-root user
RUN groupadd -r app --gid 1000 && \
    useradd -r -g app --uid 1000 --shell /bin/bash --create-home app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /app/.venv ./.venv

# Copy application code
COPY --chown=app:app . .

# Set proper permissions
RUN chown -R app:app /app && \
    find /app -name "*.py" -exec chmod 644 {} \; && \
    find /app -name "*.sh" -exec chmod 755 {} \; && \
    chmod 755 /app && \
    mkdir -p /app/uploads && \
    chown app:app /app/uploads && \
    chmod 755 /app/uploads

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED="1" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONPYCACHEPREFIX="/tmp/pycache" \
    UVICORN_HOST="0.0.0.0" \
    UVICORN_PORT="8042" \
    UVICORN_ACCESS_LOG="false" \
    UVICORN_LOG_LEVEL="warning"

# Switch to non-root user
USER app

# Expose port
EXPOSE 8042

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8042/health || exit 1

# Run application
CMD ["sh", "-c", \
    "alembic upgrade head && \
    uvicorn app.main:app \
    --host ${UVICORN_HOST} \
    --port ${UVICORN_PORT} \
    --no-server-header \
    --no-access-log \
    --log-level ${UVICORN_LOG_LEVEL}"]