# backend/app/api/v1/admin.py
from uuid import UUID
from fastapi import APIRouter, Depends, status, BackgroundTasks
from app.schemas.user import UserResponse
from app.schemas.admin import GenerationStatsResponse
from app.core.webhooks import webhook_manager
from app.core.dependencies import (
    AdminDep,
    GenerationServiceDep,
    AdminServiceDep
)
from app.services.admin import AdminService
from app.services.generation import GenerationService

router = APIRouter(prefix="/admin", tags=["Admin"])

STANDARD_RESPONSES = {
    status.HTTP_200_OK: {"description": "Success"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
}

@router.post("/users/{user_id}/grant-admin", responses=STANDARD_RESPONSES)
async def grant_admin_privileges(
    user_id: UUID,
    background_tasks: BackgroundTasks,
    admin: UserResponse = Depends(AdminDep),
    service: AdminService = Depends(AdminServiceDep),
):
    """Grant admin privileges to user (HATEOAS example)"""
    await service.grant_admin(admin, user_id)
    background_tasks.add_task(
        webhook_manager.trigger,
        "admin.granted",
        {"admin_id": str(admin.id), "user_id": str(user_id)}
    )
    return {
        "status": "success",
        "links": {
            "user": {"href": f"/users/{user_id}", "method": "GET"}
        }
    }

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
    admin: UserResponse = Depends(AdminDep),
    service: GenerationService = Depends(GenerationServiceDep),
):
    return await service.get_stats()
