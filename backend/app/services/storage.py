import aiofiles
import os
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from pathlib import Path

class StorageService:
    def __init__(self):
        self.upload_dir = Path("uploads/images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_image(self, file: UploadFile, user_id: str) -> str:
        """Загрузить изображение и вернуть URL"""
        try:
            # Генерируем уникальное имя файла
            file_extension = file.filename.split('.')[-1]
            filename = f"{user_id}_{os.urandom(8).hex()}.{file_extension}"
            file_path = self.upload_dir / filename
            
            # Сохраняем файл
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            return f"{settings.APP_URL}/uploads/images/{filename}"
            
        except Exception as e:
            raise HTTPException(500, f"Ошибка загрузки файла: {str(e)}")
        