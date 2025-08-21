from fastapi import APIRouter
from app.core.config import settings


router = APIRouter(
    prefix="",
    tags=["GenConfig"],
)


@router.get("/generation")
async def get_generation_config():
    """Конфигурация генерации (стили, размеры, лимиты)"""
    return {
        "styles": [
            {"id": "malevich", "name": "Малевич", "description": "Авангардный стиль"},
            {"id": "cyberpunk", "name": "Киберпанк", "description": "Футуристичный стиль"},
            {"id": "classicism", "name": "Классицизм", "description": "Классический стиль"},
            {"id": "portrait", "name": "Портретное фото", "description": "Портретный стиль"},
            {"id": "khokhloma", "name": "Хохлома", "description": "Народный стиль"},
            {"id": "detailed", "name": "Детальное фото", "description": "Детализированный стиль"},
            {"id": "kandinsky", "name": "Кандинский", "description": "Абстрактный стиль"}
        ],
        "sizes": [
            {"id": "1:1", "name": "Квадрат", "width": 1024, "height": 1024},
            {"id": "16:9", "name": "Широкоформатный", "width": 1920, "height": 1080},
            {"id": "9:16", "name": "Вертикальный", "width": 1080, "height": 1920},
            {"id": "3:2", "name": "Классический", "width": 1200, "height": 800},
            {"id": "2:3", "name": "Портретный", "width": 800, "height": 1200}
        ],
        "limits": {
            "max_prompt_length": settings.MAX_PROMPT_LENGTH,
            "max_file_size": settings.MAX_FILE_SIZE,
            "max_generations_per_hour": settings.RATE_LIMIT_GENERATIONS
        }
    }
