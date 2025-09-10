# Работа с Kandinsky API
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException

from app.core.logger import logger
from app.repositories.generation import GenerationRepository
from app.repositories.subscription import SubscriptionRepository
from app.schemas.generation import GenerationCreate, GenerationResponse, GenerationStatusResponse
from app.services.kandinsky import KandinskyAPI, GenerationRequest


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
            generation_in: GenerationCreate,
            api_client: KandinskyAPI
    ) -> Optional[GenerationResponse]:
        """
        Creates new generation task with:
        - Quota validation
        - Kandinsky API integration
        - Automatic status tracking
        """
        # UNCOMMENT THESE LINES BELOW, THEY CHECK QUOTA AND MONEY!!!
        if not await self._check_quota(user_id):
            raise HTTPException(
                status_code=402,
                detail="Generation quota exceeded"
            )

        # Создаем запись в БД
        generation_data = generation_in.model_dump()
        # Remove width and height since Generation model doesn't accept them
        generation_data.pop("width", None)
        generation_data.pop("height", None)

        db_generation = await self.generation_repo.create({
            **generation_data,
            "user_id": user_id,
            "status": "pending"
        })

        # Запускаем генерацию
        try:
            request = GenerationRequest(
                prompt=generation_in.prompt,
                width=generation_in.width,
                height=generation_in.height
            )
            task_id = await api_client.generate_image(request)

            if not task_id:
                await self._mark_as_failed(db_generation.id)
                return None

            # Update DB record
            updated_gen = await self.generation_repo.update(
                db_generation.id,
                {
                    "status": "processing",
                    "external_task_id": task_id,
                    "started_at": datetime.now()
                }
            )

            # Decrement user quota
            await self.subscription_repo.decrement_quota(user_id)

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

        except Exception as e:
            await self._mark_as_failed(db_generation.id)
            raise HTTPException(
                status_code=503,
                detail=f"Generation failed: {str(e)}"
            )

    async def check_generation_status(
            self,
            generation_id: uuid.UUID,
            api_client: KandinskyAPI
    ) -> Optional[GenerationStatusResponse]:
        """Checks generation status with Kandinsky API"""
        generation = await self.generation_repo.get(generation_id)
        if not generation:
            return None

        # If already completed/failed, return current status
        if generation.status in ["completed", "failed"]:
            return GenerationStatusResponse.model_validate(generation)

        # Check with Kandinsky API
        try:
            if generation.external_task_id:
                image_data = await api_client.check_generation_status(
                    generation.external_task_id
                )

                updates = {}
                if image_data:
                    updates.update({
                        "status": "completed",
                        "result_url": self._store_image(generation_id, image_data),
                        "completed_at": datetime.now()
                    })
                else:
                    updates["status"] = "failed"

                updated_gen = await self.generation_repo.update(
                    generation_id,
                    updates
                )
                return GenerationStatusResponse.model_validate(updated_gen)

        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            await self._mark_as_failed(generation_id)

        return None

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

    async def cancel_generation(
            self,
            generation_id: uuid.UUID,
            user_id: uuid.UUID,
            api_client: KandinskyAPI
    ) -> bool:
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

        if generation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not your generation")

        if generation.status not in ["pending", "processing"]:
            return False

            # Cancel in Kandinsky API
        if generation.external_task_id:
            await api_client.cancel_generation(generation.external_task_id)

            # Update DB
        await self.generation_repo.update(
            generation_id,
            {
                "status": "cancelled",
                "cancelled_at": datetime.now()
            }
        )

        # Refund quota
        await self.subscription_repo.increment_quota(user_id)
        return True

        # Helper methods

    async def _check_quota(self, user_id: uuid.UUID) -> bool:
        """Checks if user has available generations quota"""
        subscription = await self.subscription_repo.get_by_user(user_id)
        return subscription and subscription.remaining_generations > 0

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

    async def _mark_as_failed(self, generation_id: uuid.UUID) -> None:
        """Помечает генерацию как неудачную в базе данных.

        Args:
            generation_id: UUID задачи генерации

        Side effects:
            - Обновляет статус генерации на 'failed'
            - Устанавливает дату и время ошибки
            - Логирует ошибку
        """
        try:
            await self.generation_repo.update(
                generation_id,
                {
                    "status": "failed",
                    "failed_at": datetime.now()
                }
            )
            logger.error(f"Generation {generation_id} marked as failed")
        except Exception as e:
            logger.critical(
                f"Failed to mark generation {generation_id} as failed: {str(e)}"
            )
            raise

    async def _mark_as_failed(self, generation_id: uuid.UUID):
        """Marks generation as failed in DB"""
        await self.generation_repo.update(
            generation_id,
            {
                "status": "failed",
                "failed_at": datetime.now()
            }
        )

    @staticmethod
    def _store_image(generation_id: uuid.UUID, image_data: bytes) -> str:
        """Stores generated image and returns URL"""
        # Implementation depends on your storage (S3, local, etc.)
        return f"https://storage.example.com/{generation_id}.jpg"
