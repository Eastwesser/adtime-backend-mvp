import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    PRODUCTION = "production"
    SHIPPED = "shipped"
    COMPLETED = "completed"


class OrderCreate(BaseModel):
    generation_id: Optional[uuid.UUID] = None
    design_specs: Dict = Field(..., description="Параметры дизайна в JSON")


class OrderResponse(OrderCreate):
    id: uuid.UUID
    status: OrderStatus
    amount: float
    created_at: datetime
    production_deadline: Optional[datetime]
    production_errors: Optional[List[str]]
    user_id: uuid.UUID

    class Config:
        from_attributes = True
