from app.services.storage_service import to_asset_response_url


def test_to_asset_response_url_returns_original_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr("app.services.storage_service.settings.STORAGE_PRIVATE_URLS_ENABLED", False)
    source = "https://cdn.example.com/generated/file.jpg"
    assert to_asset_response_url(source) == source


def test_to_asset_response_url_returns_signed_when_enabled(monkeypatch) -> None:
    monkeypatch.setattr("app.services.storage_service.settings.STORAGE_PRIVATE_URLS_ENABLED", True)
    monkeypatch.setattr("app.services.storage_service.settings.S3_PUBLIC_URL", "https://cdn.example.com")
    monkeypatch.setattr("app.services.storage_service.settings.STORAGE_SIGNED_URL_TTL_SECONDS", 900)
    monkeypatch.setattr("app.services.storage_service.create_presigned_url", lambda key, expires_seconds=900: "https://signed.example.com/s")

    source = "https://cdn.example.com/generated/file.jpg"
    assert to_asset_response_url(source) == "https://signed.example.com/s"
