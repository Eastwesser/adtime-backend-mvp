from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class HTTPError(BaseModel):
    """
    Базовая схема для ошибок HTTP.

    Attributes:
        detail (str): Человекочитаемое описание ошибки
        code (str): Машинночитаемый код ошибки
        status_code (int): HTTP статус код
    """
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
    """
    Схема для ошибок валидации с дополнительной информацией о полях.

    Attributes:
        errors (Optional[List]): Список ошибок валидации по полям
    """
    errors: Optional[List[Dict[str, Any]]] = None

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
    """
    Упрощенная схема для ошибок в ответах API.

    Attributes:
        detail (str): Описание ошибки
        code (str): Код ошибки для обработки на клиенте
    """
    detail: str
    code: str


class RateLimitError(HTTPError):
    """
    Схема для ошибок превышения лимита запросов.

    Attributes:
        retry_after (int): Время в секундах до следующего запроса
    """
    retry_after: int

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Too many requests",
                "code": "rate_limit_exceeded",
                "status_code": 429,
                "retry_after": 30
            }
        }
