from collections.abc import Generator

import pytest


def _clear_caches() -> None:
    from canvas_sdk.caching.client import CACHES

    cleared_drivers: set[str] = set()

    for (driver, _), cache in CACHES.items():
        # If we've already cleared the cache for the current driver, skip
        # it to avoid clearing it again.
        if driver in cleared_drivers:
            continue

        cache._connection.clear()
        cleared_drivers.add(driver)

    CACHES.clear()


@pytest.fixture(autouse=True)
def clear_caches() -> Generator:
    """Clear the cache before each test."""
    _clear_caches()

    yield

    _clear_caches()
