"""Design export event tracking API."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.ai_tool_job import AiToolJob
from app.models.project import Project
from app.models.user import User
from app.services.design_export_service import log_design_export
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/designs", tags=["designs-exports"])


class ExportEventPayload(BaseModel):
    export_format: str
    target_platform: str | None = None
    job_id: str | None = None
    source: str | None = None


@router.post("/{design_id}/export-event", status_code=status.HTTP_201_CREATED)
async def log_export_event(
    design_id: UUID,
    body: ExportEventPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a design export event.

    This endpoint records when a user exports a design, enabling backend-owned
    measurement of the generation-to-export funnel without dependency on user
    feedback submission.

    Request body:
    {
        "export_format": "png|jpg|pdf|etc",
        "target_platform": "shopee|tokopedia|etc|null",
        "job_id": "uuid|null"
    }

    Returns:
        {"export_id": "uuid", "success": true, "message": "Export logged"}
    """
    export_format = body.export_format
    target_platform = body.target_platform
    job_id = body.job_id

    if not export_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="export_format is required",
        )

    owned_project = await db.execute(
        select(Project.id).where(
            Project.id == design_id,
            Project.user_id == current_user.id,
        )
    )
    if owned_project.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found",
        )

    parsed_job_id = None
    if job_id:
        try:
            candidate_job_id = UUID(job_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id must be a valid UUID",
            ) from exc

        ai_tool_job = await db.execute(
            select(AiToolJob.id).where(
                AiToolJob.id == candidate_job_id,
                AiToolJob.user_id == current_user.id,
            )
        )
        if ai_tool_job.scalar_one_or_none() is not None:
            parsed_job_id = candidate_job_id

    try:
        export = await log_design_export(
            user_id=current_user.id,
            design_id=design_id,
            export_format=export_format,
            target_platform=target_platform,
            job_id=parsed_job_id,
            success=True,
            db=db,
        )

        await db.commit()

        return {
            "export_id": str(export.id),
            "success": True,
            "message": f"Export logged as {export_format}",
        }
    except Exception as exc:
        logger.error(
            "export_event.error design_id=%s user_id=%s error=%s",
            design_id,
            current_user.id,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log export event",
        ) from exc
