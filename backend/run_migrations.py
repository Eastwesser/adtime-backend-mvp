import asyncio
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.connect() as connection:
        await connection.run_sync(
            lambda conn: command.upgrade(alembic_cfg, "head")
        )
        await connection.run_sync(
            lambda conn: command.stamp(alembic_cfg, "head")
        )


def main():
    try:
        asyncio.run(run_migrations())
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
