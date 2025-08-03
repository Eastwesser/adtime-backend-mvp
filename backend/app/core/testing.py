from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


def create_mock_session() -> AsyncSession:
    """Создает мок AsyncSession для тестов"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


def create_mock_client(
        app,
        overrides: Dict[Any, Any] = None
) -> TestClient:
    """Создает тестовый клиент с моками зависимостей"""
    if overrides:
        app.dependency_overrides.update(overrides)
    return TestClient(app)


@pytest.fixture
def mock_repo():
    """Фикстура для мока репозитория"""
    repo = MagicMock()
    repo.get = AsyncMock()
    repo.create = AsyncMock()
    return repo


class FakeRedis:
    """Фейковый Redis для тестов"""

    def __init__(self):
        self._data = {}

    async def get(self, key: str) -> str:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: int = None) -> bool:
        self._data[key] = value
        return True
