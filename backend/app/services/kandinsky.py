import asyncio
import base64
import logging
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GenerationRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    num_images: int = 1


class KandinskyAPI:
    def __init__(self, api_key: str, secret_key: str):
        self.base_url = "https://api-key.fusionbrain.ai/"
        self.headers = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient()

    async def get_pipeline_id(self) -> Optional[str]:
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

    async def generate_image(self, request: GenerationRequest) -> Optional[str]:
        pipeline_id = await self.get_pipeline_id()
        if not pipeline_id:
            return None

        params = {
            "type": "GENERATE",
            "numImages": request.num_images,
            "width": request.width,
            "height": request.height,
            "generateParams": {"query": request.prompt}
        }

        files = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, params, 'application/json')
        }

        try:
            response = await self.client.post(
                f"{self.base_url}key/api/v1/pipeline/run",
                headers=self.headers,
                files=files,
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
            max_attempts: int = 10,
            delay: float = 3.0
    ) -> Optional[bytes]:
        attempt = 0
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
            except Exception as e:
                logger.error(f"Error checking status: {str(e)}")
                attempt += 1
                await asyncio.sleep(delay)

        logger.error(f"Max attempts reached for task {task_id}")
        return None

    async def close(self):
        await self.client.aclose()

    @asynccontextmanager
    async def context(self):
        try:
            yield self
        finally:
            await self.close()

# # Usage example:
# async with KandinskyAPI(api_key, secret_key).context() as api:
#     await api.generate_image(...)
