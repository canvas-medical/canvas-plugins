"""
Thread-safe plugin context management for setting database search_path.

Supports both plugin-specific schemas and shared data namespaces.
"""

import threading
from collections.abc import Generator
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


def get_current_schema() -> str | None:
    """Get the current schema (namespace or plugin schema) for this thread."""
    return getattr(_plugin_context, "schema", None)


def get_access_level() -> str:
    """Get the current access level for this thread.

    Returns:
        'read' by default (principle of least privilege)
        'read_write' when explicitly granted write access
    """
    return getattr(_plugin_context, "access_level", "read")


def is_write_allowed() -> bool:
    """Check if write operations are allowed in the current context."""
    return get_access_level() == "read_write"


def _is_postgres() -> bool:
    """Check if we're running on PostgreSQL (vs SQLite for tests)."""
    from django.conf import settings

    return "postgresql" in settings.DATABASES["default"]["ENGINE"]


def _set_search_path(schema: str) -> None:
    """Set PostgreSQL search_path. No-op on SQLite."""
    if not _is_postgres():
        return

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SET search_path = %s, public", [schema])


def _reset_search_path() -> None:
    """Reset PostgreSQL search_path to default. No-op on SQLite."""
    if not _is_postgres():
        return

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SET search_path = public")


@contextmanager
def plugin_database_context(
    plugin_name: str,
    namespace: str | None = None,
    access_level: str = "read_write",
) -> Generator[None, None, None]:
    """
    Thread-safe context manager for plugin operations.

    All Django ORM operations within this context will use either:
    - The plugin's own schema (if namespace is None)
    - The specified namespace schema (if namespace is provided)

    Args:
        plugin_name: The plugin's name (for tracking purposes)
        namespace: Optional namespace schema to use instead of plugin schema
        access_level: 'read' or 'read_write' (only applies to namespaces)
    """
    # Determine which schema to use
    schema = namespace if namespace else plugin_name

    # Save old context
    old_plugin = getattr(_plugin_context, "plugin_name", None)
    old_schema = getattr(_plugin_context, "schema", None)
    old_access_level = getattr(_plugin_context, "access_level", None)

    # Set new context
    _plugin_context.plugin_name = plugin_name
    _plugin_context.schema = schema
    _plugin_context.access_level = access_level

    # Set search_path on the current connection for this context (PostgreSQL only)
    _set_search_path(schema)

    try:
        yield
    finally:
        # Restore previous context
        if old_plugin:
            _plugin_context.plugin_name = old_plugin
            _plugin_context.schema = old_schema
            _plugin_context.access_level = old_access_level
            _set_search_path(old_schema or old_plugin)
        else:
            # Clear context entirely
            for attr in ("plugin_name", "schema", "access_level"):
                if hasattr(_plugin_context, attr):
                    delattr(_plugin_context, attr)
            # Reset to default search_path
            _reset_search_path()


__exports__ = (
    "get_current_plugin",
    "get_current_schema",
    "get_access_level",
    "is_write_allowed",
    "plugin_database_context",
)
