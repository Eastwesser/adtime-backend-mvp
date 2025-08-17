from datetime import timedelta
from uuid import UUID
from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.security import create_access_token
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse

class AdminService:
    """Handles god-mode operations with audit logging"""
    
    def __init__(self, user_repo: UserRepository):
        self.users = user_repo

    async def grant_admin(self, current_user: UserResponse, user_id: UUID) -> None:
        """Grants admin privileges to a user"""
        if not current_user.is_superadmin:
            raise PermissionDeniedError()

        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("User")

        await self.users.update(user_id, {"role": "admin"})

    async def impersonate_user(self, admin_id: UUID, user_id: UUID) -> dict:
        """Generates a temporary token to act as another user (admin-only)."""
        admin = await self.users.get(admin_id)
        if not admin or not admin.is_superadmin:
            raise PermissionDeniedError("Superadmin access required")

        target_user = await self.users.get(user_id)
        if not target_user:
            raise NotFoundError("User")

        # Create a short-lived token (e.g., 5 minutes) with the target user's permissions
        return {
            "token": create_access_token(
                str(target_user.id),
                expires_delta=timedelta(minutes=5),
                role=target_user.role
            ),
            "expires_in": 300,
            "original_admin": str(admin_id)
        }
        