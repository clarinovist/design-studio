from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal
from uuid import UUID
from datetime import datetime


class ColorSwatch(BaseModel):
    """
    A specific color definition within a Brand Kit.
    """
    hex: str = Field(..., description="Hex color code, e.g., #FF5733", example="#FF5733")
    name: str = Field(..., description="Color name in Indonesian", example="Merah Utama")
    role: Literal["primary", "secondary", "accent", "background", "text"] = Field(
        ..., description="Logical role: primary, secondary, accent, background, text", example="primary"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hex": "#FF5733",
                "name": "Merah Utama",
                "role": "primary"
            }
        }
    )


class Typography(BaseModel):
    """
    Typography settings defining primary and secondary fonts for a Brand Kit.
    """
    primaryFont: Optional[str] = Field(None, description="Primary font family name", example="Inter")
    secondaryFont: Optional[str] = Field(None, description="Secondary font family name", example="Playfair Display")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "primaryFont": "Inter",
                "secondaryFont": "Playfair Display"
            }
        }
    )


class BrandKitBase(BaseModel):
    """
    Base properties for a Brand Kit.
    """
    name: str = Field(..., description="Name of the brand kit", example="Brand Kit Utama")
    logo_url: Optional[str] = Field(
        None, description="URL of the uploaded logo (legacy/single logo)", example="https://example.com/logo.png"
    )
    logos: Optional[List[str]] = Field(
        default_factory=list, description="List of logo URLs", example=["https://example.com/logo.png"]
    )
    colors: List[ColorSwatch] = Field(..., min_length=1, max_length=10, description="List of color swatches defining the brand's color palette")
    typography: Optional[Typography] = Field(None, description="Typography settings defining the brand's fonts")


class BrandKitCreate(BrandKitBase):
    """
    Schema for creating a new Brand Kit.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Brand Kit Utama",
                "logo_url": "https://example.com/logo.png",
                "logos": ["https://example.com/logo.png"],
                "colors": [
                    {
                        "hex": "#FF5733",
                        "name": "Merah Utama",
                        "role": "primary"
                    }
                ],
                "typography": {
                    "primaryFont": "Inter",
                    "secondaryFont": "Playfair Display"
                }
            }
        }
    )


class BrandKitUpdate(BaseModel):
    """
    Schema for updating an existing Brand Kit.
    """
    name: Optional[str] = Field(None, description="New name for the brand kit", example="Updated Brand Kit")
    logo_url: Optional[str] = Field(None, description="New primary logo URL", example="https://example.com/new-logo.png")
    logos: Optional[List[str]] = Field(None, description="Updated list of logo URLs", example=["https://example.com/new-logo.png"])
    colors: Optional[List[ColorSwatch]] = Field(None, description="Updated list of color swatches")
    typography: Optional[Typography] = Field(None, description="Updated typography settings")
    is_active: Optional[bool] = Field(None, description="Whether this brand kit is currently active for the user", example=True)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Brand Kit",
                "is_active": True
            }
        }
    )


class BrandKitResponse(BrandKitBase):
    """
    Response schema returning full details of a Brand Kit.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174000",
                "name": "Brand Kit Utama",
                "logo_url": "https://example.com/logo.png",
                "logos": ["https://example.com/logo.png"],
                "colors": [
                    {
                        "hex": "#FF5733",
                        "name": "Merah Utama",
                        "role": "primary"
                    }
                ],
                "typography": {
                    "primaryFont": "Inter",
                    "secondaryFont": "Playfair Display"
                },
                "is_active": True,
                "created_at": "2023-01-01T12:00:00Z"
            }
        }
    )

    id: UUID = Field(..., description="Unique Brand Kit identifier")
    user_id: UUID = Field(..., description="User ID that owns this Brand Kit")
    is_active: bool = Field(..., description="Whether this brand kit is currently active")
    created_at: datetime = Field(..., description="Creation timestamp")


class ColorExtractionResponse(BaseModel):
    """
    Schema for returning colors extracted from an uploaded image.
    """
    colors: List[ColorSwatch] = Field(..., description="List of color swatches extracted from the image")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "colors": [
                    {
                        "hex": "#FF5733",
                        "name": "Dominant Red",
                        "role": "primary"
                    }
                ]
            }
        }
    )
