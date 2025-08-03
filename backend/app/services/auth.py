# Аутентификация, JWT
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.auth import Token
from backend.app.schemas.user import UserCreate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Сервис для аутентификации и авторизации пользователей.
    Обрабатывает:
    - Регистрацию новых пользователей
    - Аутентификацию по email/password
    - Генерацию JWT токенов
    - Хеширование паролей
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля и его хеша.

        Args:
            plain_password: Пароль в чистом виде
            hashed_password: Хешированный пароль

        Returns:
            bool: True если пароль верный
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Генерирует хеш пароля.

        Args:
            password: Пароль в чистом виде

        Returns:
            str: Хешированный пароль
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(user: User) -> Token:
        """Создает JWT токен доступа для пользователя.

        Args:
            user: Объект пользователя

        Returns:
            Token: Объект с токеном доступа
        """
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now() + expires_delta

        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_PRIVATE_KEY,
            algorithm=settings.ALGORITHM
        )
        return Token(
            access_token=encoded_jwt,
            token_type="bearer"
        )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Аутентифицирует пользователя по email и паролю.

        Args:
            email: Email пользователя
            password: Пароль пользователя

        Returns:
            Optional[UserResponse]: Данные пользователя или None если аутентификация не удалась
        """
        user = await self.user_repo.get_by_email(email)  # Сессия внутри репозитория
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return UserResponse.model_validate(user)

    async def register_user(self, user_create: UserCreate) -> UserResponse:
        """Регистрирует нового пользователя.

        Args:
            user_create: Данные для регистрации

        Returns:
            UserResponse: Данные зарегистрированного пользователя

        Raises:
            HTTPException: Если email уже занят
        """
        if await self.user_repo.get_by_email(user_create.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        hashed_password = self.get_password_hash(user_create.password)
        user_dict = user_create.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password

        user = await self.user_repo.create(user_dict)
        return UserResponse.model_validate(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        """Обновляет access token по refresh token.

        Args:
            refresh_token: Токен для обновления

        Returns:
            Token: Новая пара токенов

        Raises:
            HTTPException: Если токен невалиден
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_PRIVATE_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_id = payload.get("sub")
            user = await self.user_repo.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return self.create_access_token(user)

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def request_password_reset(self, email: str) -> None:
        """Запрос на сброс пароля. Отправляет email с токеном сброса.

        Args:
            email: Email пользователя для сброса пароля

        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Генерируем токен сброса (действителен 1 час)
        reset_data = {
            "sub": str(user.id),
            "type": "password_reset",
            "exp": datetime.now() + timedelta(hours=1)
        }
        reset_token = jwt.encode(
            reset_data,
            settings.JWT_PRIVATE_KEY,
            algorithm=settings.ALGORITHM
        )

        # В реальном приложении здесь будет отправка email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        print(f"Password reset link: {reset_url}")  # Для отладки

    async def reset_password(self, token: str, new_password: str) -> None:
        """Сброс пароля по токену из email

        Args:
            token: Токен сброса пароля
            new_password: Новый пароль

        Raises:
            HTTPException: Если токен невалиден или истек
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_PRIVATE_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("type") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Обновляем пароль
            hashed_password = self.get_password_hash(new_password)
            await self.user_repo.update(user_id, {"hashed_password": hashed_password})

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
