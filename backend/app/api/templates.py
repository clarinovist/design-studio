"""Templates API: list and retrieve design templates."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.template import Template
from app.schemas.error import ERROR_RESPONSES
from pydantic import BaseModel, Field

router = APIRouter(tags=["Templates"])


class TemplateResponse(BaseModel):
    """
    Schema representing a design template.
    """
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category (e.g., social, ad)")
    aspect_ratio: str = Field(..., description="Canvas aspect ratio (e.g., 1:1, 16:9)")
    style: str = Field(..., description="Visual style of the template")
    default_text_layers: list = Field(..., description="Default text layer configuration")
    prompt_suffix: Optional[str] = Field(None, description="Prompt modifiers added to generation")
    thumbnail_url: Optional[str] = Field(None, description="URL to a thumbnail preview image")


@router.get(
    "/",
    response_model=list[TemplateResponse],
    status_code=200,
    summary="List templates",
    description="Lists available design templates, optionally filtering by category or aspect ratio.",
    responses={
        200: {"description": "Templates successfully retrieved"},
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def list_templates(
    category: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all templates, optionally filtered by category or aspect_ratio."""
    query = select(Template)

    if category:
        query = query.where(Template.category == category)
    if aspect_ratio:
        query = query.where(Template.aspect_ratio == aspect_ratio)

    result = await db.execute(query)
    templates = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "name": t.name,
            "category": t.category,
            "aspect_ratio": t.aspect_ratio,
            "style": t.style,
            "default_text_layers": t.default_text_layers,
            "prompt_suffix": t.prompt_suffix,
            "thumbnail_url": t.thumbnail_url,
        }
        for t in templates
    ]


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=200,
    summary="Get template details",
    description="Retrieves the full details of a specific design template by its ID.",
    responses={
        200: {"description": "Template retrieved successfully"},
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single template by ID."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": str(template.id),
        "name": template.name,
        "category": template.category,
        "aspect_ratio": template.aspect_ratio,
        "style": template.style,
        "default_text_layers": template.default_text_layers,
        "prompt_suffix": template.prompt_suffix,
        "thumbnail_url": template.thumbnail_url,
    }
