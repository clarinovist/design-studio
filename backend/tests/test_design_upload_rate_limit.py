import inspect

from fastapi.params import Depends

from app.api.designs_routers.media import upload_user_image
from app.api.rate_limit import rate_limit_dependency


def test_upload_user_image_uses_action_rate_limit_dependency() -> None:
    signature = inspect.signature(upload_user_image)
    dependency = signature.parameters["current_user"].default

    assert isinstance(dependency, Depends)
    assert dependency.dependency is rate_limit_dependency
