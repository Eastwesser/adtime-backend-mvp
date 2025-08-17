from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.services.production import ProductionService
from app.core.dependencies import get_db, ProductionServiceDep

router = APIRouter(prefix="/production", tags=["Production"])

@router.post("/orders/{order_id}/assign")
async def assign_order(
    order_id: UUID,
    factory_id: Optional[UUID] = None,
    service: ProductionService = Depends(ProductionServiceDep)
):
    """
    Assigns order to factory (RESTful design)
    POST /production/orders/{order_id}/assign
    """
    return await service.assign_to_factory(order_id, factory_id)

@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    status: str,
    notes: Optional[str] = None,
    service: ProductionService = Depends(ProductionServiceDep)
):
    """
    Updates production status (RESTful partial update)
    PATCH /production/orders/{order_id}/status
    """
    return await service.update_production_status(order_id, status, notes)
