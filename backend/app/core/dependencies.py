import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.rate_limiter import RateLimiter
from backend.app.core.redis import redis_client
from backend.app.core.websocket_manager import ws_manager, ConnectionManager
from backend.app.repositories.factory import FactoryRepository
from backend.app.repositories.generation import GenerationRepository
from backend.app.repositories.marketplace import MarketplaceRepository
from backend.app.repositories.notification import NotificationRepository
from backend.app.repositories.order import OrderRepository
from backend.app.repositories.payment import PaymentRepository
from backend.app.repositories.subscription import SubscriptionRepository
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserResponse
from backend.app.services.auth import AuthService
from backend.app.services.generation import GenerationService
from backend.app.services.kandinsky import KandinskyAPI
from backend.app.services.marketplace import MarketplaceService
from backend.app.services.notifications import NotificationService
from backend.app.services.order import OrderService
from backend.app.services.payment import PaymentService
from backend.app.services.subscription import SubscriptionService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    return None


def get_ws_manager() -> ConnectionManager:
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
    user = await user_repo.get(session, uuid.UUID(user_id))
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


async def get_order_service(
        session: AsyncSession = Depends(get_db)
) -> OrderService:
    order_repo = OrderRepository(session)
    payment_service = await get_payment_service(session)
    generation_repo = GenerationRepository(session)
    return OrderService(
        session,
        order_repo,
        payment_service,
        generation_repo
    )


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


async def get_rate_limiter():
    return RateLimiter(redis_client, "100/minute")


# Dependency type annotations
AdminDep = Annotated[UserResponse, Depends(get_admin_user)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
MarketplaceServiceDep = Annotated[MarketplaceService, Depends(get_marketplace_service)]
FactoryServiceDep = Annotated[FactoryRepository, Depends(get_factory_service)]
GenerationServiceDep = Annotated[GenerationService, Depends(get_generation_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
SubscriptionServiceDep = Annotated[SubscriptionService, Depends(get_subscription_service)]
KandinskyAPIDep = Annotated[KandinskyAPI, Depends(get_kandinsky_api)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]


def get_user_service():
    return None