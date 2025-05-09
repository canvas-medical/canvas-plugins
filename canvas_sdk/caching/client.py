from django.core.cache import InvalidCacheBackendError
from django.core.cache import caches as django_caches

from canvas_sdk.caching.base import Cache
from canvas_sdk.caching.exceptions import CacheConfigurationError

caches: dict[tuple[str, str], Cache] = {}


def get_cache(
    driver: str = "default", prefix: str = "", max_timeout_seconds: int | None = None
) -> Cache:
    """Get the cache client based on the specified driver."""
    try:
        key = (driver, prefix)
        connection = django_caches[driver]
        if key not in caches:
            caches[key] = Cache(connection, prefix, max_timeout_seconds)
        return caches[key]
    except InvalidCacheBackendError as error:
        raise CacheConfigurationError(driver) from error


__exports__ = ()
