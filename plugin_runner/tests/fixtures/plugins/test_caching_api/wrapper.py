from typing import Any

from canvas_sdk.caching.plugins import get_cache

test_cache = get_cache()


def wrapped_get_cache(*args: Any, **kwargs: Any) -> Any:
    """
    This contrived method just exists to ensure that we can import `get_cache`
    from files that are imported from the main protocol.
    """
    return get_cache(*args, **kwargs)


class WrappedCache:
    """
    Contrived class ensuring we can call get_cache from non-protocol code.
    """

    @classmethod
    def get(cls, key: str) -> str:
        """
        Get a cache item.
        """
        if cached := get_cache().get(key):
            return cached

        return "nope"

    @classmethod
    def set(cls, key: str, value: str) -> None:
        """
        Set a cache item.
        """
        cache = get_cache()
        cache.set(key, value)
