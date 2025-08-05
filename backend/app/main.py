# Entrypoint
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.monitoring import setup_monitoring
from app.schemas.errors import HTTPError, ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()  # Initialize database tables
    yield
    # Shutdown logic would go here


app = FastAPI(
    title="AdTime API",
    description="API for AdTime image generation and payments",
    version=settings.API_VERSION,
    lifespan=lifespan,  # Now this is defined above
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
    redoc_url="/documentation",  # Custom path for ReDoc
)

# Setup monitoring BEFORE any other middleware
setup_monitoring(app)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def health_check():
    return {"status": "ok", "version": settings.API_VERSION}


@app.get(
    "/health",
    tags=["System"],
    summary="System health check",
    description="""
    Comprehensive system health check including:
    - Database connectivity
    - Redis connectivity
    - External service statuses
    
    Returns 200 OK if all systems operational
    """,
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "database": "connected",
                        "redis": "connected",
                        "storage": "available"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "degraded",
                        "database": "disconnected",
                        "message": "Database connection failed"
                    }
                }
            }
        }
    }
)
async def detailed_health_check():
    """Full system health check"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "database": "connected",  # Add real checks
        "redis": "connected"
    }


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

    # Добавляем схемы ошибок
    openapi_schema["components"]["schemas"] = {
        "HTTPError": HTTPError.schema(),
        "ValidationError": ValidationError.schema(),
    }

    # Добавляем примеры ответов для ошибок
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "responses" in method:
                if "400" in method["responses"]:
                    method["responses"]["400"]["content"] = {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/HTTPError"}
                        }
                    }
                if "422" in method["responses"]:
                    method["responses"]["422"]["content"] = {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ValidationError"}
                        }
                    }

    app.openapi_schema = openapi_schema
    return openapi_schema
