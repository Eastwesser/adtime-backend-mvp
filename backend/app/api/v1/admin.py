# backend/app/api/v1/admin.py

from uuid import UUID
from app.core.webhooks import WebhookManager
from app.schemas.user import UserResponse
from app.services.admin import AdminService
from fastapi import APIRouter, Depends, BackgroundTasks

from app.core.dependencies import AdminDep, GenerationServiceDep, WebhookManagerDep
from app.schemas.admin import GenerationStatsResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users/{user_id}/grant-admin", responses=STANDARD_RESPONSES)
async def grant_admin_privileges(
    user_id: UUID,
    admin: UserResponse = AdminDep,
    service: AdminService = Depends(AdminServiceDep),
    webhooks: WebhookManager = WebhookManagerDep
):
    """Grant admin privileges to user (HATEOAS example)"""
    await service.grant_admin(admin, user_id)
    await webhooks.trigger(
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
        admin: AdminDep,
        service: GenerationServiceDep
):
    return await service.get_stats()
