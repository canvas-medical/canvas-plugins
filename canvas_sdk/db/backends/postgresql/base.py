"""
Custom PostgreSQL database backend that automatically sets search_path
based on the current plugin context.
"""

from django.db.backends.postgresql import base


class DatabaseWrapper(base.DatabaseWrapper):
    """Custom PostgreSQL wrapper that sets search_path based on plugin context."""

    def init_connection_state(self):
        """Initialize connection state, including search_path."""
        super().init_connection_state()

        # Also set search_path when connection state is initialized
        from canvas_sdk.v1.plugin_database_context import get_current_plugin

        plugin_name = get_current_plugin()
        if plugin_name:
            with self.connection.cursor() as cursor:
                cursor.execute("SET search_path = %s, public", [plugin_name])
