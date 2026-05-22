from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional

class AdCreatorRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded product image")
    brief: Optional[str] = Field(None, description="Optional brief for the advertisement")
    brand_kit_id: Optional[str] = Field(None, description="Optional brand kit ID to apply colors and fonts")
    reference_focus: Literal["auto", "human", "object"] = Field(
        "auto",
        description="How strongly to preserve reference subject identity when generating backgrounds",
    )

class AdConcept(BaseModel):
    id: str = Field(..., description="Concept/Style ID (e.g., minimalist, bold, cinematic)")
    concept_name: str = Field(..., description="Human readable concept name")
    image_url: str = Field(..., description="Generated image URL")
    headline: str = Field(..., description="Suggested headline")
    tagline: str = Field(..., description="Suggested tagline")
    call_to_action: str = Field(..., description="Suggested call to action")

class AdCreatorResponse(BaseModel):
    foreground_url: str = Field(..., description="URL of the product with background removed")
    concepts: List[AdConcept]

class BatchResizeRequest(BaseModel):
    image_url: str = Field(..., description="Original image URL to be resized")
    target_sizes: List[str] = Field(..., description="List of target aspect ratios or platforms (e.g., '1:1', '9:16', '16:9')")
    reference_focus: Literal["auto", "human", "object"] = Field(
        "auto",
        description="How strongly to preserve human/object identity during outpaint resize",
    )

class BatchResizeResponse(BaseModel):
    results: Dict[str, str] = Field(..., description="Mapping of target size to resized image URL")
