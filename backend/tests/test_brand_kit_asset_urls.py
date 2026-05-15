from types import SimpleNamespace
from uuid import uuid4

from app.api.brand_kits import _serialize_brand_kit_response


def test_serialize_brand_kit_response_signs_logo_urls(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.brand_kits.to_asset_response_url",
        lambda url: f"signed:{url}",
    )

    kit = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        name="Kit A",
        logo_url="https://cdn.example.com/generated/logo.png",
        logos=["https://cdn.example.com/generated/logo.png", "https://cdn.example.com/generated/logo2.png"],
        colors=[{"hex": "#000000", "name": "Hitam", "role": "text"}],
        typography={"primaryFont": "Inter"},
        brand_strategy={"tone": "friendly"},
        is_active=True,
        created_at=None,
        folder_id=None,
    )

    data = _serialize_brand_kit_response(kit)

    assert data.logo_url == "signed:https://cdn.example.com/generated/logo.png"
    assert data.logos[0] == "signed:https://cdn.example.com/generated/logo.png"
    assert data.logos[1] == "signed:https://cdn.example.com/generated/logo2.png"
