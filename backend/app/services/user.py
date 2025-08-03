import uuid
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db
from app.repositories import UserRepository
from app.schemas import UserResponse


class UserService:
    """Сервис для работы с пользователями системы.

    Обеспечивает:
    - Получение информации о пользователях
    - Обновление профилей
    - Управление ролями (для админов)
    - Работу с подписками пользователей
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: uuid.UUID) -> Optional[UserResponse]:
        """Получить пользователя по ID.

        Args:
            user_id: UUID пользователя

        Returns:
            UserResponse или None если не найден
        """
        user = await self.user_repo.get(user_id)
        return UserResponse.model_validate(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Получить пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            UserResponse или None если не найден
        """
        user = await self.user_repo.get_by_email(email)
        return UserResponse.model_validate(user) if user else None

    async def update_user(
            self,
            user_id: uuid.UUID,
            update_data: dict,
            current_user: UserResponse
    ) -> UserResponse:
        """Обновить данные пользователя.

        Args:
            user_id: UUID обновляемого пользователя
            update_data: Данные для обновления
            current_user: Текущий аутентифицированный пользователь

        Returns:
            Обновленные данные пользователя

        Raises:
            HTTPException 403: Если попытка изменить не свой профиль без прав админа
            HTTPException 404: Если пользователь не найден
        """
        # Проверка прав
        if str(user_id) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update another user's profile"
            )

        user = await self.user_repo.update(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.model_validate(user)

    async def search_users(self, query: str, limit: int = 10) -> list[UserResponse]:
        """Поиск пользователей по email или имени.

        Args:
            query: Строка поиска
            limit: Максимальное количество результатов

        Returns:
            Список найденных пользователей
        """
        users = await self.user_repo.search(query, limit)
        return [UserResponse.model_validate(u) for u in users]

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Обновить время последнего входа пользователя.

        Args:
            user_id: UUID пользователя
        """
        await self.user_repo.update_last_login(user_id)


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    """Фабрика для Dependency Injection UserService.

    Args:
        session: Асинхронная сессия SQLAlchemy

    Returns:
        Экземпляр UserService
    """
    user_repo = UserRepository(session)
    return UserService(user_repo)
