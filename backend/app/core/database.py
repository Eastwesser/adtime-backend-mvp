from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# Базовый класс для моделей (альтернатива отдельному base.py)
Base = declarative_base()

# Асинхронный движок
engine = create_async_engine(
    str(settings.DATABASE_URL), 
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    echo=settings.DB_ECHO,
)

# Фабрика сессий
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncSession:
    """Генератор сессий для Dependency Injection"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Создание таблиц (для тестов и начальной настройки)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
