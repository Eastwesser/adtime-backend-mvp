from typing import Generic, TypeVar, Optional
from uuid import UUID

from backend.app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ResponseSchemaType = TypeVar("ResponseSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def get(self, id: UUID) -> Optional[ResponseSchemaType]:
        raise NotImplementedError

    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        raise NotImplementedError

    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ResponseSchemaType]:
        raise NotImplementedError
