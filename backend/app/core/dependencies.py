import uuid
from typing import Annotated
from app.repositories.chat import ChatRepository
from fastapi import Request
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.webhooks import WebhookManager
from app.core.database import async_session
from app.core.config import settings
from app.core.rate_limiter import RateLimiter
from app.core.redis import redis_client
from app.core.websocket_manager import ws_manager, ConnectionManager
from app.repositories.factory import FactoryRepository
from app.repositories.generation import GenerationRepository
from app.repositories.marketplace import MarketplaceRepository
from app.repositories.notification import NotificationRepository
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.services.generation import GenerationService
from app.services.kandinsky import KandinskyAPI
from app.services.marketplace import MarketplaceService
from app.services.notifications import NotificationService
from app.services.order import OrderService
from app.services.payment import PaymentService
from app.services.subscription import SubscriptionService
from app.services.admin import AdminService
from app.services.storage import StorageService
from app.services.production import ProductionService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_db() -> AsyncSession:
    """Генератор сессий базы данных для Dependency Injection.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy

    Ensures:
        Сессия будет закрыта после использования
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_ws_manager() -> ConnectionManager:
    """Возвращает глобальный менеджер WebSocket соединений.

    Returns:
        ConnectionManager: Экземпляр менеджера соединений
    """
    return ws_manager


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get(uuid.UUID(user_id), include_deleted=False)
    if user is None:
        raise credentials_exception
    return UserResponse.model_validate(user)


CurrentUserDep = Annotated[UserResponse, Depends(get_current_user)]


async def get_factory_service(
        session: AsyncSession = Depends(get_db)
) -> FactoryRepository:
    return FactoryRepository(session)


async def get_payment_service(
        session: AsyncSession = Depends(get_db)
) -> PaymentService:
    payment_repo = PaymentRepository(session)
    return PaymentService(payment_repo)


async def get_auth_service(
        session: AsyncSession = Depends(get_db)
) -> AuthService:
    user_repo = UserRepository(session)
    return AuthService(user_repo)


async def get_generation_service(
        session: AsyncSession = Depends(get_db)
) -> GenerationService:
    generation_repo = GenerationRepository(session)
    subscription_repo = SubscriptionRepository(session)
    kandinsky_api = KandinskyAPI(
        settings.KANDINSKY_API_KEY,
        settings.KANDINSKY_SECRET_KEY
    )
    return GenerationService(
        generation_repo,
        subscription_repo,
        kandinsky_api
    )

async def get_chat_repo(session: AsyncSession = Depends(get_db)) -> ChatRepository:
    return ChatRepository(session)

async def get_order_repo(session: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(session)

async def get_generation_repo(session: AsyncSession = Depends(get_db)) -> GenerationRepository:
    return GenerationRepository(session)

async def get_order_service(
    session: AsyncSession = Depends(get_db),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    order_repo: OrderRepository = Depends(get_order_repo),
    payment_service: PaymentService = Depends(get_payment_service),
    generation_repo: GenerationRepository = Depends(get_generation_repo)
) -> OrderService:
    return OrderService(
        session=session,
        chat_repo=chat_repo,
        order_repo=order_repo,
        payment_service=payment_service,
        generation_repo=generation_repo,
    )

OrderServiceDep = Depends(get_order_service)

async def get_subscription_service(
        session: AsyncSession = Depends(get_db)
) -> SubscriptionService:
    subscription_repo = SubscriptionRepository(session)
    return SubscriptionService(subscription_repo)


async def get_kandinsky_api() -> KandinskyAPI:
    return KandinskyAPI(
        api_key=settings.KANDINSKY_API_KEY,
        secret_key=settings.KANDINSKY_SECRET_KEY
    )


async def get_admin_user(user: UserResponse = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def get_notification_service(
        session: AsyncSession = Depends(get_db)
) -> NotificationService:
    notification_repo = NotificationRepository(session)
    return NotificationService(notification_repo)


async def get_marketplace_service(
        session: AsyncSession = Depends(get_db)
) -> MarketplaceService:
    marketplace_repo = MarketplaceRepository(
        session,
        await get_payment_service(session),
        await get_notification_service(session)
    )
    user_repo = UserRepository(session)
    return MarketplaceService(marketplace_repo, user_repo)

async def get_rate_limiter(request: Request) -> RateLimiter:
    """Dependency that checks rate limits"""
    limiter = RateLimiter(
        redis=redis_client,
        key=f"rate_limit:{request.client.host}",  # Or use user_id if authenticated
        limit="100/minute"
    )
    await limiter.check()
    return limiter

async def get_webhook_manager() -> WebhookManager:
    return WebhookManager()

async def get_admin_service(session: AsyncSession = Depends(get_db)) -> AdminService:
    user_repo = UserRepository(session)
    return AdminService(user_repo)


# Dependency type annotations
AdminDep = Annotated[UserResponse, Depends(get_admin_user)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
MarketplaceServiceDep = Annotated[MarketplaceService, Depends(get_marketplace_service)]
FactoryServiceDep = Annotated[FactoryRepository, Depends(get_factory_service)]
GenerationServiceDep = Annotated[GenerationService, Depends(get_generation_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
SubscriptionServiceDep = Annotated[SubscriptionService, Depends(get_subscription_service)]
KandinskyAPIDep = Annotated[KandinskyAPI, Depends(get_kandinsky_api)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]
WebhookManagerDep = Annotated[WebhookManager, Depends(get_webhook_manager)]

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def get_user_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Fetch user data with sensitive fields filtered out."""
        user = await self.repo.get(user_id)
        if not user:
            raise NotFoundError("User")
        return UserResponse.model_validate(user)

    async def update_profile(self, user_id: uuid.UUID, data: dict) -> UserResponse:
        """Update user profile (e.g., name, avatar)."""
        # Add validation/logic here
        await self.repo.update(user_id, data)
        return await self.get_user_profile(user_id)


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    user_repo = UserRepository(session)
    return UserService(user_repo)

async def get_storage_service() -> StorageService:
    return StorageService()

StorageDep = Annotated[StorageService, Depends(get_storage_service)]

async def get_production_service(
    session: AsyncSession = Depends(get_db)
) -> ProductionService:
    return ProductionService(session)

ProductionServiceDep = Annotated[ProductionService, Depends(get_production_service)]
