from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.workers.ai_tool_jobs_runner import _sync_usage_for_completed_job


@pytest.mark.asyncio
@patch("app.workers.ai_tool_jobs_runner.mark_ai_tool_usage_from_status", new_callable=AsyncMock)
@patch("app.workers.ai_tool_jobs_runner.AsyncSessionLocal")
async def test_sync_usage_for_completed_job_marks_succeeded(
    mock_session_local,
    mock_mark_usage,
):
    session = AsyncMock()
    session.get = AsyncMock(return_value=SimpleNamespace(status="completed"))
    mock_session_local.return_value.__aenter__.return_value = session

    await _sync_usage_for_completed_job("job-1")

    mock_mark_usage.assert_awaited_once()
    kwargs = mock_mark_usage.await_args.kwargs
    assert kwargs["ai_tool_job_id"] == "job-1"
    assert kwargs["status"] == "completed"
    assert kwargs["metadata"] == {"actual_cost_source": "missing_from_provider"}
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.workers.ai_tool_jobs_runner.mark_ai_tool_usage_from_status", new_callable=AsyncMock)
@patch("app.workers.ai_tool_jobs_runner.AsyncSessionLocal")
async def test_sync_usage_for_completed_job_skips_non_completed_status(
    mock_session_local,
    mock_mark_usage,
):
    session = AsyncMock()
    session.get = AsyncMock(return_value=SimpleNamespace(status="failed"))
    mock_session_local.return_value.__aenter__.return_value = session

    await _sync_usage_for_completed_job("job-2")

    mock_mark_usage.assert_not_awaited()
    session.commit.assert_not_awaited()
