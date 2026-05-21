"""Regression tests for storage quota reconciliation after delete flows."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.api.ai_tools_routers.results import delete_tool_result
from app.api.designs_routers.jobs import delete_job
from app.api.projects import delete_project
from app.models.user import User


def _result_with_scalar_one_or_none(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _result_with_scalars_all(values):
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


@pytest.mark.asyncio
async def test_delete_tool_result_recalculates_after_record_is_deleted():
    user = User(id=uuid4(), email="user@example.com")
    record = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        result_url="https://cdn.example.com/results/deleted.png",
        file_size=99_000_000,
    )
    db = AsyncMock()
    db.execute.return_value = _result_with_scalar_one_or_none(record)

    with (
        patch("app.services.storage_service.delete_image", new=AsyncMock()) as delete_image,
        patch("app.services.storage_quota_service.decrement_usage", new=AsyncMock()) as decrement_usage,
        patch("app.services.storage_quota_service.recalculate_storage", new=AsyncMock(return_value=0)) as recalculate_storage,
    ):
        await delete_tool_result(str(record.id), db=db, current_user=user)

    delete_image.assert_awaited_once_with(record.result_url)
    db.delete.assert_awaited_once_with(record)
    db.flush.assert_awaited_once()
    recalculate_storage.assert_awaited_once_with(user.id, db)
    decrement_usage.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_job_recalculates_after_job_is_deleted():
    user = User(id=uuid4(), email="user@example.com")
    job = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        result_url="https://cdn.example.com/jobs/deleted.png",
        file_size=42_000_000,
    )
    db = AsyncMock()
    db.execute.return_value = _result_with_scalar_one_or_none(job)

    with (
        patch("app.services.storage_service.delete_image", new=AsyncMock()) as delete_image,
        patch("app.services.storage_quota_service.decrement_usage", new=AsyncMock()) as decrement_usage,
        patch("app.services.storage_quota_service.recalculate_storage", new=AsyncMock(return_value=0)) as recalculate_storage,
    ):
        await delete_job(str(job.id), db=db, current_user=user)

    delete_image.assert_awaited_once_with(job.result_url)
    db.delete.assert_awaited_once_with(job)
    db.flush.assert_awaited_once()
    recalculate_storage.assert_awaited_once_with(user.id, db)
    decrement_usage.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_project_deletes_associated_jobs_before_recalculating_storage():
    user = User(id=uuid4(), email="user@example.com")
    project = SimpleNamespace(id=uuid4(), user_id=user.id)
    jobs = [
        SimpleNamespace(id=uuid4(), result_url="https://cdn.example.com/job-1.png", file_size=5_000_000),
        SimpleNamespace(id=uuid4(), result_url="https://cdn.example.com/job-2.png", file_size=3_000_000),
    ]
    db = AsyncMock()
    db.execute.side_effect = [
        _result_with_scalar_one_or_none(project),
        _result_with_scalars_all(jobs),
    ]

    with (
        patch("app.services.storage_service.delete_image", new=AsyncMock()) as delete_image,
        patch("app.services.storage_quota_service.decrement_usage", new=AsyncMock()) as decrement_usage,
        patch("app.services.storage_quota_service.recalculate_storage", new=AsyncMock(return_value=0)) as recalculate_storage,
    ):
        await delete_project(project.id, db=db, current_user=user)

    assert delete_image.await_count == 2
    delete_image.assert_any_await(jobs[0].result_url)
    delete_image.assert_any_await(jobs[1].result_url)
    deleted_objects = [call.args[0] for call in db.delete.await_args_list]
    assert jobs[0] in deleted_objects
    assert jobs[1] in deleted_objects
    assert project in deleted_objects
    db.flush.assert_awaited_once()
    recalculate_storage.assert_awaited_once_with(user.id, db)
    decrement_usage.assert_not_awaited()
