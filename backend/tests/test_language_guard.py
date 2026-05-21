from app.services.language_guard import (
    assert_no_cjk_for_indonesian,
    contains_cjk_text,
    indonesian_language_instruction,
    should_enforce_indonesian,
)


def test_contains_cjk_text_detects_nested_mandarin_copy():
    payload = {
        "pages": [
            {
                "content": {
                    "title": "新品上市",
                    "cta": "BELI SEKARANG",
                }
            }
        ]
    }

    assert contains_cjk_text(payload) is True


def test_assert_no_cjk_rejects_indonesian_output_leakage():
    payload = {"headline": "新品上市", "cta": "BELI SEKARANG"}

    try:
        assert_no_cjk_for_indonesian(
            payload,
            language="id",
            context="test response",
        )
    except ValueError as exc:
        assert "CJK/Mandarin" in str(exc)
    else:
        raise AssertionError("Expected Mandarin leakage to be rejected")


def test_assert_no_cjk_allows_clean_indonesian_copy():
    payload = {
        "headline": "Promo Spesial Hari Ini",
        "subline": "Kualitas premium untuk kebutuhan harian Anda.",
        "cta": "BELI SEKARANG",
    }

    assert_no_cjk_for_indonesian(payload, language="id", context="test response")


def test_language_instruction_defaults_to_indonesian_guard():
    assert should_enforce_indonesian("id-ID") is True
    instruction = indonesian_language_instruction("id")
    assert "Bahasa Indonesia" in instruction
    assert "Mandarin" in instruction
