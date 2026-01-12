from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from django.db import connection, models


class PluginDataManager(models.Manager["PluginData"]):
    """Custom manager that enforces plugin isolation via RLS."""

    _thread_local = threading.local()

    @classmethod
    def _get_current_plugin(cls) -> str | None:
        """Get the current plugin context."""
        return getattr(cls._thread_local, "current_plugin", None)

    @classmethod
    def _set_current_plugin(cls, plugin_name: str | None) -> None:
        """Set the current plugin context."""
        cls._thread_local.current_plugin = plugin_name

    def _require_context(self) -> str:
        """Get current plugin, raising if not set."""
        plugin_name = self._get_current_plugin()
        if not plugin_name:
            raise RuntimeError("Plugin context not set.")
        return plugin_name

    def get_queryset(self) -> models.QuerySet[PluginData]:
        """Return a queryset scoped to current plugin via RLS."""
        self._require_context()
        return super().get_queryset()

    def upsert(self, key: str, data: dict[str, Any]) -> PluginData:
        """
        Insert or update a plugin data record with shallow merge.

        On insert, stores the data as-is. On update, merges new keys into
        existing data (top-level shallow merge via jsonb || operator).

        Args:
            key: Unique key within this plugin's namespace
            data: JSON-serializable dictionary to store/merge

        Returns:
            The created or updated PluginData instance
        """
        plugin_name = self._require_context()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO plugin_io_plugindata (id, plugin_name, key, data, created, modified)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (plugin_name, key)
                DO UPDATE SET data = plugin_io_plugindata.data || EXCLUDED.data, modified = NOW()
                RETURNING id, plugin_name, key, data, created, modified
                """,
                [str(uuid.uuid4()), plugin_name, key, json.dumps(data)],
            )
            row = cursor.fetchone()

        # Parse JSON if returned as string (depends on psycopg version/config)
        row_data = row[3]
        if isinstance(row_data, str):
            row_data = json.loads(row_data)

        return PluginData(
            id=row[0],
            plugin_name=row[1],
            key=row[2],
            data=row_data,
            created=row[4],
            modified=row[5],
        )


class PluginData(models.Model):
    """
    JSONB-based storage for plugin-specific data.

    This model provides persistent key-value storage with JSON document values.
    Each plugin can only access its own data, enforced by PostgreSQL Row-Level Security.

    Storing Data:
        # upsert() merges new keys into existing data (shallow merge)
        PluginData.objects.upsert("config", {"timeout": 30})
        PluginData.objects.upsert("config", {"retries": 3})
        # Result: {"timeout": 30, "retries": 3}

        # Existing keys are updated
        PluginData.objects.upsert("config", {"timeout": 60})
        # Result: {"timeout": 60, "retries": 3}

    Retrieving Data:
        config = PluginData.objects.get(key="config")
        print(config.data["timeout"])

        if PluginData.objects.filter(key="config").exists():
            ...

    Querying by JSON Content:
        # Filter by JSON field
        episodes = PluginData.objects.filter(
            key__startswith="episode:",
            data__patient_id="patient-123"
        )

        # Query nested JSON
        active = PluginData.objects.filter(data__status="active")

    Full Replacement:
        # Use save() when you need to replace all data or delete keys
        config = PluginData.objects.get(key="config")
        del config.data["retries"]
        config.save()  # Replaces entire data field

    Deleting Records:
        PluginData.objects.filter(key="old-data").delete()
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plugin_name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = PluginDataManager()

    class Meta:
        managed = False
        db_table = "plugin_io_plugindata"

    def __str__(self) -> str:
        return f"{self.plugin_name}:{self.key}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the record, setting plugin_name from context."""
        plugin_name = PluginDataManager._get_current_plugin()
        if not plugin_name:
            raise RuntimeError("Plugin context not set.")
        self.plugin_name = plugin_name
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Delete the record."""
        if not PluginDataManager._get_current_plugin():
            raise RuntimeError("Plugin context not set.")
        return super().delete(*args, **kwargs)


@contextmanager
def plugin_context(plugin_name: str) -> Generator[None, None, None]:
    """
    Context manager to set plugin context for PluginData operations.

    Sets the thread-local context and PostgreSQL RLS session variable once.
    RLS uses SET LOCAL (transaction-scoped) for security.

    This is used internally by the plugin runner. Plugin developers should not
    use this directly.

    Args:
        plugin_name: The unique identifier for the plugin
    """
    previous_plugin = PluginDataManager._get_current_plugin()
    try:
        PluginDataManager._set_current_plugin(plugin_name)
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.current_plugin = %s", [plugin_name])
        yield
    finally:
        PluginDataManager._set_current_plugin(previous_plugin)
        if previous_plugin:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL app.current_plugin = %s", [previous_plugin])
