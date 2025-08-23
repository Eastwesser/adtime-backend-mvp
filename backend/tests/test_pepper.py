# tests/test_pepper.py
import pytest
from app.services.auth import AuthService
from app.core.config import settings

def test_pepper_implementation():
    """Test that pepper is working correctly"""
    password = "MySecurePassword123!"
    
    # Hash with pepper
    hashed = AuthService.get_password_hash(password)
    
    # Verify with correct password
    assert AuthService.verify_password(password, hashed) == True
    
    # Verify with wrong password
    assert AuthService.verify_password("WrongPassword", hashed) == False
    
    # Verify pepper is configured
    assert settings.PASSWORD_PEPPER != ""
    assert len(settings.PASSWORD_PEPPER) >= 32

def test_pepper_security():
    """Test that pepper adds security"""
    password = "test123"
    
    # Hash with our pepper
    hashed_with_pepper = AuthService.get_password_hash(password)
    
    # Simulate hash without pepper (как у хакера)
    from passlib.context import CryptContext
    no_pepper_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_without_pepper = no_pepper_context.hash(password)
    
    # Они должны быть РАЗНЫЕ!
    assert hashed_with_pepper != hashed_without_pepper
    
    # Наш верифаер должен отвергать хеши без pepper
    assert AuthService.verify_password(password, hashed_without_pepper) == False