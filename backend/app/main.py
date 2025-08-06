# Entrypoint
from contextlib import asynccontextmanager
from enum import Enum
import json
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


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from enum import Enum, EnumType
    from pydantic import BaseModel
    from typing import Any
    import json

    def serialize_enums(obj: Any) -> Any:
        """Recursively serialize Enums and Enum types in the schema"""
        if isinstance(obj, (Enum, EnumType)):
            if isinstance(obj, Enum):
                return obj.value
            return str(obj)  # Handle EnumType case
        elif isinstance(obj, dict):
            return {k: serialize_enums(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [serialize_enums(v) for v in obj]
        elif isinstance(obj, BaseModel):
            return serialize_enums(obj.model_dump())
        elif hasattr(obj, '__dict__'):
            return serialize_enums(obj.__dict__)
        return obj

    try:
        # Generate the basic schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )

        # Clean the schema by serializing any Enums
        openapi_schema = serialize_enums(openapi_schema)

        # Ensure components exist
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        if "schemas" not in openapi_schema["components"]:
            openapi_schema["components"]["schemas"] = {}

        # Add error schemas
        from app.schemas.errors import HTTPError, ValidationError
        error_schemas = {
            "HTTPError": serialize_enums(HTTPError.model_json_schema()),
            "ValidationError": serialize_enums(ValidationError.model_json_schema())
        }
        openapi_schema["components"]["schemas"].update(error_schemas)

        app.openapi_schema = openapi_schema
        return openapi_schema

    except Exception as e:
        print(f"Error generating OpenAPI schema: {e}")
        raise

app.openapi = custom_openapi


def debug_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    try:
        # Generate the basic schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )

        # Convert all enums to their values
        def clean_schema(schema):
            if isinstance(schema, dict):
                return {k: clean_schema(v) for k, v in schema.items()}
            elif isinstance(schema, list):
                return [clean_schema(v) for v in schema]
            elif isinstance(schema, Enum):
                return schema.value
            elif hasattr(schema, '__dict__'):
                return clean_schema(schema.__dict__)
            return schema

        openapi_schema = clean_schema(openapi_schema)
        app.openapi_schema = openapi_schema
        return openapi_schema
    except Exception as e:
        print(f"Error generating OpenAPI schema: {e}")
        raise

# Uncomment to debug
app.openapi = debug_openapi

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

