from botocore.exceptions import ClientError

from backend.app.core.config import settings


class S3Storage:
    """
    AWS S3 Storage integration for file uploads/downloads
    
    Configuration:
        - Requires S3 credentials in settings
        - Handles file uploads with public URLs
        - Supports file deletion
    
    Usage:
        storage = S3Storage()
        url = await storage.upload(file_bytes, "path/to/file.jpg")
    """

    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self.bucket = settings.S3_BUCKET

    async def upload(self, file_bytes: bytes, file_key: str) -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_bytes
            )
            return f"{settings.S3_PUBLIC_URL}/{file_key}"
        except ClientError as e:
            raise RuntimeError(f"S3 upload failed: {e}")

    async def delete(self, file_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_key)
            return True
        except ClientError:
            return False


# Для локального тестирования
class LocalStorage:
    def __init__(self):
        self.base_path = "uploads"

    async def upload(self, file_bytes: bytes, file_key: str) -> str:
        path = f"{self.base_path}/{file_key}"
        with open(path, "wb") as f:
            f.write(file_bytes)
        return f"/media/{file_key}"
