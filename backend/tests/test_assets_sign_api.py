from app.api.assets import _is_owner_via_keys


def test_is_owner_via_keys_matches_same_key() -> None:
    target_key = "generated/abc123.jpg"
    candidate_urls = [
        "http://localhost:8000/static/uploads/generated/abc123.jpg",
        "http://localhost:8000/static/uploads/generated/other.jpg",
    ]

    assert _is_owner_via_keys(target_key, candidate_urls) is True


def test_is_owner_via_keys_returns_false_on_mismatch() -> None:
    target_key = "generated/not-owned.jpg"
    candidate_urls = [
        "http://localhost:8000/static/uploads/generated/abc123.jpg",
        "http://localhost:8000/static/uploads/generated/other.jpg",
    ]

    assert _is_owner_via_keys(target_key, candidate_urls) is False
