from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Payment as YooPayment

from app.core.dependencies import PaymentServiceDep
from app.core.dependencies import (
    get_db
)
from app.schemas.payment import PaymentResponse

router = APIRouter(
    # prefix="/payments",
    prefix="",
    tags=["Payments"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "/create",
    response_model=PaymentResponse,
    summary="Create Payment",
    description="""
    Creates a new payment for an order.

    Process:
    1. Validates order exists
    2. Creates payment in YooKassa
    3. Saves payment reference in DB
    """,
    responses={
        201: {"description": "Payment created"},
        400: {"description": "Invalid request"},
        402: {"description": "Payment failed"}
    }
)
async def create_payment(
        service: PaymentServiceDep,
        order_id: UUID,
        amount: float,
        description: str = "Order payment",
        session: AsyncSession = Depends(get_db)
):
    amount_kopecks = round(amount * 100)
    payment = await service.create_payment(
        session=session,
        order_id=order_id,
        amount=amount,
        description=description
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment creation failed"
        )
    return payment


@router.get(
    "/{payment_id}/status",
    response_model=PaymentResponse,
    summary="Check Payment Status",
    responses={
        200: {"description": "Payment status"},
        404: {"description": "Payment not found"}
    }
)
async def check_payment_status(
        service: PaymentServiceDep,
        payment_id: UUID,
        session: AsyncSession = Depends(get_db)
) -> Optional[PaymentResponse]:
    payment = await service.check_payment_status(session, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.post(
    "/webhook",
    summary="Payment Webhook",
    responses={
        200: {"description": "Webhook processed"},
        400: {"description": "Invalid webhook data"}
    },
    include_in_schema=False
)
async def handle_webhook(
        service: PaymentServiceDep,
        notification: dict,
        session: AsyncSession = Depends(get_db)
):
    result = await service.handle_webhook(session, notification)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )
    return result


@router.get(
    "/{payment_id}/redirect",
    summary="Payment Redirect",
    responses={
        307: {"description": "Redirecting to payment"},
        404: {"description": "Payment not found"},
        400: {"description": "Payment already processed"}
    }
)
async def redirect_to_payment(
        service: PaymentServiceDep,
        payment_id: UUID,
        session: AsyncSession = Depends(get_db)
):
    payment = await service.check_payment_status(session, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already processed"
        )

    # Получаем URL для редиректа из ЮKassa
    yoo_payment = YooPayment.find_one(payment.external_id)
    return RedirectResponse(url=yoo_payment.confirmation.confirmation_url)
