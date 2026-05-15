from app.api.projects import _project_canvas_with_response_url


def test_project_canvas_with_response_url_preserves_without_background() -> None:
    canvas = {"elements": []}
    assert _project_canvas_with_response_url(canvas) == canvas


def test_project_canvas_with_response_url_updates_background(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.projects.to_asset_response_url",
        lambda url: "https://signed.example.com/a",
    )
    canvas = {"elements": [], "backgroundUrl": "https://cdn.example.com/generated/abc.jpg"}

    updated = _project_canvas_with_response_url(canvas)

    assert updated is not None
    assert updated["backgroundUrl"] == "https://signed.example.com/a"
    assert canvas["backgroundUrl"] == "https://cdn.example.com/generated/abc.jpg"
