# /backend/app/api/v1/__init__.py
from fastapi import APIRouter

from .admin import router as admin_router
from .auth import router as auth_router
from .generate import router as generate_router
from .marketplace import router as marketplace_router
from .payment import router as payment_router
from .users import router as users_router
from .orders import router as orders_router
# NEW (added missing)
from .balance import router as balance_router
from .generation_config import router as generation_config_router
from .feedback import router as feedback_router
from .history import router as history_router
from .upload import router as upload_router
from .production import router as production_router

router = APIRouter()

# Include all routers with their prefixes
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(payment_router, prefix="/payment", tags=["Payment"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(generate_router, prefix="/generate", tags=["Generate"])
router.include_router(marketplace_router, prefix="/marketplace", tags=["Marketplace"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
router.include_router(orders_router, prefix="/orders", tags=["Orders"])
# NEW
router.include_router(balance_router, prefix="/balance", tags=["Balance"])
router.include_router(generation_config_router, prefix="/generation_config", tags=["GenConfig"])
router.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])
router.include_router(history_router, prefix="/history", tags=["History"])
router.include_router(production_router, prefix="/production", tags=["Production"])
router.include_router(upload_router, prefix="/upload", tags=["Upload"])