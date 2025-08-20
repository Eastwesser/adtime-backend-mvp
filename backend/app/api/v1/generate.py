from uuid import UUID

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.core.dependencies import (
    GenerationServiceDep,
    CurrentUserDep,
    KandinskyAPIDep, RateLimiterDep
)
from app.schemas.generation import (
    GenerationResponse,
    GenerationStatusResponse
)

router = APIRouter(
    # prefix="/generate",
    prefix="",
    tags=["Generations"],
    responses={429: {"description": "Rate limit exceeded"}}
)


class GenerationCreate(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        examples=["A cute corgi in a spacesuit"],
        description="Text prompt for image generation"
    )
    model_version: str = Field(
        default="kandinsky-2.1",
        description="Kandinsky model version"
    )
    width: int = Field(
        default=1024,
        ge=256,
        le=2048,
        description="Image width in pixels"
    )
    height: int = Field(
        default=1024,
        ge=256,
        le=2048,
        description="Image height in pixels"
    )

    @field_validator('model_version')
    def validate_model_version(cls, v):
        allowed_versions = ["kandinsky-2.1", "kandinsky-2.2"]
        if v not in allowed_versions:
            raise ValueError(f"Unsupported model version. Allowed: {allowed_versions}")
        return v


# class RateLimiterDep:
#     """Зависимость для ограничения частоты запросов.
#
#     Использует Redis для хранения счетчиков.
#     """
#
#     def __init__(self, redis_client, rate_limit: str):
#         self.redis = redis_client
#         self.limit, self.period = self._parse_rate_limit(rate_limit)
#
#     async def check_request(self, user_id: str) -> None:
#         """Проверяет, не превышен ли лимит запросов.
#
#         Raises:
#             HTTPException: 429 если лимит превышен
#         """
#         key = f"rate_limit:{user_id}"
#         current = await self.redis.incr(key)
#
#         if current == 1:
#             await self.redis.expire(key, self.period)
#
#         if current > self.limit:
#             raise HTTPException(
#                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#                 detail=f"Rate limit exceeded: {self.limit} per {self.period}sec"
#             )
#
#     def _parse_rate_limit(self, rate_limit: str) -> tuple[int, int]:
#         """Парсит строку вида '10/minute' в (limit, period_seconds)."""
#         try:
#             limit, period = rate_limit.split("/")
#             period_seconds = {
#                 "second": 1,
#                 "minute": 60,
#                 "hour": 3600
#             }[period.lower()]
#             return int(limit), period_seconds
#         except Exception as e:
#             raise ValueError(f"Invalid rate limit format: {rate_limit}") from e
#

@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenerationResponse,
    summary="Create Generation Task",
    description="""
    Submit new image generation task to Kandinsky API.

    Features:
    - Rate limited (10 requests/minute per user)
    - Automatic quota management
    - Async processing with status tracking

    Returns:
    - generation_id: Track task status using this ID
    - estimated_time: Approximate processing time
    """,
    responses={
        202: {"description": "Generation task accepted"},
        402: {"description": "Insufficient quota"},
        429: {"description": "Too many requests"},
        503: {"description": "Kandinsky API unavailable"}
    },
    tags=["Generations"],
)
async def create_generation(
        generation_in: GenerationCreate,
        user: CurrentUserDep,
        service: GenerationServiceDep,
        rate_limiter: RateLimiterDep,
        kandinsky_api: KandinskyAPIDep
):
    await rate_limiter.check_request(str(user.id))

    try:
        generation = await service.create_generation(
            user_id=user.id,
            generation_in=generation_in,
            api_client=kandinsky_api
        )

        if not generation:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Generation service unavailable"
            )

        return generation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{generation_id}/status",
    response_model=GenerationStatusResponse,
    summary="Check Generation Status",
    description="""
    Get current status of generation task.

    Possible statuses:
    - pending: Waiting in queue
    - processing: Generation in progress
    - completed: Successfully generated
    - failed: Generation failed
    - cancelled: Manually cancelled
    """,
    responses={
        200: {"description": "Status information"},
        404: {"description": "Generation not found"}
    },
    tags=["Generations"]
)
async def check_generation_status(
        generation_id: UUID,
        service: GenerationServiceDep,
        kandinsky_api: KandinskyAPIDep
):
    generation = await service.check_generation_status(
        generation_id=generation_id,
        api_client=kandinsky_api
    )

    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )

    return generation


class GenerationCancelResponse(BaseModel):
    """Модель ответа при отмене генерации.

    Attributes:
        success (bool): Флаг успешности операции
        generation_id (UUID): ID отмененной генерации
        refunded (bool): Была ли возвращена квота
    """
    success: bool = Field(
        ...,
        description="Успешно ли выполнена отмена",
        example=True
    )
    generation_id: UUID = Field(
        ...,
        description="ID отмененной генерации",
        example="a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
    )
    refunded: bool = Field(
        ...,
        description="Была ли возвращена квота",
        example=True
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generation_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
                "refunded": True
            }
        }


@router.post(
    "/{generation_id}/cancel",
    response_model=GenerationCancelResponse,
    summary="Cancel Generation",
    description="Cancel pending or processing generation task",
    responses={
        200: {"description": "Cancellation successful"},
        400: {"description": "Cannot cancel completed/failed task"},
        404: {"description": "Generation not found"}
    }
)
async def cancel_generation(
        generation_id: UUID,
        user: CurrentUserDep,
        service: GenerationServiceDep,
        kandinsky_api: KandinskyAPIDep
):
    success = await service.cancel_generation(
        generation_id=generation_id,
        user_id=user.id,
        api_client=kandinsky_api
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or failed generation"
        )

    return {"success": True, "generation_id": generation_id}
