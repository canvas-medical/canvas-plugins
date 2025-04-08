import typing
from unittest.mock import Mock

import pytest

from canvas_sdk.caching.client import get_cache
from canvas_sdk.caching.exceptions import CacheConfigurationError, CachingException

if typing.TYPE_CHECKING:
    from typing import Any

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_caches(
    mocker: "MockerFixture", request: "Any"
) -> typing.Generator[list[Mock], None, None]:
    """A fixture that mocks the given cache drivers."""
    drivers = {(driver, ""): mocker.Mock() for driver in getattr(request, "param", ["default"])}

    mocker.patch.dict(
        "canvas_sdk.caching.client.caches",
        drivers,
        clear=True,
    )

    yield list(drivers.values())


@pytest.fixture
def mock_django_caches(
    mocker: "MockerFixture", request: "Any"
) -> typing.Generator[list[Mock], None, None]:
    """A fixture that mocks the given django cache drivers."""
    drivers = {driver: mocker.Mock() for driver in getattr(request, "param", ["default"])}

    mocker.patch.dict(
        "canvas_sdk.caching.client.django_caches",
        drivers,
    )

    yield list(drivers.values())


def test_get_client_default_driver() -> None:
    """Ensures get_cache() called with no args returns the default cache client."""
    assert get_cache() is get_cache(driver="default")


def test_get_client_invalid_driver() -> None:
    """Ensures get_cache raises an error when trying to fetch a non-existent cache driver."""
    with pytest.raises(CacheConfigurationError):
        get_cache(driver="non_existent_driver")


def test_get_client_not_recreated() -> None:
    """Ensures cache client is not recreated each time get_cache() is called."""
    assert get_cache() is get_cache()


def test_cache_get_existent_key() -> None:
    """Tests fetching an existing object from the cache."""
    cache = get_cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"


def test_cache_non_existent_key() -> None:
    """Tests fetching a non-existent key from the cache."""
    cache = get_cache()
    assert cache.get("key") is None


def test_get_many_keys() -> None:
    """Ensures that multiple keys can be retrieved from the cache at once."""
    cache = get_cache()
    data = {"key1": "value1", "key2": "value2"}
    cache.set_many(data)

    assert cache.get_many(keys=data.keys()) == data


def test_get_or_set_key_falls_back_to_default() -> None:
    """Ensures that a key can be set to a default automatically if it doesn't exist."""
    cache = get_cache()
    cache.set("existing_key", "existing_value")

    assert cache.get_or_set("existing_key", default="default") == "existing_value"
    assert cache.get_or_set("new_key", default="default") == "default"
    assert (
        cache.get_or_set("new_key_with_callable_default", default=lambda: "callable_default")
        == "callable_default"
    )


def test_set_key() -> None:
    """Ensures cache key is set correctly."""
    cache = get_cache()
    cache.set("key", "value")
    assert "key" in cache


def test_set_many_keys() -> None:
    """Ensures that multiple cache keys can be set at the same time."""
    cache = get_cache()
    data = {"key1": "value1", "key2": "value2"}
    cache.set_many(data)

    assert cache.get("key1") == data["key1"]
    assert cache.get("key2") == data["key2"]


def test_delete_key() -> None:
    """Ensures cache key is deleted correctly."""
    cache = get_cache()
    cache.set("key", "value")
    cache.delete("key")
    assert cache.get("key") is None


def test_clear_cache() -> None:
    """Ensures that all keys are removed."""
    cache = get_cache()
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache._connection.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_get_cache_includes_a_custom_prefix_in_the_cache_key() -> None:
    """Ensure that a given custom prefix is included in the cache key."""
    prefix = "prefix"
    key = "key"
    full_key = f"{prefix}:{key}"
    cache = get_cache(prefix=prefix)

    assert cache._make_key(key) == full_key


def test_make_key_is_called_for_all_cache_methods(
    mocker: "MockerFixture", mock_django_caches: list[Mock]
) -> None:
    """Ensure that make_key is called for every public method defined in the cache interface."""
    method_args: dict[str, typing.Any] = {
        "get": ("key",),
        "set": ("key", "value"),
        "delete": ("key",),
        "set_many": ({"key": "value"},),
        "get_many": (("key",),),
        "get_or_set": ("key",),
    }

    mock_make_key = mocker.patch("canvas_sdk.caching.client.Cache._make_key")

    cache = get_cache()
    cache_method_names = [
        method_name
        for method_name in dir(cache)
        if callable(getattr(cache, method_name))
        # ignore private and builtin methods
        and not method_name.startswith("_")
    ]

    for call_count, method_name in enumerate(cache_method_names, start=1):
        args = method_args.get(method_name, [])
        getattr(cache, method_name)(*args)
        assert mock_make_key.call_count == call_count


def test_get_timeout_raises_an_exception_if_the_timeout_exceeds_the_max_timeout() -> None:
    """Ensure that an exception is raised if the timeout exceeds the max timeout."""
    cache = get_cache(max_timeout_seconds=10)
    with pytest.raises(CachingException):
        cache._get_timeout(timeout_seconds=20)


def test_get_timeout_returns_the_max_timeout_seconds_if_no_timeout_is_provided() -> None:
    """Ensure that the max timeout is returned if no timeout is provided."""
    cache = get_cache(max_timeout_seconds=10)
    assert cache._get_timeout(timeout_seconds=None) == 10


def test_get_timeout_returns_the_provided_timeout_if_it_does_not_exceed_the_max_timeout_seconds() -> (
    None
):
    """Ensure that the provided timeout is returned if it does not exceed the max timeout."""
    cache = get_cache(max_timeout_seconds=10)
    assert cache._get_timeout(timeout_seconds=5) == 5


def test_get_timeout_is_called_by_all_set_operations(
    mocker: "MockerFixture", mock_django_caches: list[Mock]
) -> None:
    """Ensure that get_timeout is called for every set operation."""
    method_args: dict[str, typing.Any] = {
        "set": ("key", "value"),
        "set_many": ({"key": "value"},),
        "get_or_set": ("key", "value"),
    }

    mock_get_timeout = mocker.patch("canvas_sdk.caching.client.Cache._get_timeout")

    cache = get_cache()

    for call_count, method_name in enumerate(method_args.keys(), start=1):
        args = method_args.get(method_name, [])
        getattr(cache, method_name)(*args)
        assert mock_get_timeout.call_count == call_count
