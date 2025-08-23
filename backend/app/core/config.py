import os
from typing import Optional
from cryptography.hazmat.primitives import serialization
from pydantic import Field, PostgresDsn, RedisDsn, HttpUrl
from pydantic.v1 import validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from yookassa import Configuration
import rsa

class Settings(BaseSettings):
    PROJECT_NAME: str = "AdTime Marketplace"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database settings
    DATABASE_URL: PostgresDsn = Field(description="URL подключения к PostgreSQL")
    # DATABASE_URL: PostgresDsn = Field(
    #     default="postgresql+asyncpg://user:pass@localhost:5432/db",
    #     description="URL подключения к PostgreSQL"
    # )
    DB_ECHO: bool = Field(
        default=False,
        description="Логировать SQL-запросы"
    )

    # S3
    S3_ENDPOINT: HttpUrl = Field(
        description="Endpoint S3-совместимого хранилища"
    )
    S3_ACCESS_KEY: str = Field(
        description="Access key для S3"
    )
    S3_SECRET_KEY: str = Field(
        description="Secret key для S3"
    )
    S3_BUCKET: str = "adtime-dev"
    S3_PUBLIC_URL: str

    # Payments
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_RETURN_URL: str = "https://yourapp.com/payment/return"

    # Redis
    REDIS_URL: RedisDsn = Field(description="Redis connection URL")
    # REDIS_URL: RedisDsn = "redis://redis:6379/0" 

    # Auth
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = Field(
        default=None,
        description="Публичный ключ для проверки JWT"
    )
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Kandinsky
    KANDINSKY_API_KEY: str
    KANDINSKY_SECRET_KEY: str

    # CORS and API
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "https://yourapp.com"],
        description="Allowed CORS origins"
    )
    # ALLOWED_ORIGINS: list[str] = ["*"]
    API_VERSION: str = "1.0.0"
    SUPPORT_EMAIL: str = "support@adtime.com"

    # Modern Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Webhook settings
    WEBHOOK_SECRET: str = Field(
        default=os.urandom(32).hex(),  # Generate random secret if not provided
        description="Secret key for webhook signature validation"
    )
    
    WEBHOOK_RETRY_DELAY: float = Field(
        default=1.0,
        description="Initial retry delay in seconds"
    )

    WEBHOOK_MAX_RETRIES: int = Field(
        default=5 if os.getenv('ENVIRONMENT') == 'production' else 3,
        description="Maximum retry attempts for webhook processing"
    )
    
    WEBHOOK_RETRY_BACKOFF: float = Field(
        default=2.0,
        description="Retry backoff multiplier"
    )

    # PEPPER для паролей
    PASSWORD_PEPPER: str = Field(
        default="",
        description="Secret pepper value for password hashing. Critical for security!"
    )
    
    # Дополнительно можно добавить:
    BCRYPT_ROUNDS: int = Field(
        default=12,
        description="Cost factor for bcrypt password hashing",
        ge=10, le=16  # Минимум 10, максимум 16
    )

    @validator('ALLOWED_ORIGINS', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(',')
        return v

    @validator('WEBHOOK_SECRET')
    def validate_webhook_secret(cls, v):
        if len(v) < 16:  # Minimum length for security
            raise ValueError('Webhook secret must be at least 16 characters')
        return v

    @validator('S3_ENDPOINT')
    def validate_s3_endpoint(cls, v):
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('Invalid S3 endpoint URL')
        return v

    def load_keys(self):
        """Load keys from files"""
        try:
            with open('private.pem') as f:
                self.JWT_PRIVATE_KEY = f.read().strip()
            with open('public.pem') as f:
                self.JWT_PUBLIC_KEY = f.read().strip()
        except FileNotFoundError:
            # Fall back to generating new keys if files don't exist
            self.generate_keys()
            # Save the generated keys
            with open('private.pem', 'w') as f:
                f.write(self.JWT_PRIVATE_KEY)
            with open('public.pem', 'w') as f:
                f.write(self.JWT_PUBLIC_KEY)

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

class YooKassaConfig:
    @classmethod
    def setup(cls, settings: Settings):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

def get_settings() -> Settings:
    """Factory function for getting settings"""
    settings = Settings()
    settings.load_keys()
    return settings

settings = get_settings()
