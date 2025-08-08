from typing import Literal


GENERATION_STATUSES = Literal["pending", "processing", "completed", "failed"]
PAYMENT_STATUSES = Literal["pending", "succeeded", "canceled"]
ORDER_STATUSES = Literal[OrderStatus.CREATED, "paid", "production", "shipped", "completed", "cancelled"]