from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from backend.app.models.subscription import Subscription
from backend.app.repositories.subscription import SubscriptionRepository
from backend.app.schemas.subscription import SubscriptionCreate, SubscriptionResponse


def _get_plan_details(plan: str) -> dict:
    plans = {
        "free": {"remaining_generations": 5},
        "pro": {"remaining_generations": 50},
        "premium": {"remaining_generations": 200}
    }
    return plans.get(plan, plans["free"])


class SubscriptionService:
    def __init__(self, subscription_repo: SubscriptionRepository):
        self.subscription_repo = subscription_repo

    async def get_user_subscription(self, user_id: UUID) -> Optional[SubscriptionResponse]:
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription:
            return None
        return SubscriptionResponse.model_validate(subscription)

    async def create_subscription(
            self,
            user_id: UUID,
            plan: str
    ) -> SubscriptionResponse:
        plan_details = _get_plan_details(plan)
        expires_at = datetime.now() + timedelta(days=30)  # 1 месяц подписки

        subscription_data = {
            "user_id": user_id,
            "plan": plan,
            "expires_at": expires_at,
            **plan_details
        }

        subscription = await self.subscription_repo.create(subscription_data)
        return SubscriptionResponse.model_validate(subscription)

