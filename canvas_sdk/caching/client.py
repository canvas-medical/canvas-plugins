from django.core.cache import InvalidCacheBackendError
from django.core.cache import caches as django_caches

from canvas_sdk.caching.base import Cache
from canvas_sdk.caching.exceptions import CacheConfigurationError

caches: dict[tuple[str, str], Cache] = {}


def get_cache(driver: str = "default", prefix: str = "", max_timeout: int | None = None) -> Cache:
    """Get the cache client base on the specified driver."""
    try:
        connection = django_caches[driver]
        if (driver, prefix) not in caches:
            caches[(driver, prefix)] = Cache(connection, prefix, max_timeout)
        return caches[(driver, prefix)]
    except InvalidCacheBackendError as error:
        raise CacheConfigurationError(driver) from error
