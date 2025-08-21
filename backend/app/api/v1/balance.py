from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from app.core.dependencies import CurrentUserDep, get_db
from app.repositories.user import UserRepository
from app.schemas.balance import BalanceResponse

router = APIRouter(
    prefix="",
    tags=["Balance"],
)


@router.get("", response_model=BalanceResponse)
async def get_balance(user: CurrentUserDep, db=Depends(get_db)):
    """Получить баланс пользователя"""
    return {"balance": user.balance, "currency": "RUB"}

@router.post("/deposit")
async def deposit_balance(
    amount: Decimal,
    user: CurrentUserDep,
    db=Depends(get_db)
):
    """Пополнить баланс"""
    if amount <= 0:
        raise HTTPException(400, "Сумма должна быть положительной")
    
    user_repo = UserRepository(db)
    await user_repo.update(user.id, {"balance": user.balance + amount})
    return {"new_balance": user.balance + amount}
