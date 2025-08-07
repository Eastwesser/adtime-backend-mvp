from enum import Enum
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict

class OrderStatus(str, Enum):
    """Centralized order status enumeration"""
    CREATED = "created"
    PAID = "paid"
    PRODUCTION = "production"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def get_transitions(cls) -> Dict[str, List[str]]:
        """Returns allowed status transitions using string values"""
        return {
            cls.CREATED.value: [cls.PAID.value, cls.CANCELLED.value],
            cls.PAID.value: [cls.PRODUCTION.value, cls.CANCELLED.value],
            cls.PRODUCTION.value: [cls.SHIPPED.value, cls.CANCELLED.value],
            cls.SHIPPED.value: [cls.COMPLETED.value],
        }

    @classmethod
    def validate_transition(cls, current: str, new: str) -> None:
        """Validates status transition using string values"""
        allowed = cls.get_transitions().get(current, [])
        if new not in allowed:
            raise ValueError(
                f"Invalid transition from {current} to {new}. "
                f"Allowed: {allowed}"
            )

StatusValues = Literal["created", "paid", "production", "shipped", "completed", "cancelled"]

class StatusTransition(BaseModel):
    """Model for status transition"""
    from_status: StatusValues
    to_status: StatusValues
    reason: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_status": "created",
                "to_status": "paid",
                "reason": "Customer made payment"
            }
        }
    )
    