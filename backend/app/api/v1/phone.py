from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

router = APIRouter(prefix="/phone", tags=["Phone Auth"])

# Добавляем схемы для запросов
class PhoneInitRequest(BaseModel):
    phone: str

class PhoneVerifyRequest(BaseModel):
    phone: str
    code: str

@router.post("/init")
async def init_phone_login(request: PhoneInitRequest = Body(...)):
    """Отправка SMS (заглушка)"""
    # Для тестирования можно временно возвращать успех
    return {
        "success": True,
        "message": "SMS sent (stub)",
        "phone": request.phone,
        "test_code": "123456"  # Для демо/тестирования
    }

@router.post("/verify")
async def verify_phone(request: PhoneVerifyRequest = Body(...)):
    """Проверка кода SMS (заглушка)"""
    # Простая проверка для тестирования
    if request.code == "123456":
        return {
            "success": True,
            "message": "Phone verified (stub)",
            "phone": request.phone
        }
    else:
        raise HTTPException(400, "Invalid code")