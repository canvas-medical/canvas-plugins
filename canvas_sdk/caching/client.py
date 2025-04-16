from django.core.cache import InvalidCacheBackendError
from django.core.cache import caches as django_caches

from canvas_sdk.caching.base import Cache
from canvas_sdk.caching.exceptions import CacheConfigurationError

CACHES: dict[tuple[str, str], Cache] = {}


def get_cache(
    driver: str = "default",
    prefix: str = "",
    max_timeout_seconds: int | None = None,
) -> Cache:
    """Get the cache client based on the specified driver."""
    global CACHES

    try:
        key = (driver, prefix)

        if key not in CACHES:
            CACHES[key] = Cache(django_caches[driver], prefix, max_timeout_seconds)

        return CACHES[key]
    except InvalidCacheBackendError as error:
        raise CacheConfigurationError(driver) from error
