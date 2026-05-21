import pytest
from unittest.mock import patch

from app.schemas.catalog import CatalogBasicsRequest, CatalogImageInput, ImageMappingRequest
from app.services.catalog_generation_service import map_catalog_images, plan_catalog_structure


@pytest.fixture(autouse=True)
def force_catalog_fallback_path():
    with patch("app.services.catalog_generation_service._llm_available", return_value=False):
        yield


@pytest.mark.asyncio
async def test_photo_studio_three_page_catalog_prefers_service_list_structure():
    result = await plan_catalog_structure(
        CatalogBasicsRequest(
            catalog_type="service",
            total_pages=3,
            goal="showcasing",
            tone="premium",
            business_name="Studio Foto Memori",
            business_context="Studio foto keluarga, wisuda, dan prewedding di Surabaya.",
        )
    )

    page_types = [page.type for page in result.suggested_structure]
    assert page_types == ["cover", "service_list", "cta"]


@pytest.mark.asyncio
async def test_photo_studio_reference_image_maps_to_cover_and_service_page():
    basics = CatalogBasicsRequest(
        catalog_type="service",
        total_pages=3,
        goal="showcasing",
        tone="premium",
        business_name="Studio Foto Memori",
        business_context="Layanan fotografi studio untuk keluarga dan wisuda.",
    )
    structure = (await plan_catalog_structure(basics)).suggested_structure

    result = await map_catalog_images(
        ImageMappingRequest(
            basics=basics,
            structure=structure,
            images=[
                CatalogImageInput(
                    image_id="img_1",
                    filename="studio-foto-keluarga.jpg",
                    description="Portfolio studio foto keluarga indoor",
                )
            ],
        )
    )

    assert result.image_mapping[0].category == "service_image"
    assert result.image_mapping[0].recommended_pages == [1, 2]
