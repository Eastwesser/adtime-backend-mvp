from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с пользователями.

    Основная функциональность:
    - Стандартные CRUD операции
    - Поиск по email/имени
    - Управление метаданными пользователя (last_login и т.д.)

    Безопасность:
    - Не включает методы для работы с паролями (это в AuthService)
    - Все чувствительные данные исключены из базовых методов

    Особенности:
    - Поддержка поиска по различным критериям
    - Оптимизированные запросы для часто используемых операций
    - Логирование критичных операций

    Интеграции:
    - Основной репозиторий для AuthService
    - Используется практически во всех сервисах
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)  # Сессия сохраняется в базовом классе

    async def get_by_email(
            self,
            email: str,
    ) -> Optional[User]:
        """Находит пользователя по email. Использует внутреннюю сессию."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram(self, session: AsyncSession, tg_id: str) -> Optional[User]:
        """Находит пользователя по Telegram ID. Использует внутреннюю сессию."""
        result = await session.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def update_last_login(self, user_id: UUID) -> None:
        """Обновляет время последнего входа"""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now())
        )
        await self.session.commit()

    async def search(
            self,
            query: str,
            limit: int = 10
    ) -> Sequence[User]:
        """Поиск пользователей по email или имени"""
        stmt = (
            select(User)
            .where(
                or_(
                    User.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%")
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
