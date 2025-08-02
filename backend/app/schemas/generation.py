from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationCreate(BaseModel):
    prompt: str = Field(..., examples=[
        "Cyberpunk cityscape at night",
        "Watercolor landscape of mountains"
    ],
                        max_length=1000,
                        )
    model_version: str = Field(default="kandinsky-2.1")


class GenerationResponse(GenerationCreate):
    id: UUID
    status: GenerationStatus
    enhanced_prompt: Optional[str] = None
    result_url: Optional[HttpUrl] = None
    external_task_id: Optional[str] = None
    created_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True


class GenerationStatusResponse(BaseModel):
    status: GenerationStatus
    result_url: Optional[HttpUrl] = None
