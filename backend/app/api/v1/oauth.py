from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="", tags=["OAuth"])

@router.get("/providers")
async def get_oauth_providers():
    """Список OAuth провайдеров (заглушка)"""
    return {
        "providers": [
            {
                "id": "google",
                "name": "Google",
                "enabled": False
            },
            {
                "id": "yandex", 
                "name": "Yandex",
                "enabled": False
            }
        ]
    }

@router.post("/{provider}/init")
async def init_oauth(provider: str):
    """Инициализация OAuth (заглушка)"""
    raise HTTPException(501, "OAuth not implemented yet")

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, code: str, state: str = None):
    """Callback для OAuth (заглушка)"""
    raise HTTPException(501, "OAuth not implemented yet")