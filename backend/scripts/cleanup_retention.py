"""Retention cleanup utility with safe dry-run default.

Usage:
    python -m scripts.cleanup_retention --dry-run
    python -m scripts.cleanup_retention --execute
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from sqlalchemy import or_, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.ai_tool_job import AiToolJob
from app.models.ai_tool_result import AiToolResult
from app.models.user import User
from app.services.storage_service import delete_image

logger = logging.getLogger(__name__)

DEFAULT_FAILED_JOB_DAYS = 30
DEFAULT_OLD_TERMINAL_JOB_DAYS = 120
DEFAULT_ORPHAN_RESULT_DAYS = 30

# Conservative default: temporary/transient prefixes only.
TEMP_PREFIXES = {
    "retouch_input",
    "retouch_relight_input",
    "magic_eraser_mask_prepared",
    "bgswap_mask_ultra",
    "references",
}

GENERATED_PREFIXES = {
    "generated",
}


@dataclass
class CleanupSummary:
    stale_failed_jobs: int = 0
    old_terminal_jobs: int = 0
    orphaned_results: int = 0
    asset_candidates: int = 0
    files_deleted: int = 0
    db_rows_touched: int = 0
    failures: int = 0


def _extract_storage_key(url: str) -> str | None:
    if not url:
        return None

    base = settings.BACKEND_BASE_URL.rstrip("/")
    local_prefix = f"{base}/static/uploads/"
    if url.startswith(local_prefix):
        return url.replace(local_prefix, "", 1)

    if settings.S3_PUBLIC_URL:
        s3_public_prefix = settings.S3_PUBLIC_URL.rstrip("/") + "/"
        if url.startswith(s3_public_prefix):
            return url.replace(s3_public_prefix, "", 1)

    if settings.S3_ENDPOINT and settings.S3_BUCKET:
        endpoint_prefix = (
            f"{settings.S3_ENDPOINT.rstrip('/')}/{settings.S3_BUCKET}/"
        )
        if url.startswith(endpoint_prefix):
            return url.replace(endpoint_prefix, "", 1)

    if settings.S3_BUCKET:
        aws_pattern = rf"https?://{re.escape(settings.S3_BUCKET)}\\.s3\\.amazonaws\\.com/(.+)"
        aws_match = re.match(aws_pattern, url)
        if aws_match:
            return aws_match.group(1)

    return None


def _is_cleanup_candidate_key(key: str, include_generated: bool) -> bool:
    first_prefix = (key.split("/", 1)[0] or "").strip().lower()
    allowed_prefixes = set(TEMP_PREFIXES)
    if include_generated:
        allowed_prefixes.update(GENERATED_PREFIXES)
    return first_prefix in allowed_prefixes


def _iter_string_values(payload: Any) -> Iterable[str]:
    if isinstance(payload, str):
        yield payload
        return
    if isinstance(payload, dict):
        for value in payload.values():
            yield from _iter_string_values(value)
        return
    if isinstance(payload, list):
        for item in payload:
            yield from _iter_string_values(item)


def _collect_job_asset_urls(job: AiToolJob) -> set[str]:
    urls: set[str] = set()
    if job.result_url:
        urls.add(job.result_url)

    for value in _iter_string_values(job.payload_json or {}):
        if value.startswith("http://") or value.startswith("https://"):
            urls.add(value)

    return urls


async def run_cleanup(
    *,
    execute: bool,
    failed_job_days: int,
    old_terminal_job_days: int,
    orphan_result_days: int,
    include_generated: bool,
    include_completed_jobs: bool,
) -> int:
    summary = CleanupSummary()

    now = datetime.now(timezone.utc)
    failed_cutoff = now - timedelta(days=failed_job_days)
    old_terminal_cutoff = now - timedelta(days=old_terminal_job_days)
    orphan_result_cutoff = now - timedelta(days=orphan_result_days)

    async with AsyncSessionLocal() as session:
        stale_failed_query = select(AiToolJob).where(
            AiToolJob.created_at < failed_cutoff,
            AiToolJob.status.in_(["failed", "cancelled", "canceled"]),
        )
        stale_failed_jobs = (await session.execute(stale_failed_query)).scalars().all()

        old_terminal_jobs: list[AiToolJob] = []
        if include_completed_jobs:
            old_terminal_query = select(AiToolJob).where(
                AiToolJob.created_at < old_terminal_cutoff,
                AiToolJob.status.in_(["completed"]),
            )
            old_terminal_jobs = (await session.execute(old_terminal_query)).scalars().all()

        orphaned_results_query = (
            select(AiToolResult)
            .outerjoin(User, AiToolResult.user_id == User.id)
            .where(
                AiToolResult.created_at < orphan_result_cutoff,
                or_(User.id.is_(None), AiToolResult.result_url.is_(None), AiToolResult.result_url == ""),
            )
        )
        orphaned_results = (await session.execute(orphaned_results_query)).scalars().all()

        summary.stale_failed_jobs = len(stale_failed_jobs)
        summary.old_terminal_jobs = len(old_terminal_jobs)
        summary.orphaned_results = len(orphaned_results)

        job_map: dict[str, AiToolJob] = {}
        for job in stale_failed_jobs + old_terminal_jobs:
            job_map[str(job.id)] = job

        candidate_urls: set[str] = set()
        for job in job_map.values():
            for url in _collect_job_asset_urls(job):
                key = _extract_storage_key(url)
                if key and _is_cleanup_candidate_key(key, include_generated):
                    candidate_urls.add(url)

        for result in orphaned_results:
            if result.result_url:
                key = _extract_storage_key(result.result_url)
                if key and _is_cleanup_candidate_key(key, include_generated):
                    candidate_urls.add(result.result_url)

        summary.asset_candidates = len(candidate_urls)

        logger.info("=" * 72)
        logger.info("Retention cleanup mode: %s", "EXECUTE" if execute else "DRY-RUN")
        logger.info("- stale failed/cancelled ai_tool_jobs: %s", summary.stale_failed_jobs)
        logger.info(
            "- old completed ai_tool_jobs: %s (enabled=%s)",
            summary.old_terminal_jobs,
            include_completed_jobs,
        )
        logger.info("- orphaned ai_tool_results: %s", summary.orphaned_results)
        logger.info("- asset delete candidates: %s", summary.asset_candidates)

        if execute:
            for url in sorted(candidate_urls):
                try:
                    deleted = await delete_image(url)
                    if deleted:
                        summary.files_deleted += 1
                    else:
                        summary.failures += 1
                        logger.warning("Failed to delete file for URL: %s", url)
                except Exception as exc:  # defensive cleanup path
                    summary.failures += 1
                    logger.exception("Error deleting file %s: %s", url, exc)

            try:
                for result in orphaned_results:
                    await session.delete(result)
                    summary.db_rows_touched += 1

                for job in job_map.values():
                    await session.delete(job)
                    summary.db_rows_touched += 1

                await session.commit()
            except Exception as exc:
                await session.rollback()
                summary.failures += 1
                logger.exception("DB cleanup failed; rolled back. Error: %s", exc)

        logger.info("=" * 72)
        logger.info("Cleanup summary")
        logger.info("- candidates found: %s", summary.stale_failed_jobs + summary.old_terminal_jobs + summary.orphaned_results)
        logger.info("- files deleted: %s", summary.files_deleted)
        logger.info("- db rows touched: %s", summary.db_rows_touched)
        logger.info("- failures: %s", summary.failures)
        logger.info("=" * 72)

    # In dry-run this is always success. In execute, return non-zero on failure.
    return 0 if (not execute or summary.failures == 0) else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cleanup old AI job/result data and temporary assets (dry-run by default)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and print summary only (default behavior if --execute is not set).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply deletions after candidates are reviewed.",
    )
    parser.add_argument(
        "--failed-job-days",
        type=int,
        default=DEFAULT_FAILED_JOB_DAYS,
        help=f"Delete failed/cancelled ai_tool_jobs older than this many days (default: {DEFAULT_FAILED_JOB_DAYS}).",
    )
    parser.add_argument(
        "--old-terminal-job-days",
        type=int,
        default=DEFAULT_OLD_TERMINAL_JOB_DAYS,
        help=f"Age threshold for completed ai_tool_jobs when --include-completed-jobs is set (default: {DEFAULT_OLD_TERMINAL_JOB_DAYS}).",
    )
    parser.add_argument(
        "--include-completed-jobs",
        action="store_true",
        help="Include completed ai_tool_jobs in cleanup candidates (disabled by default).",
    )
    parser.add_argument(
        "--orphan-result-days",
        type=int,
        default=DEFAULT_ORPHAN_RESULT_DAYS,
        help=f"Delete orphaned ai_tool_results older than this many days (default: {DEFAULT_ORPHAN_RESULT_DAYS}).",
    )
    parser.add_argument(
        "--include-generated-prefix",
        action="store_true",
        help="Also include generated/* assets in deletion candidates (disabled by default).",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    execute = bool(args.execute)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if execute and args.dry_run:
        logger.warning("Both --dry-run and --execute provided. Proceeding with --execute.")

    return asyncio.run(
        run_cleanup(
            execute=execute,
            failed_job_days=args.failed_job_days,
            old_terminal_job_days=args.old_terminal_job_days,
            orphan_result_days=args.orphan_result_days,
            include_generated=args.include_generated_prefix,
            include_completed_jobs=args.include_completed_jobs,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
