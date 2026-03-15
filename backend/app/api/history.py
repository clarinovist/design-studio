"""Design History API: list and create history snapshots for a project."""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.core.database import get_db
from app.models.design_history import DesignHistory
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.error import ERROR_RESPONSES
from pydantic import BaseModel, Field

router = APIRouter(tags=["History"])


class DesignHistoryCreate(BaseModel):
    """
    Schema to create a new design history snapshot.
    """
    project_id: str = Field(..., description="ID of the project this history belongs to")
    background_url: str = Field(..., description="URL of the background image")
    text_layers: list = Field(..., description="List of text layers applied to the design")
    generation_params: Optional[dict] = Field(None, description="Parameters used during generation")


class DesignHistoryResponse(BaseModel):
    """
    Schema for returning a design history snapshot.
    """
    id: str = Field(..., description="History snapshot ID")
    project_id: str = Field(..., description="Associated project ID")
    background_url: str = Field(..., description="URL of the background image")
    text_layers: list = Field(..., description="Text layers applied to the design")
    generation_params: Optional[dict] = Field(None, description="Generation parameters")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


@router.get(
    "/{project_id}",
    response_model=list[DesignHistoryResponse],
    status_code=200,
    summary="List design history",
    description="Lists all design history snapshots for a specific project, ordered from newest to oldest.",
    responses={
        200: {"description": "History successfully retrieved"},
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def list_history(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all design history entries for a project, newest first."""
    result = await db.execute(
        select(DesignHistory)
        .where(DesignHistory.project_id == project_id)
        .order_by(desc(DesignHistory.created_at))
    )
    entries = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "project_id": str(e.project_id),
            "background_url": e.background_url,
            "text_layers": e.text_layers,
            "generation_params": e.generation_params,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


@router.post(
    "/",
    response_model=DesignHistoryResponse,
    status_code=201,
    summary="Create history snapshot",
    description="Saves a new snapshot of the design state to history, allowing the user to view or revert to previous variations.",
    responses={
        201: {"description": "History snapshot created successfully"},
        400: ERROR_RESPONSES[400],
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def create_history(
    data: DesignHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a design history snapshot for a project."""
    entry = DesignHistory(
        project_id=data.project_id,
        background_url=data.background_url,
        text_layers=data.text_layers,
        generation_params=data.generation_params,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return {
        "id": str(entry.id),
        "project_id": str(entry.project_id),
        "background_url": entry.background_url,
        "text_layers": entry.text_layers,
        "generation_params": entry.generation_params,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }
