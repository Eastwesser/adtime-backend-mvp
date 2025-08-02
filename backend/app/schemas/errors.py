from typing import Optional

from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str
    code: str
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Item not found",
                "code": "not_found",
                "status_code": 404
            }
        }


class ValidationError(HTTPError):
    errors: Optional[list] = None

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Validation failed",
                "code": "invalid_input",
                "status_code": 422,
                "errors": [
                    {
                        "loc": ["body", "price"],
                        "msg": "ensure this value is greater than 0",
                        "type": "value_error.number.not_gt"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    detail: str
    code: str
