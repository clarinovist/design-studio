from __future__ import annotations

from typing import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, ValidationError
from app.models.ai_tool_job import AiToolJob
from app.models.ai_tool_result import AiToolResult
from app.models.brand_kit import BrandKit
from app.models.job import Job
from app.models.user import User
from app.schemas.error import ERROR_RESPONSES
from app.services.storage_service import create_presigned_url, extract_storage_key

router = APIRouter(tags=["Assets"])


class AssetSignRequest(BaseModel):
    url: str


class AssetSignResponse(BaseModel):
    url: str
    expires_in_seconds: int


def _url_variants(url: str) -> set[str]:
    base = (url or "").strip()
    if not base:
        return set()
    variants = {base}
    variants.add(base.split("?", 1)[0])
    return variants


def _is_owner_via_keys(target_key: str | None, candidate_urls: Iterable[str]) -> bool:
    if not target_key:
        return False
    for candidate in candidate_urls:
        candidate_key = extract_storage_key(candidate)
        if candidate_key and candidate_key == target_key:
            return True
    return False


async def _collect_user_asset_urls(db: AsyncSession, user_id: UUID) -> list[str]:
    urls: list[str] = []

    job_rows = (await db.execute(select(Job.result_url, Job.reference_image_url).where(Job.user_id == user_id))).all()
    for result_url, reference_image_url in job_rows:
        if result_url:
            urls.append(result_url)
        if reference_image_url:
            urls.append(reference_image_url)

    tool_result_rows = (await db.execute(select(AiToolResult.result_url).where(AiToolResult.user_id == user_id))).scalars().all()
    urls.extend([url for url in tool_result_rows if url])

    tool_job_rows = (await db.execute(select(AiToolJob.result_url).where(AiToolJob.user_id == user_id))).scalars().all()
    urls.extend([url for url in tool_job_rows if url])

    kits = (await db.execute(select(BrandKit.logo_url, BrandKit.logos).where(BrandKit.user_id == user_id))).all()
    for logo_url, logos in kits:
        if logo_url:
            urls.append(logo_url)
        if isinstance(logos, list):
            urls.extend([logo for logo in logos if isinstance(logo, str) and logo])

    return urls


async def _user_owns_asset_url(db: AsyncSession, user_id: UUID, url: str) -> bool:
    normalized = (url or "").strip()
    if not normalized:
        return False

    target_key = extract_storage_key(normalized)
    if not target_key:
        return False

    # Fast-path for per-user upload prefixes.
    user_prefix = f"uploads/{user_id}"
    if target_key.startswith(user_prefix):
        return True

    candidate_urls = await _collect_user_asset_urls(db, user_id)

    # Exact URL match handles legacy/public URLs when still unchanged.
    target_variants = _url_variants(normalized)
    if any(candidate in target_variants for candidate in candidate_urls):
        return True

    return _is_owner_via_keys(target_key, candidate_urls)


@router.post(
    "/sign",
    response_model=AssetSignResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign Asset URL",
    description="Generates a temporary signed URL for a user-owned stored asset.",
    responses=ERROR_RESPONSES,
)
async def sign_asset_url(
    payload: AssetSignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw_url = (payload.url or "").strip()
    if not raw_url:
        raise ValidationError(detail="Asset URL is required.")

    key = extract_storage_key(raw_url)
    if not key:
        raise ValidationError(detail="Unsupported asset URL format.")

    owned = await _user_owns_asset_url(db, current_user.id, raw_url)
    if not owned:
        raise ForbiddenError(detail="Asset does not belong to current user.")

    from app.core.config import settings

    ttl_seconds = max(int(settings.STORAGE_SIGNED_URL_TTL_SECONDS or 900), 60)
    signed_url = create_presigned_url(key, expires_seconds=ttl_seconds)

    return AssetSignResponse(url=signed_url, expires_in_seconds=ttl_seconds)
