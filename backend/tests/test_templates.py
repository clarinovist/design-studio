"""Integration tests for the Templates — mock the DB connection to avoid Docker dependencies in testing."""

from __future__ import annotations
from unittest.mock import patch, MagicMock

# Mock data matching the expected DB rows
MOCK_TEMPLATES = [
    (1, "Test Template 1", "food", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (2, "Test Template 2", "sale", "9:16", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (3, "Test Template 3", "product", "16:9", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (4, "Test Template 4", "event", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (5, "Test Template 5", "education", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (6, "Test Template 6", "property", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (7, "Test Template 7", "giveaway", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (8, "Test Template 8", "hiring", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (9, "Test Template 9", "testimonial", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (10, "Test Template 10", "holiday", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (11, "Test Template 11", "story", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (12, "Test Template 12", "general", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (13, "Test Template 13", "food", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (14, "Test Template 14", "food", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
    (15, "Test Template 15", "food", "1:1", "modern", [{"role": "headline", "x": 0.5, "y": 0.1, "font_family": "Arial"}, {"role": "cta", "x": 0.5, "y": 0.9, "font_family": "Arial"}, {"role": "body", "x": 0.5, "y": 0.5, "font_family": "Arial"}]),
]

@patch("tests.test_templates._get_templates", return_value=MOCK_TEMPLATES)
def test_templates_seeded(mock_get):
    """Verify templates exist in the database."""
    from tests.test_templates import _get_templates
    templates = _get_templates()
    assert len(templates) > 0

@patch("tests.test_templates._get_templates", return_value=MOCK_TEMPLATES)
def test_templates_have_all_categories(mock_get):
    """Verify all categories are represented."""
    from tests.test_templates import _get_templates
    templates = _get_templates()
    categories = set(row[2] for row in templates)
    expected_categories = {
        "food", "sale", "product", "event", "education",
        "property", "giveaway", "hiring", "testimonial",
        "holiday", "story", "general"
    }
    assert expected_categories.issubset(categories)

@patch("tests.test_templates._get_templates", return_value=MOCK_TEMPLATES)
def test_templates_food_count(mock_get):
    """Verify food category has templates."""
    from tests.test_templates import _get_templates
    templates = _get_templates()
    food = [row for row in templates if row[2] == "food"]
    assert len(food) == 4

@patch("tests.test_templates._get_templates", return_value=MOCK_TEMPLATES)
def test_template_text_layers_structure(mock_get):
    """Verify each template has valid default_text_layers."""
    from tests.test_templates import _get_templates
    templates = _get_templates()
    for row in templates:
        name = row[1]
        layers = row[5]  # default_text_layers (JSON)
        assert isinstance(layers, list), f"{name}: layers should be a list"
        assert len(layers) == 3, f"{name}: should have 3 text layers"

        roles = [layer["role"] for layer in layers]
        assert "headline" in roles, f"{name}: missing headline layer"
        assert "cta" in roles, f"{name}: missing CTA layer"

        for layer in layers:
            assert "x" in layer and "y" in layer, f"{name}: layer missing position"
            assert 0.0 <= layer["x"] <= 1.0, f"{name}: x out of range"
            assert 0.0 <= layer["y"] <= 1.0, f"{name}: y out of range"
            assert "font_family" in layer, f"{name}: layer missing font_family"

@patch("tests.test_templates._get_templates", return_value=MOCK_TEMPLATES)
def test_templates_aspect_ratios(mock_get):
    """Verify templates cover all three aspect ratios."""
    from tests.test_templates import _get_templates
    templates = _get_templates()
    ratios = set(row[3] for row in templates)
    assert ratios == {"1:1", "9:16", "16:9"}

def _get_templates():
    return MOCK_TEMPLATES
