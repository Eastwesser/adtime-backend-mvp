# Работа с Kandinsky API
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException

from backend.app.repositories.generation import GenerationRepository
from backend.app.repositories.subscription import SubscriptionRepository
from backend.app.schemas.generation import GenerationCreate, GenerationResponse
from backend.app.services.kandinsky import KandinskyAPI, GenerationRequest


class GenerationService:
    """
    Сервис для работы с генерацией изображений через Kandinsky API.
    Основные функции:
    - Управление квотами генераций
    - Запуск и отслеживание задач генерации
    - Хранение результатов
    """

    def __init__(
            self,
            generation_repo: GenerationRepository,
            subscription_repo: SubscriptionRepository,
            kandinsky_api: KandinskyAPI
    ):
        self.generation_repo = generation_repo
        self.subscription_repo = subscription_repo
        self.kandinsky_api = kandinsky_api

    async def check_quota(self, user_id: uuid.UUID) -> bool:
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription or subscription.remaining_generations <= 0:
            return False
        return True

    async def create_generation(
            self,
            user_id: uuid.UUID,
            generation_in: GenerationCreate
    ) -> Optional[GenerationResponse]:

        if not await self.check_quota(user_id):
            raise HTTPException(
                status_code=402,
                detail="Generation quota exceeded. Please upgrade your subscription."
            )

        # Создаем запись в БД
        generation_data = {
            **generation_in.model_dump(),
            "user_id": user_id,
            "status": "pending"
        }
        db_generation = await self.generation_repo.create(generation_data)

        # Запускаем генерацию
        request = GenerationRequest(
            prompt=generation_in.prompt,
            model_version=generation_in.model_version
        )
        task_id = await self.kandinsky_api.generate_image(request)

        if not task_id:
            await self.generation_repo.update(db_generation.id, {"status": "failed"})
            return None

        # Обновляем запись в БД
        updated_gen = await self.generation_repo.update(
            db_generation.id,
            {
                "status": "processing",
                "external_task_id": task_id
            }
        )

        await self.subscription_repo.decrement_quota(user_id)

        return GenerationResponse.model_validate(updated_gen)

    async def check_generation_status(
            self,
            generation_id: uuid.UUID
    ) -> Optional[GenerationResponse]:
        generation = await self.generation_repo.get(generation_id)
        if not generation or not generation.external_task_id:
            return None

        image_data = await self.kandinsky_api.check_generation_status(
            generation.external_task_id
        )

        updates = {}
        if image_data:
            updates.update({
                "status": "completed",
                "result_url": self._store_image(generation_id)
            })
        else:
            updates["status"] = "failed"

        updated_gen = await self.generation_repo.update(generation_id, updates)
        return GenerationResponse.model_validate(updated_gen)

    @staticmethod
    def _store_image(generation_id: uuid.UUID) -> str:
        # Здесь реализация сохранения изображения (S3, локальное хранилище и т.д.)
        # Возвращаем URL до изображения
        return f"https://storage.example.com/generations/{generation_id}.jpg"

    async def get_user_generations(
            self,
            user_id: uuid.UUID,
            limit: int = 100
    ) -> List[GenerationResponse]:
        generations = await self.generation_repo.get_by_user(user_id, limit=limit)
        return [GenerationResponse.model_validate(g) for g in generations]

    async def cancel_generation(self, generation_id: uuid.UUID) -> bool:
        """Отмена запущенной генерации

        Args:
            generation_id: UUID задачи генерации

        Returns:
            bool: True если отмена успешна, False если задача уже завершена

        Raises:
            HTTPException: Если генерация не найдена или нет прав на отмену
        """
        generation = await self.generation_repo.get(generation_id)
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")

        if generation.status not in ["pending", "processing"]:
            return False

        # Отменяем задачу в Kandinsky API
        if generation.external_task_id:
            await self.kandinsky_api.cancel_generation(generation.external_task_id)

        # Обновляем статус в БД
        await self.generation_repo.update(
            generation_id,
            {"status": "cancelled", "cancelled_at": datetime.now()}
        )

        # Возвращаем квоту пользователю
        await self.subscription_repo.increment_quota(generation.user_id)
        return True

    async def get_generation_history(
            self,
            user_id: uuid.UUID,
            limit: int = 100,
            offset: int = 0
    ) -> List[GenerationResponse]:
        """Получение истории генераций с пагинацией

        Args:
            user_id: UUID пользователя
            limit: Количество записей на странице
            offset: Смещение для пагинации

        Returns:
            List[GenerationResponse]: Список генераций пользователя
        """
        generations = await self.generation_repo.get_by_user_paginated(
            user_id,
            limit=limit,
            offset=offset
        )
        return [GenerationResponse.model_validate(g) for g in generations]
