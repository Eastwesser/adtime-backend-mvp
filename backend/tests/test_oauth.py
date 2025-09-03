import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
@patch('app.services.auth.oauth_services')
async def test_oauth_flow(mock_oauth_service):
    # Mock the external OAuth service
    mock_user_data = {
        "email": "test@example.com",
        "id": "oauth123",
        "name": "Test User"
    }
    mock_oauth_service.get_oauth_user.return_value = mock_user_data
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test OAuth initiation
        response = await ac.get("/api/v1/oauth/google/init")
        assert response.status_code == 200
        
        # Test OAuth callback
        response = await ac.get("/api/v1/oauth/google/callback?code=test_code")
        assert response.status_code == 200
        assert "token" in response.json()