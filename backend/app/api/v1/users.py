from backend.app.services.user import UserService
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from backend.app.core.dependencies import (
    CurrentUserDep,
    AdminDep,
    get_user_service
)
from backend.app.schemas.user import (
    UserResponse,
    UserUpdate
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    responses={
        200: {"description": "User data"},
        401: {"description": "Unauthorized"}
    }
)
async def get_current_user(
        user: CurrentUserDep,
        service: UserService = Depends(get_user_service)
):
    return user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Admin only endpoint",
    responses={
        200: {"description": "User data"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"}
    }
)
async def get_user(
        user_id: UUID4,
        admin: AdminDep,
        service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update Current User",
    responses={
        200: {"description": "User updated"},
        400: {"description": "Validation error"}
    }
)
async def update_user(
        update_data: UserUpdate,
        user: CurrentUserDep,
        service: UserService = Depends(get_user_service)
):
    try:
        return await service.update_user(user.id, update_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)

        )
