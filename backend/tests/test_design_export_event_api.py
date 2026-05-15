from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.designs_routers.exports import ExportEventPayload, log_export_event


@pytest.mark.asyncio
async def test_log_export_event_succeeds_with_valid_payload() -> None:
    user_id = uuid4()
    design_id = uuid4()
    job_id = uuid4()

    db = MagicMock()
    db.commit = AsyncMock()

    project_result = MagicMock()
    project_result.scalar_one_or_none.return_value = design_id
    ai_tool_job_result = MagicMock()
    ai_tool_job_result.scalar_one_or_none.return_value = job_id
    db.execute = AsyncMock(side_effect=[project_result, ai_tool_job_result])

    with patch("app.api.designs_routers.exports.log_design_export", new_callable=AsyncMock) as log_export:
        log_export.return_value = SimpleNamespace(id=uuid4())

        response = await log_export_event(
            design_id=design_id,
            body=ExportEventPayload(
                export_format="png",
                target_platform=None,
                job_id=str(job_id),
                source="editor",
            ),
            current_user=SimpleNamespace(id=user_id),
            db=db,
        )

    assert response["success"] is True
    log_export.assert_awaited_once()
    assert log_export.await_args.kwargs["job_id"] == job_id
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_export_event_rejects_invalid_job_id() -> None:
    db = MagicMock()
    db.commit = AsyncMock()
    project_result = MagicMock()
    project_result.scalar_one_or_none.return_value = uuid4()
    db.execute = AsyncMock(return_value=project_result)

    with pytest.raises(HTTPException) as exc_info:
        await log_export_event(
            design_id=uuid4(),
            body=ExportEventPayload(
                export_format="png",
                target_platform=None,
                job_id="not-a-uuid",
                source="editor",
            ),
            current_user=SimpleNamespace(id=uuid4()),
            db=db,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "job_id must be a valid UUID"
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_log_export_event_ignores_non_ai_tool_job_id() -> None:
    user_id = uuid4()
    design_id = uuid4()
    foreign_job_id = uuid4()

    db = MagicMock()
    db.commit = AsyncMock()
    project_result = MagicMock()
    project_result.scalar_one_or_none.return_value = design_id
    ai_tool_job_result = MagicMock()
    ai_tool_job_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(side_effect=[project_result, ai_tool_job_result])

    with patch("app.api.designs_routers.exports.log_design_export", new_callable=AsyncMock) as log_export:
        log_export.return_value = SimpleNamespace(id=uuid4())

        await log_export_event(
            design_id=design_id,
            body=ExportEventPayload(
                export_format="png",
                job_id=str(foreign_job_id),
            ),
            current_user=SimpleNamespace(id=user_id),
            db=db,
        )

    assert log_export.await_args.kwargs["job_id"] is None


@pytest.mark.asyncio
async def test_log_export_event_rejects_non_owned_design() -> None:
    db = MagicMock()
    db.commit = AsyncMock()
    project_result = MagicMock()
    project_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=project_result)

    with pytest.raises(HTTPException) as exc_info:
        await log_export_event(
            design_id=uuid4(),
            body=ExportEventPayload(export_format="png"),
            current_user=SimpleNamespace(id=uuid4()),
            db=db,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Design not found"
    db.commit.assert_not_awaited()
