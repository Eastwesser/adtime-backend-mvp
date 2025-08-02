# /backend/app/api/v1/__init__.py
from fastapi import APIRouter

from .admin import router as admin_router
from .auth import router as auth_router
from .generate import router as generate_router
from .marketplace import router as marketplace_router
from .payment import router as payment_router
from .users import router as users_router

router = APIRouter()

# Include all routers with their prefixes
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(payment_router, prefix="/payment", tags=["Payment"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(generate_router, prefix="/generate", tags=["Generate"])
router.include_router(marketplace_router, prefix="/marketplace", tags=["Marketplace"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
