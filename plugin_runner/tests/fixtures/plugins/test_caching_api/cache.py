from canvas_sdk.caching.plugins import get_cache


class CachedSdk:
    """A simple wrapper around the cache client to provide a static interface for setting and getting cache values."""

    @classmethod
    def get(cls, key: str) -> str:
        """Get a value from the cache by key."""
        return get_cache().get(key)

    @classmethod
    def set(cls, key: str, value: str) -> None:
        """Set a value in the cache by key."""
        cache = get_cache()
        cache.set(key, value)
