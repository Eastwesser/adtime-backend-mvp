import asyncio

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine


async def run_migrations():
    engine = create_async_engine("postgresql+asyncpg://postgres:adtime@localhost:5432/adtime")
    async with engine.connect() as connection:
        await connection.run_sync(
            lambda conn: command.upgrade(Config("alembic.ini"), "head")
        )


asyncio.run(run_migrations())
