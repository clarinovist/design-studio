"""Lightweight language guardrails for LLM-generated marketing copy."""

from __future__ import annotations

import json
import re
from typing import Any

_CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
_ALLOWED_CHINESE_TERMS = {
    "shopee",
    "tiktok",
    "whatsapp",
}


def _iter_text_values(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _iter_text_values(nested)
    elif isinstance(value, (list, tuple, set)):
        for nested in value:
            yield from _iter_text_values(nested)


def contains_cjk_text(value: Any) -> bool:
    """Return True when any nested text contains Chinese/Japanese/Korean ideographs."""
    return any(_CJK_RE.search(text) is not None for text in _iter_text_values(value))


def should_enforce_indonesian(language: str | None) -> bool:
    """Treat empty/Indonesian-like language codes as Indonesian output targets."""
    normalized = (language or "id").strip().lower().replace("_", "-")
    return normalized in {"id", "id-id", "indonesia", "indonesian", "bahasa-indonesia"}


def assert_no_cjk_for_indonesian(value: Any, *, language: str | None, context: str) -> None:
    """Reject Mandarin/CJK leakage when the requested output language is Indonesian."""
    if not should_enforce_indonesian(language):
        return

    # JSON-serialize to keep the error deterministic while still allowing brand
    # names/platforms that are Latin text. CJK terms are not expected in the
    # current Indonesian-first beta output.
    if contains_cjk_text(value):
        raise ValueError(f"{context} contains CJK/Mandarin text for Indonesian output")


def indonesian_language_instruction(language: str | None) -> str:
    if should_enforce_indonesian(language):
        return (
            "LANGUAGE: Write all user-facing copy in natural Bahasa Indonesia. "
            "Do not use Mandarin, Chinese characters, Japanese kanji, or mixed CJK text. "
            "Keep brand names/platform names as originally provided."
        )
    return f"LANGUAGE: Write the copy in the requested language code '{language}'."


def preview_text(value: Any, limit: int = 400) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        text = str(value)
    return text if len(text) <= limit else f"{text[:limit]}…"
