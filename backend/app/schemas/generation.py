from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class GenerationStatus(str, Enum):
    """Статусы генерации изображения.

    Values:
        PENDING: В очереди на обработку
        PROCESSING: В процессе генерации
        COMPLETED: Успешно завершена
        FAILED: Завершена с ошибкой
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationCreate(BaseModel):
    """Модель для создания запроса на генерацию изображения.

    Attributes:
        prompt (str): Текстовое описание для генерации
        model_version (str): Версия модели генерации
    """
    prompt: str = Field(
        ...,
        examples=["Cyberpunk cityscape at night", "Watercolor landscape of mountains"],
        max_length=1000,
        description="Текстовое описание для генерации изображения"
    )
    model_version: str = Field(
        default="kandinsky-2.1",
        description="Версия модели для генерации изображения"
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
    id: UUID = Field(
        default=...,
        description="Уникальный идентификатор генерации",
    )
    status: GenerationStatus = Field(
        default=...,
        description="Текущий статус генерации",
    )
    enhanced_prompt: Optional[str] = Field(
        None,
        description="Оптимизированный промпт (опционально)"
    )
    result_url: Optional[HttpUrl] = Field(
        None,
        description="URL сгенерированного изображения (опционально)"
    )
    external_task_id: Optional[str] = Field(
        None,
        description="ID задачи во внешнем сервисе (опционально)"
    )
    created_at: datetime = Field(
        default=...,
        description="Дата создания генерации",
    )
    user_id: UUID = Field(
        default=...,
        description="ID пользователя",
    )

    class Config:
        from_attributes = True


class GenerationStatusResponse(BaseModel):
    """Модель ответа с текущим статусом генерации.

    Attributes:
        status (GenerationStatus): Текущий статус
        result_url (HttpUrl): URL результата (если завершено)
    """
    status: GenerationStatus = Field(
        default=...,
        description="Текущий статус генерации",
    )
    result_url: Optional[HttpUrl] = Field(
        None,
        description="URL сгенерированного изображения (если завершено)"
    )
