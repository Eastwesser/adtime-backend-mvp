from app.schemas.order import OrderCreate, OrderResponse
from pydantic import ValidationError
import pytest

def test_order_links():
    order = OrderResponse(
        id="a1b2c3d4-5678-9012-3456-789012345678",
        status="created",
        factory_id="b2c3d4e5-6789-0123-4567-890123456789",
        # ... other required fields ...
    )
    
    assert "/orders/a1b2c3d4-5678-9012-3456-789012345678" in order.links["self"]["href"]
    assert "pay" in order.links  # Verify action link exists for "created" status