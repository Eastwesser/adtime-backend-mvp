from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt

from backend.app.core.config import settings


def load_key(key_data: str, is_private: bool):
    """Load RSA key from PEM string"""
    if is_private:
        return serialization.load_pem_private_key(
            key_data.encode(),
            password=None,
            backend=default_backend()
        )
    return serialization.load_pem_public_key(
        key_data.encode(),
        backend=default_backend()
    )


private_key = load_key(settings.JWT_PRIVATE_KEY, is_private=True)
public_key = load_key(settings.JWT_PUBLIC_KEY, is_private=False)


def create_jwt(data: dict) -> str:
    """Create signed JWT token"""
    return jwt.encode(
        data,
        private_key,
        algorithm=settings.ALGORITHM
    )


def verify_jwt(token: str) -> dict:
    """Verify and decode JWT token"""
    return jwt.decode(
        token,
        public_key,
        algorithms=[settings.ALGORITHM]
    )


def verify_yookassa_signature(notification: dict) -> bool:
    signature = notification.get("signature")
    # Implement actual verification logic
    return True
