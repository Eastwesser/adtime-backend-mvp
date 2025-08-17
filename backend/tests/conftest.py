import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base

@pytest.fixture
def mock_db_session():
    """Mock database session with commit/rollback"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    return session

@pytest.fixture
def mock_payment_gateway():
    """Mock payment gateway responses"""
    gateway = AsyncMock()
    gateway.create_payment.return_value = {
        "id": "mock_payment_id",
        "status": "pending"
    }
    return gateway

@pytest.fixture
def client():
    """Test client with overridden dependencies"""
    return TestClient(app)