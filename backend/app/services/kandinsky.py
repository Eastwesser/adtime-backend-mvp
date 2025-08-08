import asyncio
import base64
from asyncio import Timeout
from contextlib import asynccontextmanager
from typing import ClassVar, Optional

import httpx
from httpx import AsyncClient, Limits, AsyncHTTPTransport
from pydantic import BaseModel, Field, field_validator 
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logger import get_logger

logger = get_logger(__name__)


class GenerationRequest(BaseModel):
    """Модель запроса для генерации изображения через Kandinsky API.

    Attributes:
        prompt: Текст запроса для генерации
        width: Ширина изображения (по умолчанию 1024)
        height: Высота изображения (по умолчанию 1024)
        num_images: Количество генерируемых изображений (по умолчанию 1)
    """
    prompt: str = Field(..., min_length=3, max_length=1000)
    width: int = Field(1024, ge=256, le=2048)
    height: int = Field(1024, ge=256, le=2048)
    num_images: int = Field(1, ge=1, le=4)
    
    @field_validator('width', 'height')
    def validate_dimensions(cls, v):
        if v % 64 != 0:  # Kandinsky requires multiples of 64
            raise ValueError("Dimensions must be multiples of 64")
        return v
    
class GenerationStatus(BaseModel):
    """Статусы генерации в Kandinsky API.

    Values:
        PENDING: Задача в очереди на выполнение
        PROCESSING: Генерация в процессе
        COMPLETED: Успешно завершена
        FAILED: Завершена с ошибкой
    """
    GENERATION_STATUS: ClassVar[dict] = {
        'PENDING': 'PENDING',
        'PROCESSING': 'PROCESSING', 
        'COMPLETED': 'COMPLETED',
        'FAILED': 'FAILED'
    }

    @classmethod
    def from_kandinsky(cls, status: str) -> str:
        """Converts Kandinsky API status to our status string"""
        status_map = {
            'NEW': cls.GENERATION_STATUS['PENDING'],
            'PROCESSING': cls.GENERATION_STATUS['PROCESSING'],
            'DONE': cls.GENERATION_STATUS['COMPLETED'],
            'FAIL': cls.GENERATION_STATUS['FAILED']
        }
        return status_map.get(status, cls.GENERATION_STATUS['FAILED'])

class KandinskyAPI:
    """Клиент для работы с Kandinsky API (https://fusionbrain.ai/).

    Обеспечивает:
    - Генерацию изображений по текстовому описанию
    - Проверку статуса генерации
    - Управление подключением к API

    Для работы требуется:
    - API ключ (получается в личном кабинете FusionBrain)
    - Секретный ключ
    """

    def __init__(self, api_key: str, secret_key: str):
        self.base_url = "https://api-key.fusionbrain.ai/"
        self.headers = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }
        self.timeout = httpx.Timeout(30.0)  # Таймаут запросов 30 секунд
        self.client = AsyncClient(
            timeout=Timeout(30.0),
            limits=Limits(max_connections=100, max_keepalive_connections=20),
            transport=AsyncHTTPTransport(retries=3)  # Добавляем автоматические ретраи
        )  # Асинхронный HTTP-клиент

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_pipeline_id(self) -> Optional[str]:
        """Получение ID активного пайплайна для генерации.

        Returns:
            Optional[str]: ID пайплайна или None в случае ошибки

        Note:
            Kandinsky API требует указания pipeline_id для генерации
        """
        try:
            response = await self.client.get(
                f"{self.base_url}key/api/v1/pipelines",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data[0]['id'] if data else None
        except Exception as e:
            logger.error(f"Error getting pipeline: {str(e)}")
            return None

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    async def generate_image(self, request: GenerationRequest) -> Optional[str]:
        """Запуск генерации изображения по текстовому запросу.

        Args:
            request: Параметры генерации (текст, размеры и т.д.)

        Returns:
            Optional[str]: UUID задачи генерации или None в случае ошибки

        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        pipeline_id = await self.get_pipeline_id()
        if not pipeline_id:
            return None

        # Подготовка параметров генерации
        params = {
            "type": "GENERATE",
            "numImages": request.num_images,
            "width": request.width,
            "height": request.height,
            "generateParams": {"query": request.prompt}
        }

        # Формируем multipart/form-data запрос
        files = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, params, 'application/json')
        }

        try:
            response = await self.client.post(
                f"{self.base_url}key/api/v1/pipeline/run",
                headers=self.headers,
                files={
                    'pipeline_id': (None, pipeline_id),
                    'params': (None, params, 'application/json')
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['uuid']
        except Exception as e:
            logger.error(f"Error starting generation: {str(e)}")
            return None

    async def check_generation_status(
            self,
            task_id: str,
            max_attempts: int = 20,
            initial_delay: float = 2.0
    ) -> Optional[bytes]:
        """Проверка статуса генерации изображения.

        Args:
            task_id: UUID задачи генерации
            max_attempts: Максимальное количество попыток проверки
            initial_delay: Задержка между попытками (в секундах)

        Returns:
            Optional[bytes]: Бинарные данные изображения в формате base64 или None

        Note:
            Использует полинг с экспоненциальным backoff (можно улучшить)
        """
        attempt = 0
        delay = initial_delay

        while attempt < max_attempts:
            try:
                response = await self.client.get(
                    f"{self.base_url}key/api/v1/pipeline/status/{task_id}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                data = response.json()

                if data['status'] == 'DONE':
                    return base64.b64decode(data['result']['files'][0])
                elif data['status'] == 'FAIL':
                    logger.error(f"Generation failed: {data.get('errorDescription')}")
                    return None

                attempt += 1
                await asyncio.sleep(delay)
                delay = min(delay * 1.5, 10.0)  # Exponential backoff with max 10s

            except Exception as e:
                logger.warning(f"Status check attempt {attempt} failed: {str(e)}")
                attempt += 1
                await asyncio.sleep(delay)
                delay = min(delay * 1.5, 10.0)

        logger.error(f"Max status check attempts reached for task {task_id}")
        return None

    async def close(self):
        """Корректное закрытие HTTP-клиента."""
        await self.client.aclose()

    @asynccontextmanager
    async def context(self):
        """Контекстный менеджер для автоматического управления подключением.

        Usage:
            async with KandinskyAPI(api_key, secret_key).context() as api:
                await api.generate_image(...)
        """
        try:
            yield self
        finally:
            await self.client.aclose()



    async def cancel_generation(self, external_task_id: str) -> bool:
        """Отмена задачи генерации в Kandinsky API.

        Args:
            external_task_id: ID задачи в Kandinsky API

        Returns:
            bool: True если отмена успешна, False если задача уже завершена

        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        try:
            response = await self.client.post(
                f"{self.base_url}key/api/v1/pipeline/cancel/{external_task_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("success", False)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Generation task {external_task_id} not found")
                return False
            logger.error(f"Error cancelling generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error cancelling generation: {str(e)}")
            raise
