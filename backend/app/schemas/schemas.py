from pydantic import BaseModel

class ErrorResponse(BaseModel):
    message: str
    code: str

class ValidationErrorItem(BaseModel):
    loc: list[str]
    msg: str
    type: str

class ValidationErrorResponse(ErrorResponse):
    details: list[ValidationErrorItem]
    