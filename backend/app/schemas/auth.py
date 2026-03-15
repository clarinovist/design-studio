from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
import uuid


class RegisterRequest(BaseModel):
    """
    Schema for user registration.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user", example="John Doe")
    email: EmailStr = Field(..., description="Email address for the user", example="johndoe@example.com")
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters long", example="securePassword123!"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "password": "securePassword123!"
            }
        }
    )


class LoginRequest(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr = Field(..., description="Registered email address", example="johndoe@example.com")
    password: str = Field(..., description="User password", example="securePassword123!")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "johndoe@example.com",
                "password": "securePassword123!"
            }
        }
    )


class AuthResponse(BaseModel):
    """
    Schema returned upon successful authentication or registration.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "johndoe@example.com",
                "name": "John Doe",
                "avatar_url": None,
                "credits_remaining": 500
            }
        }
    )

    id: uuid.UUID = Field(..., description="Unique user ID")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    avatar_url: Optional[str] = Field(None, description="URL pointing to the user's avatar image")
    credits_remaining: int = Field(..., description="Total available generation credits for the user")
