import sys
from os.path import abspath, dirname
from pathlib import Path

# Set up Python path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

print(f"Python paths: {sys.path}")

try:
    from app.models.base import Base
    from app.core.config import settings
except ImportError:
    from backend.app.models.base import Base
    from backend.app.core.config import settings

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Import after path is set
from app.models.base import Base  # Changed from backend.app.models.base
from app.core.config import settings  # Changed from backend.app.core.config

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in 'online' mode with async support."""
    connectable = create_async_engine(
        str(settings.DATABASE_URL),  # Convert to string here
        poolclass=NullPool,  # Disable connection pooling for migrations
        echo=True if settings.DEBUG else False
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
