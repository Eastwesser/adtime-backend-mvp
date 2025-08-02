from pydantic import BaseModel

from backend.app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(Token):
    """Response model for login endpoint"""
    pass


class AuthRequest(BaseModel):
    """Request model for email/password auth"""
    email: str
    password: str


class UserLoginResponse(BaseModel):
    """Combined user and token response"""
    user: UserResponse
    token: Token
