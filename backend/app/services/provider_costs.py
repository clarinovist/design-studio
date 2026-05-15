"""Provider cost extraction and fallback estimation helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


_DECIMAL_PLACES = Decimal("0.000001")


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if amount < 0:
        return None
    return amount.quantize(_DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def _read_nested(data: Any, path: tuple[str, ...]) -> Any:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def extract_actual_cost_usd(provider_result: Any) -> Decimal | None:
    """Extract provider-returned actual USD cost from common payload shapes."""
    if provider_result is None:
        return None

    candidate_paths = (
        ("actual_cost",),
        ("cost",),
        ("cost_usd",),
        ("total_cost",),
        ("usage", "cost"),
        ("usage", "cost_usd"),
        ("usage", "total_cost"),
        ("billing", "actual_cost"),
        ("billing", "cost_usd"),
        ("metrics", "cost_usd"),
    )

    for path in candidate_paths:
        raw = _read_nested(provider_result, path)
        parsed = _to_decimal(raw)
        if parsed is not None:
            return parsed

    return None


def estimate_ai_cost_usd(
    operation: str,
    model: str | None,
    quality: str | None,
    count: int = 1,
) -> Decimal | None:
    """Estimate USD cost for margin monitoring when provider cost is missing."""
    normalized_operation = (operation or "").strip().lower()
    normalized_model = (model or "").strip().lower()
    normalized_quality = (quality or "auto").strip().lower()

    base_by_operation: dict[str, Decimal] = {
        "generate_design": Decimal("0.020000"),
        "redesign": Decimal("0.015000"),
        "background_swap": Decimal("0.010000"),
        "product_scene": Decimal("0.012000"),
        "remove_background": Decimal("0.004000"),
        "id_photo": Decimal("0.008000"),
        "upscale": Decimal("0.006000"),
        "magic_eraser": Decimal("0.010000"),
        "text_banner": Decimal("0.009000"),
        "generative_expand": Decimal("0.011000"),
        "watermark": Decimal("0.003000"),
    }

    if normalized_operation.startswith("batch:"):
        normalized_operation = normalized_operation.split(":", 1)[1]

    base_cost = base_by_operation.get(normalized_operation)
    if base_cost is None:
        return None

    quality_multiplier: dict[str, Decimal] = {
        "basic": Decimal("0.80"),
        "pro": Decimal("1.00"),
        "standard": Decimal("1.00"),
        "auto": Decimal("1.00"),
        "ultra": Decimal("1.85"),
    }
    model_multiplier = Decimal("1.00")
    if "gpt-image-2" in normalized_model:
        model_multiplier = Decimal("1.70")

    qty = max(int(count or 1), 1)
    multiplier = quality_multiplier.get(normalized_quality, Decimal("1.00")) * model_multiplier
    estimated = (base_cost * multiplier) * Decimal(qty)
    return estimated.quantize(_DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def sum_actual_cost_usd(provider_results: list[Any]) -> Decimal | None:
    """Sum all provider-returned actual costs; returns None if none are available."""
    total = Decimal("0")
    found = False

    for item in provider_results:
        cost = extract_actual_cost_usd(item)
        if cost is None:
            continue
        total += cost
        found = True

    if not found:
        return None
    return total.quantize(_DECIMAL_PLACES, rounding=ROUND_HALF_UP)
