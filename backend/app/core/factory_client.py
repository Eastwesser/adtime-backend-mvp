from app.models.factory import Factory
from app.models.order import Order
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.errors import APIError

class FactoryAPIClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def submit_order(self, factory: Factory, order: Order) -> dict:
        """Standardized interface for factory communication"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{factory.api_url}/orders",
                    json={
                        "order_id": str(order.id),
                        "specs": order.design_specs,
                        "deadline": order.production_deadline.isoformat()
                    },
                    headers={"Authorization": f"Bearer {factory.api_key}"} if factory.api_key else None
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise APIError(
                message="Factory API communication failed",
                code="factory_api_error",
                details=str(e),
            )
        