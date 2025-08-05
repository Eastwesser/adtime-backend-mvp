# backend/app/api/v1/admin.py

from fastapi import APIRouter

from app.core.dependencies import AdminDep, GenerationServiceDep
from app.schemas.admin import GenerationStatsResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/generations/stats",
    response_model=GenerationStatsResponse,
    summary="Generation Statistics",
    description="Get system-wide generation metrics (Admin only)",
    responses={
        200: {"description": "Statistics data"},
        403: {"description": "Forbidden (requires admin)"}
    }
)
async def generation_stats(
        admin: AdminDep,
        service: GenerationServiceDep
):
    return await service.get_stats()
