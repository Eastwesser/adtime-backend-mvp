from typing import Dict, List, Optional, Literal, ClassVar
from pydantic import BaseModel, ConfigDict


# Define status values as string literals
StatusValues = Literal[
    "created", "paid", "production", "shipped", 
    "completed", "cancelled", "pending", "succeeded"
]

OrderStatusValues = Literal["created", "paid", "production", "shipped", "completed", "cancelled"]

# class OrderStatus:
#     """Order status constants"""
#     CREATED: ClassVar[str] = "created"
#     PAID: ClassVar[str] = "paid"
#     PRODUCTION: ClassVar[str] = "production"
#     SHIPPED: ClassVar[str] = "shipped"
#     COMPLETED: ClassVar[str] = "completed"
#     CANCELLED: ClassVar[str] = "cancelled"
#     PENDING: ClassVar[str] = "pending"
#     SUCCEEDED: ClassVar[str] = "succeeded"

OrderStatusValues = Literal["created", "paid", "production", "shipped", "completed", "cancelled"]

# For backward compatibility
class OrderStatus:
    CREATED = "created"
    PAID = "paid"
    PRODUCTION = "production"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderStatusHelper:
    """Helper class for order status operations"""
    
    TRANSITIONS = {
        OrderStatus.CREATED: [OrderStatus.PAID, OrderStatus.CANCELLED],
        OrderStatus.PAID: [OrderStatus.PRODUCTION, OrderStatus.CANCELLED],
        OrderStatus.PRODUCTION: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.COMPLETED]
    }

    # @classmethod
    # def get_transitions(cls) -> Dict[str, List[str]]:
    #     """Returns allowed status transitions"""
    #     return cls.TRANSITIONS

    # @classmethod
    # def validate_transition(cls, current: str, new: str) -> None:
    #     """Validates status transition"""
    #     allowed = cls.TRANSITIONS.get(current, [])
    #     if new not in allowed:
    #         raise ValueError(
    #             f"Invalid transition from {current} to {new}. "
    #             f"Allowed: {allowed}"
    #         )
    @classmethod
    def validate_transition(cls, current: str, new: str) -> None:
        allowed = cls.TRANSITIONS.get(current, [])
        if new not in allowed:
            raise ValueError(f"Invalid transition from {current} to {new}")

class StatusTransition(BaseModel):
    """Pydantic model for status changes"""
    from_status: StatusValues  # Now this will work
    to_status: StatusValues
    reason: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_status": "created",  # Use string literal here
                "to_status": "paid",
                "reason": "Payment received"
            }
        }
    )
    