from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from backend.app.core.dependencies import (
    CurrentUserDep,
    MarketplaceServiceDep,
    PaymentServiceDep
)
from backend.app.schemas.marketplace import (
    CartItemAdd,
    DirectOrderResponse
)
from backend.app.schemas.marketplace import MarketItem, MarketFilters

router = APIRouter(
    prefix="/marketplace",
    tags=["Marketplace"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/items",
    response_model=list[MarketItem],
    summary="Browse marketplace items",
    description="""
    Get a list of available advertising designs in the marketplace.
    
    ### Filters:
    - Filter by type (banner, standee, etc.)
    - Price range filtering
    - Minimum rating
    - Search by title
    """,
    responses={
        200: {"description": "List of marketplace items"},
        400: {"description": "Invalid filter parameters"}
    }
)
async def list_market_items(
        filters: MarketFilters,
        service: MarketplaceServiceDep
):
    """Get filtered marketplace items"""
    try:
        return await service.get_items(filters)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/items/{item_id}/cart",
    summary="Add item to cart",
    description="""
    Add a marketplace item to your shopping cart.
    
    ### Parameters:
    - item_id: UUID of the marketplace item
    - quantity: Number of items to add (default: 1)
    """,
    responses={
        200: {"description": "Item added to cart"},
        404: {"description": "Item not found"},
        400: {"description": "Invalid quantity"}
    }
)
async def add_to_cart(
        service: MarketplaceServiceDep,
        user: CurrentUserDep,
        item_id: UUID,
        quantity: int = 1,
):
    """Add item to user's cart"""
    try:
        return await service.add_to_cart(user.id, item_id, quantity)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )


@router.post(
    "/items/{item_id}/order",
    summary="Create direct order",
    description="""
    Create an order directly from a marketplace item (bypassing cart).
    
    Automatically:
    - Creates payment
    - Assigns to production factory
    - Tracks order status
    """,
    responses={
        201: {
            "description": "Order created",
            "content": {
                "application/json": {
                    "example": {"order_id": "uuid", "status": "created"}
                }
            }
        },
        402: {"description": "Payment required"},
        404: {"description": "Item not found"}
    }
)
async def create_direct_order(
        item_id: UUID,
        user: CurrentUserDep,
        service: MarketplaceServiceDep,
        payment_service: PaymentServiceDep
):
    """Create order directly from marketplace item"""
    try:
        order = await service.create_order_from_item(user.id, item_id)
        payment = await payment_service.create_payment(
            order_id=order.id,
            amount=order.amount,
            description=f"Order for {item_id}"
        )
        return {
            "order_id": order.id,
            "status": "created",
            "payment_id": payment.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )


@router.post(
    "/cart/items",
    summary="Add to Cart",
    description="Add item to user's shopping cart",
    responses={
        200: {"description": "Item added"},
        400: {"description": "Invalid quantity"},
        404: {"description": "Item not found"}
    }
)
async def add_to_cart(
        item: CartItemAdd,
        user: CurrentUserDep,
        service: MarketplaceServiceDep
):
    try:
        return await service.add_to_cart(
            user_id=user.id,
            item_id=item.item_id,
            quantity=item.quantity
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/orders/direct",
    response_model=DirectOrderResponse,
    summary="Create Direct Order",
    description="""
    Create order directly from item (without cart).

    Steps:
    1. Creates order
    2. Processes payment
    3. Assigns to production
    """,
    responses={
        201: {"description": "Order created"},
        402: {"description": "Payment required"},
        404: {"description": "Item not found"}
    }
)
async def create_direct_order(
        item_id: UUID4,
        user: CurrentUserDep,
        service: MarketplaceServiceDep
):
    try:
        return await service.create_order_from_item(user.id, item_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
