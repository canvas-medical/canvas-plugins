"""Patterns from installed plugins that only work under the deprecated sandbox rules.

Each function runs inside a handler's compute(), as the original code did, and returns a
string describing its result.
"""

from canvas_sdk.utils.http import Http


def private_sdk_attribute() -> str:
    """Reading an SDK client's private attribute, as a plugin building its own URLs does."""
    return str(Http()._session is not None)


def lazily_imported_nonlocal() -> str:
    """A module imported only when needed, which uses nonlocal."""
    from test_always_legacy_plugin.helpers.compositions import count_items

    return str(count_items(["a", "b", "c"]))


class _Snapshot:
    pass


def own_module_name() -> str:
    """Reading `__module__` on the plugin's own object."""
    return _Snapshot().__module__.split(".")[0]
