"""
Thread-safe plugin context management for setting database search_path.

Supports both plugin-specific schemas and shared data namespaces.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import django.db
from django.conf import settings as django_settings

import settings

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper

log = logging.getLogger("plugin_runner_logger")

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
    return "postgresql" in django_settings.DATABASES["default"]["ENGINE"]


def _set_search_path(schema: str) -> None:
    """Set PostgreSQL search_path. No-op on SQLite."""
    if not _is_postgres():
        return

    with django.db.connection.cursor() as cursor:
        cursor.execute("SET search_path = %s, public", [schema])


def _set_connection_plugin(plugin_name: str) -> None:
    """Name the plugin whose queries the connection runs. No-op on SQLite.

    home-app's views over agent run records keep only that plugin's rows, so a plugin never
    reads another's runs or proposals; an empty name reads none.
    """
    if not _is_postgres():
        return

    with django.db.connection.cursor() as cursor:
        cursor.execute("SELECT set_config('canvas.plugin_name', %s, false)", [plugin_name])


def _discard_connection() -> None:
    """Close the thread's connection so the pool never hands it out again."""
    raw = django.db.connection.connection
    if raw is not None:
        raw.close()
    django.db.connection.close()


def _reset_search_path() -> None:
    """Reset PostgreSQL search_path to default. No-op on SQLite."""
    if not _is_postgres():
        return

    with django.db.connection.cursor() as cursor:
        cursor.execute("SET search_path = public")


def _swap_to_writable_connection() -> BaseDatabaseWrapper | None:
    """Swap the default SQLite connection to writable mode.

    Returns the original connection so it can be restored, or None if no swap was needed.
    """
    if _is_postgres():
        return None

    original = django.db.connections["default"]
    temp_handler = django.db.utils.ConnectionHandler(
        {"default": settings.SQLITE_WRITE_MODE_DATABASE}
    )
    django.db.connections["default"] = temp_handler["default"]
    return original


def _restore_connection(original: BaseDatabaseWrapper) -> None:
    """Restore the original default connection after a writable swap."""
    temp_connection = django.db.connections["default"]
    django.db.connections["default"] = original
    temp_connection.close()


def _restore_thread(plugin_name: str | None, schema: str | None, access_level: str | None) -> None:
    """Put back the thread's plugin context as it was before a context was entered."""
    if plugin_name:
        _plugin_context.plugin_name = plugin_name
        _plugin_context.schema = schema
        _plugin_context.access_level = access_level
    else:
        for attr in ("plugin_name", "schema", "access_level"):
            if hasattr(_plugin_context, attr):
                delattr(_plugin_context, attr)


def _reset_connection(
    plugin_name: str, old_plugin: str | None, old_schema: str | None, namespace: str | None
) -> None:
    """Give the connection back the plugin name and schema it had before ``plugin_name``'s.

    When that fails, such as on a transaction a plugin left aborted, the connection may
    still carry the plugin's name and schema, so it is closed rather than pooled for reuse.
    """
    try:
        _set_connection_plugin(old_plugin or "")
        if old_schema:
            _set_search_path(old_schema)
        elif namespace:
            _reset_search_path()
    except Exception:
        log.warning(
            "plugin_database_context: could not reset the connection after %s; closing it",
            plugin_name,
            exc_info=True,
        )
        _discard_connection()


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

    try:
        # Only change search_path if a namespace is declared
        if namespace:
            _set_search_path(namespace)
        _set_connection_plugin(plugin_name)
    except Exception:
        # A failed entry, such as a failover, leaves the thread and its connection naming
        # what they named before, so no later exit restores this plugin's name and schema.
        _restore_thread(old_plugin, old_schema, old_access_level)
        _reset_connection(plugin_name, old_plugin, old_schema, namespace)
        raise

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

        # Restore the thread's previous context before touching the database, so a
        # failed reset below never leaves this thread naming the plugin.
        _restore_thread(old_plugin, old_schema, old_access_level)
        _reset_connection(plugin_name, old_plugin, old_schema, namespace)


__exports__ = (
    "get_current_plugin",
    "get_current_schema",
    "get_access_level",
    "is_write_allowed",
)
