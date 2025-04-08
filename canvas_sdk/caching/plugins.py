from typing import Any

import settings
from canvas_sdk.caching.base import Cache
from canvas_sdk.caching.client import get_cache as get_cache_client
from canvas_sdk.utils.plugins import plugin_only


@plugin_only
def get_cache(**kwargs: Any) -> Cache:
    """Get the cache client for plugins."""
    prefix = kwargs["plugin_name"]
    return get_cache_client("plugins", prefix, settings.CANVAS_SDK_CACHE_TIMEOUT_SECONDS)
