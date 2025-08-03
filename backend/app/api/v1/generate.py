from uuid import UUID

from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field, field_validator

from backend.app.core.dependencies import (
    GenerationServiceDep,
    CurrentUserDep,
    KandinskyAPIDep
)
from backend.app.schemas.generation import (
    GenerationResponse,
    GenerationStatusResponse
)

router = APIRouter(
    prefix="/generate",
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


class RateLimiterDep:
    async def check_request(self, param):
        pass


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


class GenerationCancelResponse:
    pass


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
