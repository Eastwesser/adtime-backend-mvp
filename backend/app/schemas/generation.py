from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

GenerationStatusValues = Literal["pending", "processing", "completed", "failed"]

class GenerationCreate(BaseModel):
    """Модель для создания запроса на генерацию изображения.

    Attributes:
        prompt (str): Текстовое описание для генерации
        model_version (str): Версия модели генерации
    """
    prompt: str = Field(
        ...,
        examples=["Cyberpunk cityscape at night"],
        max_length=1000,
        description="Text prompt for image generation"
    )
    model_version: str = Field(
        default="kandinsky-2.1",
        description="Model version for image generation"
    )


class GenerationResponse(GenerationCreate):
    """Модель ответа с данными о генерации изображения.

    Наследует все поля GenerationCreate и добавляет:
        id (UUID): Уникальный идентификатор генерации
        status (GenerationStatus): Текущий статус
        enhanced_prompt (str): Оптимизированный промпт (опционально)
        result_url (HttpUrl): URL сгенерированного изображения (опционально)
        external_task_id (str): ID задачи во внешнем сервисе (опционально)
        created_at (datetime): Дата создания
        user_id (UUID): ID пользователя
    """
    id: UUID = Field(..., description="Unique generation ID")
    status: GenerationStatusValues = Field(..., description="Current status")
    enhanced_prompt: Optional[str] = Field(None, description="Optimized prompt")
    result_url: Optional[HttpUrl] = Field(None, description="Generated image URL")
    external_task_id: Optional[str] = Field(None, description="External task ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    user_id: UUID = Field(..., description="User ID")

    model_config = ConfigDict(from_attributes=True)
    
class GenerationStatusResponse(BaseModel):
    """Модель ответа с текущим статусом генерации.

    Attributes:
        status (GenerationStatus): Текущий статус
        result_url (HttpUrl): URL результата (если завершено)
    """
    status: GenerationStatusValues = Field(..., description="Current status")
    result_url: Optional[HttpUrl] = Field(None, description="Result URL if completed")
