from types import SimpleNamespace

from app.services.ai_tool_job_service import serialize_job


def test_serialize_job_signs_result_url_and_meta(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.ai_tool_job_service.to_asset_response_url",
        lambda url: f"signed:{url}",
    )

    job = SimpleNamespace(
        id="abc",
        tool_name="batch",
        status="completed",
        progress_percent=100,
        phase_message="done",
        result_url="https://cdn.example.com/generated/result.jpg",
        error_message=None,
        cancel_requested=False,
        created_at=None,
        started_at=None,
        finished_at=None,
        payload_json={
            "_result_meta": {
                "item_results": [
                    {"filename": "a.png", "result_url": "https://cdn.example.com/generated/a.png"}
                ]
            }
        },
    )

    data = serialize_job(job)

    assert data["result_url"] == "signed:https://cdn.example.com/generated/result.jpg"
    assert data["result_meta"]["item_results"][0]["result_url"] == "signed:https://cdn.example.com/generated/a.png"
