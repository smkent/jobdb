from typing import Any

from django.conf import settings
from django.http import HttpRequest


def common_context(request: HttpRequest) -> dict[str, Any]:
    return {"settings_debug": settings.DEBUG}
