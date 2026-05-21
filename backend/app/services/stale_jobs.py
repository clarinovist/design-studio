"""Utilities for timing out generation jobs that outlive the worker window."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_tool_job import AiToolJob
from app.models.job import Job

_STALE_STATUSES = ("queued", "processing")


def stale_job_cutoff(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current - timedelta(minutes=max(settings.JOB_STALE_TIMEOUT_MINUTES, 1))


async def expire_stale_generation_jobs(db: AsyncSession, *, now: datetime | None = None) -> int:
    """Mark old design generation jobs as failed so users stop polling forever."""
    cutoff = stale_job_cutoff(now)
    result = await db.execute(
        update(Job)
        .where(Job.status.in_(_STALE_STATUSES), Job.created_at < cutoff)
        .values(
            status="failed",
            error_message=(
                "Job timed out before completion. Please create a new generation."
            ),
            completed_at=now or datetime.now(timezone.utc),
        )
    )
    await db.commit()
    return int(getattr(result, "rowcount", 0) or 0)


async def expire_stale_ai_tool_jobs(db: AsyncSession, *, now: datetime | None = None) -> int:
    """Mark old AI tool jobs as failed so tool history does not stay stuck."""
    cutoff = stale_job_cutoff(now)
    result = await db.execute(
        update(AiToolJob)
        .where(AiToolJob.status.in_(_STALE_STATUSES), AiToolJob.created_at < cutoff)
        .values(
            status="failed",
            error_message=(
                "Job timed out before completion. Please create a new generation."
            ),
            finished_at=now or datetime.now(timezone.utc),
            progress_percent=100,
        )
    )
    await db.commit()
    return int(getattr(result, "rowcount", 0) or 0)
