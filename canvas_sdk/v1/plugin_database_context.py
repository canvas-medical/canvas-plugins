"""
Thread-safe plugin context management for setting database search_path.

Supports both plugin-specific schemas and shared data namespaces.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager, nullcontext
from typing import TYPE_CHECKING, Any

from django.conf import settings as django_settings
from django.db import connection, transaction

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
    return "postgresql" in django_settings.DATABASES["default"]["ENGINE"]


# Transaction-local (is_local=true): Postgres reverts it at COMMIT/ROLLBACK, so
# it never outlives the transaction it was set in.
SET_LOCAL_SEARCH_PATH_SQL = "SELECT set_config('search_path', %s, true)"


def _search_path_value(schema: str) -> str:
    """Return the search_path value for a namespace schema."""
    return f'"{schema}", public'


def _apply_local_search_path(cursor: Any, schema: str) -> None:
    """Set search_path for the current transaction only on a raw DB-API cursor."""
    cursor.execute(SET_LOCAL_SEARCH_PATH_SQL, [_search_path_value(schema)])


def _namespace_search_path_wrapper(
    execute: Callable[..., Any],
    sql: str,
    params: Any,
    many: bool,
    context: dict[str, Any],
) -> Any:
    """Django execute wrapper that scopes search_path to each query's transaction.

    The plugin runner reaches Postgres through pgdog in transaction mode, so two
    consecutive transactions from one Django connection can run on different
    Postgres sessions, and a Postgres session is shared by many clients. A
    session-level ``SET search_path`` would leak to whichever client uses that
    session next, or be missing on the next transaction. Instead, every query
    made while a namespace is active runs inside a transaction that first sets
    the namespace's search_path locally: inside the caller's transaction if
    there is one, otherwise in a transaction wrapped around the single query.

    The schema is read from the thread-local plugin context at call time, so
    nested contexts see the innermost namespace.
    """
    schema = get_current_schema()
    # Statements Django issues while opening the wrapping transaction re-enter
    # this wrapper (SQLite sends BEGIN through a cursor); pass those through.
    if schema is None or getattr(_plugin_context, "scoping_search_path", False):
        return execute(sql, params, many, context)

    db = context["connection"]
    # context["cursor"] is Django's CursorWrapper; .cursor is the raw DB-API
    # cursor, which does not re-enter this wrapper.
    raw_cursor = context["cursor"].cursor

    scope: AbstractContextManager[Any] = (
        nullcontext() if db.in_atomic_block else transaction.atomic(using=db.alias)
    )
    _plugin_context.scoping_search_path = True
    try:
        with scope:
            _apply_local_search_path(raw_cursor, schema)
            _plugin_context.scoping_search_path = False
            return execute(sql, params, many, context)
    finally:
        _plugin_context.scoping_search_path = False


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

    temp_connection = django.db.connections["default"]
    django.db.connections["default"] = original
    temp_connection.close()


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

    # Only scope search_path if a namespace is declared (PostgreSQL only).
    search_path_scope: AbstractContextManager[Any] = (
        connection.execute_wrapper(_namespace_search_path_wrapper)
        if namespace and _is_postgres()
        else nullcontext()
    )

    # In SQLite mode, the default connection is read-only. Swap to the
    # writable connection for plugins that have read_write access so that
    # custom data writes succeed during local development.
    original_connection = None
    if access_level == "read_write" and namespace:
        original_connection = _swap_to_writable_connection()

    try:
        with search_path_scope:
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
        else:
            # Clear context entirely
            for attr in ("plugin_name", "schema", "access_level"):
                if hasattr(_plugin_context, attr):
                    delattr(_plugin_context, attr)


__exports__ = (
    "get_current_plugin",
    "get_current_schema",
    "get_access_level",
    "is_write_allowed",
)
