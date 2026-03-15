from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
import uuid
from datetime import datetime


from pydantic import Field


class UserUpdate(BaseModel):
    """
    Schema for updating a user's profile.
    """
    name: Optional[str] = Field(None, description="The updated name of the user. Must be between 2 and 100 characters.", example="John Doe")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Smith"
            }
        }
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Name cannot be empty or whitespace only")
        if len(v) > 100:
            raise ValueError("Name must be 100 characters or fewer")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v


class UserResponse(BaseModel):
    """
    Schema representing a user profile with associated quotas and credits.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "Jane Smith",
                "avatar_url": "https://example.com/avatar.png",
                "credits_remaining": 500,
                "storage_used": 1500000,
                "storage_quota": 104857600,
                "provider": "email",
                "created_at": "2023-01-01T12:00:00Z"
            }
        }
    )

    id: uuid.UUID = Field(..., description="Unique user identifier.")
    email: str = Field(..., description="User's email address.")
    name: str = Field(..., description="User's full name.")
    avatar_url: Optional[str] = Field(None, description="URL pointing to the user's avatar image.")
    credits_remaining: int = Field(..., description="Available generation credits for the user.")
    storage_used: int = Field(0, description="Bytes of storage currently used by the user.")
    storage_quota: int = Field(104857600, description="Total storage bytes allowed for the user.")
    provider: str = Field(..., description="Authentication provider (e.g. email, google, facebook).")
    created_at: datetime = Field(..., description="Date and time when the user was created.")
