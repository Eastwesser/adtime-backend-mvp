from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from yookassa import Configuration


class Settings(BaseSettings):
    PROJECT_NAME: str = "AdTime Marketplace"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database - Updated to use PostgresDsn for validation
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://postgres:adtime@localhost:5432/adtime"
    DB_ECHO: bool = False

    # S3
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "adtime-dev"
    S3_PUBLIC_URL: str

    # Payments
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_RETURN_URL: str = "https://yourapp.com/payment/return"

    # Redis - Updated to use RedisDsn
    REDIS_URL: RedisDsn = "redis://redis:6379"

    # Auth
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = None
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Kandinsky
    KANDINSKY_API_KEY: str
    KANDINSKY_SECRET_KEY: str

    # CORS and API
    ALLOWED_ORIGINS: list[str] = ["*"]
    API_VERSION: str = "1.0.0"
    SUPPORT_EMAIL: str = "support@adtime.com"

    # Modern Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8"
    )

    def generate_keys(self):
        """Generate RSA keys if not provided"""
        if not self.JWT_PRIVATE_KEY:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.JWT_PRIVATE_KEY = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')

            public_key = private_key.public_key()
            self.JWT_PUBLIC_KEY = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')

    @property
    def database_kwargs(self) -> dict:
        """For SQLAlchemy connection kwargs"""
        return {
            "url": str(self.DATABASE_URL),
            "echo": self.DB_ECHO
        }


settings = Settings()
settings.generate_keys()


class YooKassaConfig:
    @classmethod
    def setup(cls):
        """Initialize YooKassa with project settings"""
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


YooKassaConfig.setup()
