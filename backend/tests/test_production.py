# tests/test_production.py
from unittest.mock import MagicMock
from uuid import uuid4
import pytest


@pytest.mark.asyncio
async def test_assign_order_success(mock_db_session):
    from app.services.production import ProductionService
    
    # Setup mock returns
    mock_order = MagicMock()
    mock_order.design_specs = {"product_type": "poster"}
    mock_factory = MagicMock()
    mock_factory.current_load = 0
    mock_factory.production_capacity = 10
    
    # Mock repository methods
    order_repo = MagicMock()
    order_repo.get = AsyncMock(return_value=mock_order)
    factory_repo = MagicMock()
    factory_repo.find_by_specialization = AsyncMock(return_value=[mock_factory])
    
    service = ProductionService(mock_db_session, order_repo, factory_repo)
    
    # Test
    result = await service.assign_to_factory(uuid4())
    assert result.status == "production"

@pytest.mark.asyncio
async def test_factory_notification(mock_db_session):
    from app.core.factory_client import FactoryAPIClient
    from unittest.mock import patch
    
    client = FactoryAPIClient()
    factory = MagicMock(api_url="http://test.com", api_key="test")
    order = MagicMock(id=uuid4(), design_specs={}, production_deadline=None)
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {})
        await client.submit_order(factory, order)
        mock_post.assert_called_once()   
