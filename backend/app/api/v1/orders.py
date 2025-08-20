from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import (
    CurrentUserDep,
    OrderServiceDep,
)
from app.schemas.order import OrderResponse, OrderCreate, OrderUpdate, ChatMessageSchema, ChatMessageCreate
from app.services.order import OrderService

router = APIRouter(
    # prefix="/orders",
    prefix="",
    tags=["Orders"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "",
    response_model=OrderResponse,
    summary="Create New Order",
    description="Create a new design order with payment",
    responses={
        201: {"description": "Order created successfully"},
        400: {"description": "Invalid order data"},
        401: {"description": "Unauthorized"}
    }
)
async def create_order(
    order_data: OrderCreate,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Create a new order with payment"""
    result = await service.create_order_with_payment(user.id, order_data)
    return result["order"]

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
    description="Get detailed order information",
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

@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update Order",
    description="Update order information",
    responses={
        200: {"description": "Order updated"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"}
    }
)
async def update_order(
    order_id: UUID,
    update_data: OrderUpdate,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Update order information"""
    return await service.update_order(order_id, update_data, user.id)

@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Order",
    description="Delete an order (only CREATED or CANCELLED orders can be deleted)",
    responses={
        204: {"description": "Order deleted"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
        400: {"description": "Cannot delete order in current status"}
    }
)
async def delete_order(
    order_id: UUID,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Delete an order"""
    await service.delete_order(order_id, user.id)

@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel Order",
    description="Cancel an order with optional reason",
    responses={
        200: {"description": "Order cancelled"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"},
        400: {"description": "Cannot cancel order in current status"}
    }
)
async def cancel_order(
    order_id: UUID,
    user: CurrentUserDep,  # ← THIS FIRST (no default)
    reason: str = None,    # ← THEN this (has default)
    service: OrderService = Depends(OrderServiceDep)
):
    """Cancel an order"""
    return await service.cancel_order(order_id, user.id, reason)

# Chat endpoints
@router.post(
    "/{order_id}/messages",
    response_model=ChatMessageSchema,
    summary="Add Message to Order Chat",
    description="Add a message to the order's chat",
    responses={
        201: {"description": "Message added"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"}
    }
)
async def add_order_message(
    order_id: UUID,
    message_data: ChatMessageCreate,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Add a message to order chat"""
    return await service.add_order_message(
        order_id, user.id, message_data.message, message_data.attachments
    )

@router.get(
    "/{order_id}/messages",
    response_model=list[ChatMessageSchema],
    summary="Get Order Messages",
    description="Get all messages from order chat",
    responses={
        200: {"description": "List of messages"},
        403: {"description": "Access denied"},
        404: {"description": "Order not found"}
    }
)
async def get_order_messages(
    order_id: UUID,
    user: CurrentUserDep,
    service: OrderService = Depends(OrderServiceDep)
):
    """Get order chat messages"""
    return await service.get_order_messages(order_id)
