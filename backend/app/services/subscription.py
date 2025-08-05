from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.repositories.subscription import SubscriptionRepository
from app.schemas.subscription import SubscriptionResponse


def _get_plan_details(plan: str) -> dict:
    plans = {
        "free": {"remaining_generations": 5},
        "pro": {"remaining_generations": 50},
        "premium": {"remaining_generations": 200}
    }
    return plans.get(plan, plans["free"])


class SubscriptionService:
    """
    Сервис управления подписками пользователей.
    Основные функции:
    - Активация/продление подписок
    - Управление квотами
    - Обработка платежей за подписки
    """

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

    async def upgrade_subscription(
            self,
            user_id: UUID,
            new_plan: str
    ) -> SubscriptionResponse:
        """Обновление тарифного плана подписки

        Args:
            user_id: UUID пользователя
            new_plan: Новый тарифный план (free/pro/premium)

        Returns:
            SubscriptionResponse: Обновленная подписка

        Raises:
            ValueError: Если план невалиден
        """
        valid_plans = ["free", "pro", "premium"]
        if new_plan not in valid_plans:
            raise ValueError(f"Invalid plan. Allowed: {valid_plans}")

        # Получаем текущую подписку
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription:
            return await self.create_subscription(user_id, new_plan)

        # Обновляем план
        plan_details = _get_plan_details(new_plan)
        updates = {
            "plan": new_plan,
            **plan_details
        }

        # Если это апгрейд - продлеваем подписку
        if new_plan != "free" and subscription.plan == "free":
            updates["expires_at"] = datetime.now() + timedelta(days=30)

        updated_sub = await self.subscription_repo.update(subscription.id, updates)
        return SubscriptionResponse.model_validate(updated_sub)

    async def cancel_subscription(self, user_id: UUID) -> bool:
        """Отмена подписки пользователя (перевод на free тариф)

        Args:
            user_id: UUID пользователя

        Returns:
            bool: True если отмена успешна
        """
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription or subscription.plan == "free":
            return False

        # Устанавливаем free тариф
        plan_details = _get_plan_details("free")
        await self.subscription_repo.update(
            subscription.id,
            {
                "plan": "free",
                **plan_details
            }
        )
        return True
