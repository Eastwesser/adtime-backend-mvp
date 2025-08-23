# app/core/password_validation.py
from password_strength import PasswordPolicy
from fastapi import HTTPException, status

policy = PasswordPolicy.from_names(
    length=8, uppercase=1, numbers=1, special=1
)

def validate_password_strength(password: str):
    """Validate password meets security requirements"""
    if errors := policy.test(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too weak. Must contain: 8+ characters, 1 uppercase, 1 number, 1 special character"
        )
    