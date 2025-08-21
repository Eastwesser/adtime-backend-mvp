from contextlib import asynccontextmanager
from sqlalchemy import text

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_router
from app.core.config import settings, YooKassaConfig
from app.core.database import init_db, async_session
from app.core.errors import APIError, api_error_handler
from app.core.monitoring import setup_monitoring
from app.core.webhooks import webhook_manager
from app.services.order import handle_order_webhook
from app.core.redis import redis_client 

YooKassaConfig.setup(settings)

# Health check functions
async def check_database_health():
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "disconnected"

# async def check_redis_health():
#     try:
#         redis_client = redis.Redis.from_url(settings.REDIS_URL)
#         await redis_client.ping()
#         await redis_client.close()
#         return "connected"
#     except Exception:
#         return "disconnected"

async def check_redis_health():
    try:
        return "connected" if await redis_client.ping() else "disconnected"
    except Exception:
        return "disconnected"

# Add to lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # Import and register the webhook handler

    webhook_manager.register("order.created")(handle_order_webhook)
    
    yield
    

app = FastAPI(
    title="AdTime API",
    description="API for AdTime image generation and payments",
    version=settings.API_VERSION, 
    lifespan=lifespan,
    contact={
        "name": "Support",
        "email": settings.SUPPORT_EMAIL,
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login and JWT token management"
        },
        {
            "name": "Users",
            "description": "User profile management operations"
        },
        {
            "name": "Generations",
            "description": "AI image generation and status tracking"
        },
        {
            "name": "Marketplace",
            "description": "Browse and purchase advertising designs",
            "externalDocs": {
                "description": "Marketplace guide",
                "url": "https://docs.adtime.com/marketplace"
            }
        },
        {
            "name": "Orders",
            "description": "Order processing and production tracking"
        },
        {
            "name": "Payments",
            "description": "Payment processing via YooKassa"
        },
        {
            "name": "Admin",
            "description": "Administrative operations (requires admin rights)"
        },
        {
            "name": "System",
            "description": "System health checks and monitoring"
        }
    ],
    redoc_url="/documentation",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

# Exception handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, lambda _, exc: JSONResponse(
    status_code=exc.status_code,
    content={"error": {"message": exc.detail, "code": "http_error"}}
))

# Setup monitoring and CORS
setup_monitoring(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "version": settings.API_VERSION}

@app.get("/health", tags=["System"])
async def system_health_check():
    """Overall system health endpoint with real checks"""
    db_status = await check_database_health()
    redis_status = await check_redis_health()
    
    overall_status = "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy"
    
    return {
        "status": overall_status,
        "version": settings.API_VERSION,
        "database": db_status,
        "redis": redis_status
    }
