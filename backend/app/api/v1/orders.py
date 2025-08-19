from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import (
    CurrentUserDep,
    OrderServiceDep,
    get_db
)
from app.schemas.order import OrderResponse
from app.services.order import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "",
    response_model=list[OrderResponse],
    summary="Get User Orders",
    description="Get list of all orders for current user with optional filtering",
    responses={
        200: {"description": "List of user orders"},
        401: {"description": "Unauthorized"}
    }
)
async def list_orders(
    user: CurrentUserDep,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    service: OrderService = Depends(OrderServiceDep)
):
    """Get paginated list of user orders with optional status filter"""
    return await service.get_user_orders(
        user_id=user.id,
        status=status,
        limit=limit,
        offset=offset
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get Order Details",
    description="Get detailed order information including chat messages",
    responses={
        200: {"description": "Order details"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"}
    }
)
async def get_order(
    order_id: UUID,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Get detailed order information"""
    order = await service.get_order(order_id)
    
    # Check ownership
    if order.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this order is denied"
        )
    
    return order
