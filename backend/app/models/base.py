"""
Базовый класс для всех моделей SQLAlchemy.

Создает declarative_base() - основу для объявления моделей.
Все модели должны наследоваться от этого класса.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
