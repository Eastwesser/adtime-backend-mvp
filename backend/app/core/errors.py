from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict

class APIError(HTTPException):
    """Base class for all API errors"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "code": code,
                "details": details
            }
        )
        self.code = code

class NotFoundError(APIError):
    def __init__(self, resource: str):
        super().__init__(
            message=f"{resource} not found",
            code="not_found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class PermissionDeniedError(APIError):
    def __init__(self):
        super().__init__(
            message="Permission denied",
            code="permission_denied",
            status_code=status.HTTP_403_FORBIDDEN
        )

class ValidationError(APIError):
    def __init__(self, errors: Dict[str, Any]):
        super().__init__(
            message="Validation failed",
            code="validation_error",
            details=errors
        )

async def api_error_handler(_, exc: APIError) -> JSONResponse:
    """Global handler for our custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail["message"],
                "code": exc.detail["code"],
                "details": exc.detail.get("details")
            }
        }
    )
