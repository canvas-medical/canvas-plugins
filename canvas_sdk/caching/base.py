from collections.abc import Iterable
from typing import Any

from django.core.cache import BaseCache

from canvas_sdk.caching.exceptions import CachingException
from canvas_sdk.caching.utils import WriteOnceProperty


class Cache:
    """A Class wrapper for interacting with cache."""

    _connection = WriteOnceProperty[BaseCache]()
    _prefix = WriteOnceProperty[str]()
    _max_timeout_seconds = WriteOnceProperty[int | None]()

    def __init__(
        self, connection: BaseCache, prefix: str = "", max_timeout_seconds: int | None = None
    ) -> None:
        self._connection = connection
        self._prefix = prefix
        self._max_timeout_seconds = max_timeout_seconds

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}:{key}" if self._prefix else key

    def _get_timeout(self, timeout_seconds: int | None) -> int | None:
        if timeout_seconds is None:
            return self._max_timeout_seconds

        if self._max_timeout_seconds is not None and timeout_seconds > self._max_timeout_seconds:
            raise CachingException(
                f"Timeout of {timeout_seconds} seconds exceeds the max timeout of {self._max_timeout_seconds} seconds."
            )

        return timeout_seconds

    def set(self, key: str, value: Any, timeout_seconds: int | None = None) -> None:
        """Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            timeout_seconds: The number of seconds for which the value should be cached.
        """
        key = self._make_key(key)
        self._connection.set(key, value, self._get_timeout(timeout_seconds))

    def set_many(self, data: dict[str, Any], timeout_seconds: int | None = None) -> list[str]:
        """Set multiple values in the cache simultaneously.

        Args:
            data: A dict of cache keys and their values.
            timeout_seconds: The number of seconds for which to cache the data.

        Returns:
            Returns a list of cache keys that failed insertion if supported by
            the backend. Otherwise, an empty list is returned.
        """
        data = {self._make_key(key): value for key, value in data.items()}
        return self._connection.set_many(data, self._get_timeout(timeout_seconds))

    def get(self, key: str, default: Any | None = None) -> Any:
        """Fetch a given key from the cache.

        Args:
            key: The cache key.
            default: The value to return if the key does not exist.

        Returns:
            The cached value, or the default if the key does not exist.
        """
        key = self._make_key(key)
        return self._connection.get(key, default)

    def get_or_set(
        self, key: str, default: Any | None = None, timeout_seconds: int | None = None
    ) -> Any:
        """Fetch a given key from the cache, or set it to the given default.

        If the key does not exist, it will be created with the given default as
        its value. If the default is a callable, it will be called with no
        arguments and the return value will be used.

        Args:
            key: The key to retrieve.
            default: The default value to set if the key does not exist. May be
                     a callable with no arguments.
            timeout_seconds: The number of seconds for which to cache the key.

        Returns:
            The cached value.
        """
        key = self._make_key(key)
        return self._connection.get_or_set(key, default, self._get_timeout(timeout_seconds))

    def get_many(self, keys: Iterable[str]) -> Any:
        """Fetch multiple values from the cache.

        This is often much faster than retrieving cached values individually,
        and its use is encouraged where possible.

        Args:
            keys: The cache keys to retrieve.

        Returns:
            A dict mapping each key in 'keys' to its cached value.
        """
        keys = {self._make_key(key) for key in keys}
        return self._connection.get_many(keys)

    def delete(self, key: str) -> None:
        """Delete a key from the cache.

        Args:
            key: The key to be removed from the cache.
        """
        key = self._make_key(key)
        self._connection.delete(key)

    def __contains__(self, key: str) -> bool:
        """Return True if the key is in the cache and has not expired."""
        key = self._make_key(key)
        return self._connection.__contains__(key)


__exports__ = ()
