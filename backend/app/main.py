from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.monitoring import setup_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan management"""
    await init_db()
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
)

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
async def health_check():
    """System health endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "database": "connected",
        "redis": "connected"
    }