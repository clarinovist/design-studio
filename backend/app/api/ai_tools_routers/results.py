"""API endpoints for managing AI tool results (list & delete)."""

import logging
import uuid as uuid_mod
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.error import ERROR_RESPONSES
from app.api.deps import get_db
from app.api.rate_limit import rate_limit_dependency, rate_limit_reads
from app.models.user import User
from app.models.ai_tool_result import AiToolResult
from app.services.storage_service import to_asset_response_url

router = APIRouter(tags=["AI Tools"])
logger = logging.getLogger(__name__)


async def save_tool_result(
    db: AsyncSession,
    user_id,
    tool_name: str,
    result_url: str,
    file_size: int,
    input_summary: Optional[str] = None,
) -> str:
    """
    Helper: insert an AiToolResult record and return its ID as string.
    Called by individual tool endpoints after successful upload.
    """
    record = AiToolResult(
        user_id=user_id,
        tool_name=tool_name,
        result_url=result_url,
        file_size=file_size,
        input_summary=(input_summary or "")[:200],
    )
    db.add(record)
    await db.flush()  # get the id without committing (caller commits)
    return str(record.id)


@router.get(
    "/my-results",
    response_model=list,
    status_code=status.HTTP_200_OK,
    summary="List My AI Tool Results",
    description="Fetch saved AI tool results for the current user, newest first.",
    responses=ERROR_RESPONSES,
)
async def list_my_results(
    tool_name: Optional[str] = Query(None, description="Filter by tool name"),
    folder_id: Optional[str] = Query(None, description="Filter by folder ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(rate_limit_reads),
):
    """List saved AI tool results for the current user."""
    query = select(AiToolResult).where(AiToolResult.user_id == current_user.id)

    if tool_name:
        query = query.where(AiToolResult.tool_name == tool_name)

    if folder_id:
        try:
            import uuid
            f_uuid = uuid.UUID(folder_id)
            query = query.where(AiToolResult.folder_id == f_uuid)
        except ValueError:
            pass

    query = query.order_by(desc(AiToolResult.created_at)).offset(offset).limit(limit)

    result = await db.execute(query)
    records = result.scalars().all()

    return [
        {
            "id": str(r.id),
            "tool_name": r.tool_name,
            "result_url": to_asset_response_url(r.result_url) if r.result_url else None,
            "input_summary": r.input_summary,
            "file_size": r.file_size,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.delete(
    "/results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete AI Tool Result",
    description="Delete a saved AI tool result, remove from storage, and reclaim quota.",
    responses=ERROR_RESPONSES,
)
async def delete_tool_result(
    result_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(rate_limit_dependency),
):
    """Delete an AI tool result: remove from storage + reclaim quota."""
    try:
        rid = uuid_mod.UUID(result_id)
    except ValueError:
        raise ValidationError(detail="Invalid result ID format")

    result = await db.execute(
        select(AiToolResult).where(
            AiToolResult.id == rid, AiToolResult.user_id == current_user.id
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundError(detail="Result not found")

    # 1. Delete from storage
    from app.services.storage_service import delete_image

    await delete_image(record.result_url)

    # 2. Delete DB record first, then reconcile from authoritative rows.
    # Counter-based decrement can drift if a previous delete partially failed
    # or if the user's stored counter was already stale.
    await db.delete(record)
    await db.flush()

    # 3. Recalculate storage quota from remaining records.
    from app.services.storage_quota_service import recalculate_storage

    await recalculate_storage(current_user.id, db)
