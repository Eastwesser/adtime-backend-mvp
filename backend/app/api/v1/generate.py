from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.app.core.dependencies import (
    GenerationServiceDep,
    CurrentUserDep,
    KandinskyAPIDep
)
from backend.app.schemas.generation import (
    GenerationResponse,
    GenerationStatusResponse
)

router = APIRouter(prefix="/generate", tags=["Generation"])


class GenerationCreate(BaseModel):
    prompt: str = Field(..., example="A cute corgi in a spacesuit")
    model_version: str = Field(default="kandinsky-2.1", example="kandinsky-2.1")


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenerationResponse,
    summary="Create Generation",
    description="Submit new image generation task",
    responses={
        202: {"description": "Generation task accepted"},
        424: {"description": "Generation service unavailable"},
        429: {"description": "Rate limit exceeded"}
    },
    tags=["Generations"]
)
async def create_generation(
        generation_in: GenerationCreate,
        user: CurrentUserDep,
        service: GenerationServiceDep,
        kandinsky_api: KandinskyAPIDep
):
    generation = await service.create_generation(user.id, generation_in)
    if not generation:
        return JSONResponse(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            content={"detail": "Generation service unavailable"}
        )
    return generation


@router.get(
    "/{generation_id}/status",
    response_model=GenerationStatusResponse,
    summary="Check Generation Status",
    description="Get current status of generation task",
    responses={
        200: {"description": "Status information"},
        404: {"description": "Generation not found"}
    },
    tags=["Generations"]
)
async def check_generation_status(
        generation_id: UUID,
        service: GenerationServiceDep
):
    generation = await service.check_generation_status(generation_id)
    if not generation:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Generation not found"}
        )
    return generation
