# app/core/v1/users.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    email: str


@router.get(
    "/users/{id}",
    response_model=UserResponse,
    summary="Get User",
    description="Retrieve user details by ID",
    responses={
        200: {"description": "User data"},
        404: {"description": "User not found"},
        403: {"description": "Forbidden (admin only)"}
    },
    tags=["Users"]
)
async def get_user(id: int):
    return {"id": id, "email": "test@test.com"}
