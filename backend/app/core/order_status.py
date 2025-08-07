from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict

# Define status values as string literals
StatusValues = Literal["created", "paid", "production", "shipped", "completed", "cancelled"]

class OrderStatusHelper:
    """Helper class for order status operations"""
    
    TRANSITIONS = {
        "created": ["paid", "cancelled"],
        "paid": ["production", "cancelled"],
        "production": ["shipped", "cancelled"],
        "shipped": ["completed"]
    }

    @classmethod
    def get_transitions(cls) -> Dict[str, List[str]]:
        """Returns allowed status transitions"""
        return cls.TRANSITIONS

    @classmethod
    def validate_transition(cls, current: str, new: str) -> None:
        """Validates status transition"""
        allowed = cls.TRANSITIONS.get(current, [])
        if new not in allowed:
            raise ValueError(
                f"Invalid transition from {current} to {new}. "
                f"Allowed: {allowed}"
            )


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