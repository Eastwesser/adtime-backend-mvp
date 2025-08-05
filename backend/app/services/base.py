from datetime import datetime
from typing import Generic, TypeVar, Optional
from uuid import UUID

from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ResponseSchemaType = TypeVar("ResponseSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def get(self, id: UUID) -> Optional[ResponseSchemaType]:
        """Получение одной записи по ID

        Args:
            id: UUID записи

        Returns:
            Optional[ResponseSchemaType]: Найденная запись или None
        """
        obj = await self.repository.get(id)
        return ResponseSchemaType.model_validate(obj) if obj else None

    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        """Создание новой записи

        Args:
            obj_in: Данные для создания

        Returns:
            ResponseSchemaType: Созданная запись
        """
        obj = await self.repository.create(obj_in)
        return ResponseSchemaType.model_validate(obj)

    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ResponseSchemaType]:
        """Обновление существующей записи

        Args:
            id: UUID записи
            obj_in: Данные для обновления

        Returns:
            Optional[ResponseSchemaType]: Обновленная запись или None если не найдена
        """
        obj = await self.repository.update(id, obj_in)
        return ResponseSchemaType.model_validate(obj) if obj else None

    async def delete(self, id: UUID) -> bool:
        """Мягкое удаление записи (soft delete)

        Args:
            id: UUID записи для удаления

        Returns:
            bool: True если удаление успешно, False если запись не найдена
        """
        return await self.repository.update(
            id,
            {
                "is_deleted": True,
                "deleted_at": datetime.now()
            }
        ) is not None

    async def restore(self, id: UUID) -> bool:
        """Восстановление мягко удалённой записи

        Args:
            id: UUID записи для восстановления

        Returns:
            bool: True если восстановление успешно, False если запись не найдена
        """
        return await self.repository.update(
            id,
            {
                "is_deleted": False,
                "deleted_at": None
            }
        ) is not None

    async def list_all(
            self,
            include_deleted: bool = False,
            limit: int = 100,
            offset: int = 0
    ) -> list[ResponseSchemaType]:
        """Получение списка записей с возможностью включать удалённые

        Args:
            include_deleted: Включать ли удалённые записи
            limit: Лимит записей
            offset: Смещение

        Returns:
            list[ResponseSchemaType]: Список записей
        """
        objs = await self.repository.list_all(include_deleted, limit, offset)
        return [ResponseSchemaType.model_validate(obj) for obj in objs]
