from datetime import datetime
from typing import TypeVar, Generic, Optional, Sequence, Any, Union
from uuid import UUID

from sqlalchemy import update, delete, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD операциями и поддержкой soft delete.

    Содержит общие методы для работы с любыми сущностями:
    - Базовые CRUD операции (create, read, update, delete)
    - Поддержка мягкого удаления (soft delete)
    - Пагинация и фильтрация
    - Универсальные методы для работы с БД

    Основные принципы:
    1. Все методы асинхронные
    2. Работает с SQLAlchemy async session
    3. Поддерживает Generic типы для работы с любой моделью
    4. Обрабатывает базовые ошибки БД

    Примечания:
    - Для мягкого удаления модель должна иметь поля is_deleted и deleted_at
    - Для кастомных запросов следует создавать методы в дочерних репозиториях
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """Инициализация репозитория.

        Args:
            model: SQLAlchemy модель сущности
            session: Асинхронная сессия SQLAlchemy
        """
        self.model = model
        self.session = session

    async def get(self, id: UUID, include_deleted: bool = False) -> Optional[ModelType]:
        """Получение одной записи по ID.

        Args:
            id: UUID записи
            include_deleted: Включать ли удалённые записи (по умолчанию False)

        Returns:
            Optional[ModelType]: Найденная запись или None
        """
        query = select(self.model).where(self.model.id == id)
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, obj_in: Union[dict, Any]) -> ModelType:
        """Создание новой записи.

        Args:
            obj_in: Данные для создания (dict или pydantic модель)

        Returns:
            ModelType: Созданная запись
        """
        if not isinstance(obj_in, dict):
            obj_in = obj_in.dict()

        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: UUID, obj_in: Union[dict, Any]) -> Optional[ModelType]:
        """Обновление существующей записи.

        Args:
            id: UUID записи
            obj_in: Данные для обновления (dict или pydantic модель)

        Returns:
            Optional[ModelType]: Обновлённая запись или None если не найдена
        """
        if not isinstance(obj_in, dict):
            obj_in = obj_in.dict(exclude_unset=True)

        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
        )
        await self.session.commit()
        return await self.get(id, include_deleted=True)

    async def delete(self, id: UUID) -> bool:
        """Физическое удаление записи из БД.

        Args:
            id: UUID записи

        Returns:
            bool: True если удаление успешно, False если запись не найдена
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def soft_delete(self, id: UUID) -> bool:
        """Мягкое удаление записи (проставляет флаг is_deleted).

        Args:
            id: UUID записи

        Returns:
            bool: True если удаление успешно, False если запись не найдена

        Raises:
            ValueError: Если модель не поддерживает soft delete
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValueError("Model doesn't support soft delete")

        return await self.update(
            id,
            {"is_deleted": True, "deleted_at": datetime.now()}
        ) is not None

    async def restore(self, id: UUID) -> bool:
        """Восстановление мягко удалённой записи.

        Args:
            id: UUID записи

        Returns:
            bool: True если восстановление успешно, False если запись не найдена

        Raises:
            ValueError: Если модель не поддерживает soft delete
        """
        if not hasattr(self.model, 'is_deleted'):
            raise ValueError("Model doesn't support soft delete")

        return await self.update(
            id,
            {"is_deleted": False, "deleted_at": None}
        ) is not None

    async def list(
            self,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[dict] = None
    ) -> Sequence[ModelType]:
        """Получение списка записей с пагинацией.

        Args:
            skip: Количество записей для пропуска (offset)
            limit: Максимальное количество записей
            filters: Дополнительные фильтры {поле: значение}

        Returns:
            Sequence[ModelType]: Список записей
        """
        query = select(self.model).offset(skip).limit(limit)
        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_all(
            self,
            include_deleted: bool = False,
            limit: int = 100,
            offset: int = 0,
            filters: Optional[dict] = None
    ) -> Sequence[ModelType]:
        """Получение полного списка записей с поддержкой soft delete.

        Args:
            include_deleted: Включать ли удалённые записи
            limit: Максимальное количество записей
            offset: Смещение (skip)
            filters: Дополнительные фильтры {поле: значение}

        Returns:
            Sequence[ModelType]: Список записей
        """
        query = select(self.model).offset(offset).limit(limit)

        # Применяем фильтр по is_deleted если нужно и модель поддерживает soft delete
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted == False)

        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        return result.scalars().all()

    def _apply_filters(self, query: Select, filters: Optional[dict] = None) -> Select:
        """Применяет дополнительные фильтры к запросу.

        Args:
            query: SQLAlchemy Select запрос
            filters: Словарь фильтров {поле: значение}

        Returns:
            Select: Модифицированный запрос с фильтрами
        """
        if not filters:
            return query

        conditions = []
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    conditions.append(getattr(self.model, field).in_(value))
                else:
                    conditions.append(getattr(self.model, field) == value)

        if conditions:
            query = query.where(and_(*conditions))

        return query
