from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)  # Сессия сохраняется в базовом классе

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Находит пользователя по email. Использует внутреннюю сессию."""
        result = await session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram(self, session: AsyncSession, tg_id: str) -> Optional[User]:
        """Находит пользователя по Telegram ID. Использует внутреннюю сессию."""
        result = await session.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        return result.scalar_one_or_none()
