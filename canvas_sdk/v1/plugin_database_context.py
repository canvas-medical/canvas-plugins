"""
Thread-safe plugin context management for setting database search_path.
"""

import threading
from contextlib import contextmanager

# Thread-local storage for plugin context
_plugin_context = threading.local()


def set_current_plugin(plugin_name: str) -> None:
    """Set the current plugin name for this thread."""
    _plugin_context.plugin_name = plugin_name


def get_current_plugin() -> str | None:
    """Get the current plugin name for this thread."""
    return getattr(_plugin_context, "plugin_name", None)


def clear_current_plugin() -> None:
    """Clear the current plugin name for this thread."""
    if hasattr(_plugin_context, "plugin_name"):
        delattr(_plugin_context, "plugin_name")


@contextmanager
def plugin_database_context(plugin_name: str):
    """
    Thread-safe context manager for plugin operations.

    All Django ORM operations within this context will use the plugin's schema.
    """
    old_plugin = get_current_plugin()
    set_current_plugin(plugin_name)
    try:
        yield
    finally:
        if old_plugin:
            set_current_plugin(old_plugin)
        else:
            clear_current_plugin()


__exports__ = (
    "set_current_plugin",
    "get_current_plugin",
    "clear_current_plugin",
    "plugin_context",
)
