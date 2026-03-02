"""
Thread-safe plugin context management for setting database search_path.

Supports both plugin-specific schemas and shared data namespaces.
"""

from __future__ import annotations

import threading
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper

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


def _swap_to_writable_connection() -> BaseDatabaseWrapper | None:
    """Swap the default SQLite connection to writable mode.

    Returns the original connection so it can be restored, or None if no swap was needed.
    """
    if _is_postgres():
        return None

    import django.db

    import settings

    original = django.db.connections["default"]
    temp_handler = django.db.utils.ConnectionHandler(
        {"default": settings.SQLITE_WRITE_MODE_DATABASE}
    )
    django.db.connections["default"] = temp_handler["default"]
    return original


def _restore_connection(original: BaseDatabaseWrapper) -> None:
    """Restore the original default connection after a writable swap."""
    import django.db

    django.db.connections["default"] = original


@contextmanager
def plugin_database_context(
    plugin_name: str,
    namespace: str | None = None,
    access_level: str = "read",
) -> Generator[None, None, None]:
    """
    Thread-safe context manager for plugin operations.

    All Django ORM operations within this context will use the specified namespace
    schema in addition to the public schema

    Args:
        plugin_name: The plugin's name
        namespace: Optional namespace schema to use for custom data
        access_level: 'read' or 'read_write' (only applies to namespaces)
    """
    # Save old context
    old_plugin = getattr(_plugin_context, "plugin_name", None)
    old_schema = getattr(_plugin_context, "schema", None)
    old_access_level = getattr(_plugin_context, "access_level", None)

    # Set new context
    _plugin_context.plugin_name = plugin_name
    _plugin_context.schema = namespace
    _plugin_context.access_level = access_level

    # Only change search_path if a namespace is declared
    if namespace:
        _set_search_path(namespace)

    # In SQLite mode, the default connection is read-only. Swap to the
    # writable connection for plugins that have read_write access so that
    # custom data writes succeed during local development.
    original_connection = None
    if access_level == "read_write" and namespace:
        original_connection = _swap_to_writable_connection()

    try:
        yield
    finally:
        # Restore writable connection swap if we did one
        if original_connection is not None:
            _restore_connection(original_connection)

        # Restore previous context
        if old_plugin:
            _plugin_context.plugin_name = old_plugin
            _plugin_context.schema = old_schema
            _plugin_context.access_level = old_access_level
            if old_schema:
                _set_search_path(old_schema)
            elif namespace:
                _reset_search_path()
        else:
            # Clear context entirely
            for attr in ("plugin_name", "schema", "access_level"):
                if hasattr(_plugin_context, attr):
                    delattr(_plugin_context, attr)
            if namespace:
                _reset_search_path()


__exports__ = (
    "get_current_plugin",
    "get_current_schema",
    "get_access_level",
    "is_write_allowed",
    "plugin_database_context",
)
