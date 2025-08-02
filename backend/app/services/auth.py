# Аутентификация, JWT
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.auth import Token
from backend.app.schemas.user import UserCreate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        user = await self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return UserResponse.model_validate(user)  # Convert to response model

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, user: User) -> Token:
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
            settings.JWT_PRIVATE_KEY,  # Updated to use from config
            algorithm=settings.ALGORITHM
        )
        return Token(
            access_token=encoded_jwt,
            token_type="bearer"
        )

    async def register_user(self, user_create: UserCreate) -> UserResponse:
        if await self.user_repo.get_by_email(user_create.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        hashed_password = self.get_password_hash(user_create.password)
        user_dict = user_create.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password

        user = await self.user_repo.create(user_dict, obj_in=user_create)
        return UserResponse.model_validate(user)
