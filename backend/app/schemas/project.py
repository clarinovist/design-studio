from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID


class CanvasElementSchema(BaseModel):
    """
    Schema representing a single element on the project canvas (e.g., text, image).
    """
    id: str = Field(..., description="Unique identifier for the canvas element", example="el_12345")
    type: str = Field(..., description="Type of the element (e.g., 'text', 'image')", example="text")
    x: float = Field(..., description="Horizontal position", example=10.5)
    y: float = Field(..., description="Vertical position", example=20.5)
    width: Optional[float] = Field(None, description="Width of the element", example=100.0)
    height: Optional[float] = Field(None, description="Height of the element", example=50.0)
    rotation: Optional[float] = Field(0, description="Rotation angle in degrees", example=0.0)
    text: Optional[str] = Field(None, description="Text content if type is 'text'", example="Hello World")
    fontFamily: Optional[str] = Field(None, description="Font family if type is 'text'", example="Inter")
    fontSize: Optional[int] = Field(None, description="Font size in pixels", example=24)
    fill: Optional[str] = Field(None, description="Fill color (hex or rgba)", example="#FFFFFF")
    align: Optional[str] = Field(None, description="Text alignment", example="center")

    # Add other flexible properties using extra fields if necessary
    model_config = ConfigDict(extra="allow")


class ProjectCanvasState(BaseModel):
    """
    Schema representing the complete state of a project canvas.
    """
    elements: List[Dict[str, Any]] = Field(..., description="List of canvas elements")
    backgroundUrl: Optional[str] = Field(None, description="URL of the canvas background image", example="https://example.com/bg.png")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "elements": [
                    {
                        "id": "el_123",
                        "type": "text",
                        "x": 100,
                        "y": 100,
                        "text": "Hello"
                    }
                ],
                "backgroundUrl": "https://example.com/bg.png"
            }
        }
    )


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    """
    title: Optional[str] = Field(None, description="Updated project title", example="My New Project")
    canvas_state: Optional[Dict[str, Any]] = Field(None, description="Updated JSON object representing the canvas state")
    status: Optional[str] = Field(None, description="Updated status (e.g., 'draft', 'published')", example="draft")
    aspect_ratio: Optional[str] = Field(None, description="Updated aspect ratio", example="16:9")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "status": "published"
            }
        }
    )


class ProjectResponse(BaseModel):
    """
    Schema for a project response, including its current state.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174000",
                "title": "Summer Sale Promo",
                "status": "draft",
                "aspect_ratio": "1:1",
                "canvas_state": {"elements": []},
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T12:00:00Z"
            }
        }
    )

    id: UUID = Field(..., description="Unique project identifier")
    user_id: UUID = Field(..., description="User ID that owns this project")
    title: str = Field(..., description="Project title")
    status: str = Field(..., description="Current status of the project")
    aspect_ratio: str = Field(..., description="Aspect ratio of the project canvas")
    canvas_state: Optional[Dict[str, Any]] = Field(None, description="JSON object representing the canvas state")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
