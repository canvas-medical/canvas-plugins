import pytest

from canvas_sdk.caching.client import caches


@pytest.fixture(autouse=True)
def clear_caches() -> None:
    """Clear the cache before each test."""
    cleared_drivers: set[str] = set()
    for (driver, _), cache in caches.items():
        # If we've already cleared the cache for the current driver, skip
        # it to avoid clearing it again.
        if driver in cleared_drivers:
            continue

        cache._connection.clear()
        cleared_drivers.add(driver)

    caches.clear()
