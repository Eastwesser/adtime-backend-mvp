from app.schemas.schemas import ValidationErrorResponse
from fastapi import status
from app.schemas.errors import ErrorResponse
from app.core.errors import ValidationError

STANDARD_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ValidationError,
        "description": "Validation Error"
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorResponse,
        "description": "Unauthorized"
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorResponse,
        "description": "Forbidden"
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorResponse,
        "description": "Not Found"
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ValidationErrorResponse,
    },
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "model": ErrorResponse,
        "description": "Rate Limit Exceeded"
    }
}

PRODUCTION_RESPONSES = {
    **STANDARD_RESPONSES,
    status.HTTP_202_ACCEPTED: {
        "description": "Assignment in progress"
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "No available factories"
    }
}
