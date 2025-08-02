import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan = SubscriptionPlan.FREE


class SubscriptionResponse(SubscriptionCreate):
    id: uuid.UUID
    expires_at: datetime
    remaining_generations: int
    user_id: uuid.UUID

    class Config:
        from_attributes = True
