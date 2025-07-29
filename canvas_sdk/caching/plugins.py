from __future__ import annotations

from typing import TYPE_CHECKING, Any

from canvas_sdk.caching.client import get_cache as get_cache_client
from canvas_sdk.utils.plugins import plugin_context
from settings import CANVAS_SDK_CACHE_TIMEOUT_SECONDS

if TYPE_CHECKING:
    from canvas_sdk.caching.base import Cache


@plugin_context
def get_cache(**kwargs: Any) -> Cache:
    """Get the cache client for plugins."""
    return get_cache_client(
        driver="plugins",
        prefix=kwargs["plugin_name"],
        max_timeout_seconds=CANVAS_SDK_CACHE_TIMEOUT_SECONDS,
    )


__exports__ = ("get_cache",)
