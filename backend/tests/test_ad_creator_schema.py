from app.schemas.ad_creator import AdCreatorRequest, BatchResizeRequest


def test_ad_creator_request_reference_focus_default_auto() -> None:
    payload = AdCreatorRequest.model_validate({"image_base64": "data:image/png;base64,abc"})
    assert payload.reference_focus == "auto"


def test_ad_creator_request_reference_focus_accepts_human() -> None:
    payload = AdCreatorRequest.model_validate(
        {
            "image_base64": "data:image/png;base64,abc",
            "reference_focus": "human",
        }
    )
    assert payload.reference_focus == "human"


def test_batch_resize_request_reference_focus_default_auto() -> None:
    payload = BatchResizeRequest.model_validate(
        {
            "image_url": "https://example.com/image.jpg",
            "target_sizes": ["1:1"],
        }
    )
    assert payload.reference_focus == "auto"
