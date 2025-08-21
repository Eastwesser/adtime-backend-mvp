from pydantic import BaseModel

class BalanceResponse(BaseModel):
    """Response schema for user balance"""
    balance: float
    currency: str = "RUB"

    class Config:
        from_attributes = True
        