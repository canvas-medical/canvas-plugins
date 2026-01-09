from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from django.db import connection, models
from django.db.models import QuerySet


class PluginDataQuerySet(QuerySet["PluginData"]):
    """Extended QuerySet with plugin-specific operations."""

    def upsert(self, key: str, data: dict[str, Any]) -> PluginData:
        """
        Insert or update a plugin data record.

        If a record with the given key exists (including soft-deleted), it will be
        updated. Otherwise, a new record is created.

        Args:
            key: Unique key within this plugin's namespace
            data: JSON-serializable dictionary to store

        Returns:
            The created or updated PluginData instance
        """
        plugin_name = PluginDataManager.get_current_plugin()
        if not plugin_name:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) first."
            )

        # Use raw SQL for true upsert with soft-delete recovery
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO plugin_io_plugindata (id, plugin_name, key, data, created, modified, deleted_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW(), NULL) ON CONFLICT (plugin_name, key)
                WHERE deleted_at IS NULL
                    DO
                UPDATE SET
                    data = EXCLUDED.data,
                    modified = NOW(),
                    deleted_at = NULL
                    RETURNING id, plugin_name, key, data, created, modified, deleted_at
                """,
                [str(uuid.uuid4()), plugin_name, key, json.dumps(data)],
            )
            row = cursor.fetchone()

        return PluginData(
            id=row[0],
            plugin_name=row[1],
            key=row[2],
            data=row[3],
            created=row[4],
            modified=row[5],
            deleted_at=row[6],
        )

    def soft_delete(self) -> int:
        """
        Soft delete matching records by setting deleted_at.

        Returns:
            Number of records soft-deleted
        """
        return self.update(deleted_at=datetime.now())


class PluginDataManager(models.Manager["PluginData"]):
    """
    Custom manager that enforces plugin isolation via RLS session variable.
    """

    _thread_local = threading.local()

    @classmethod
    def set_current_plugin(cls, plugin_name: str) -> None:
        """
        Set the current plugin context.

        Args:
            plugin_name: The plugin identifier
        """
        cls._thread_local.current_plugin = plugin_name

    @classmethod
    def get_current_plugin(cls) -> str | None:
        """Get the current plugin context."""
        return getattr(cls._thread_local, "current_plugin", None)

    def _set_plugin_context(self) -> None:
        """Set the PostgreSQL session variable for RLS."""
        current_plugin = self.get_current_plugin()
        if not current_plugin:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) "
                "before accessing plugin data."
            )

        # Always set RLS context - home-app's RLS policies handle access control
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.current_plugin = %s", [current_plugin])

    def get_queryset(self) -> PluginDataQuerySet:
        """Return a queryset with plugin context set."""
        self._set_plugin_context()
        return PluginDataQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def upsert(self, key: str, data: dict[str, Any]) -> PluginData:
        """Convenience method to upsert from manager."""
        self._set_plugin_context()
        return self.get_queryset().upsert(key, data)


class PluginData(models.Model):
    """
    JSONB-based storage for plugin-specific data.

    This model provides persistent key-value storage with JSON document values.
    Each plugin can access its own data, and can optionally share its data with
    other plugins (read-only).

    Data Sharing Configuration:
        Configure data sharing in your CANVAS_MANIFEST.json:

        ```json
        {
          "name": "my_plugin",
          "data_isolated": true,  // Keep my data private (default)
          ...
        }
        ```

        - `data_isolated: true` (default): Your plugin's data is private. Only you
          can read/write it. Other plugins cannot access it.

        - `data_isolated: false`: Your plugin's data is shared (read-only). Other
          plugins can READ your data, but only you can WRITE to it. Use this when
          you want to expose data as a shared cache or lookup table.

        IMPORTANT: Setting `data_isolated: false` does NOT grant your plugin access
        to other plugins' data. It only makes YOUR data readable by others.

        The plugin runner automatically reads this setting from your manifest.
        No code changes needed!

    Basic Usage:
    ```python
        # Store data
        PluginData.objects.upsert("config", {"api_url": "https://...", "timeout": 30})

        # Retrieve data
        config = PluginData.objects.get(key="config")
        print(config.data["api_url"])

        # Check existence
        if PluginData.objects.filter(key="config").exists():
            ...
    ```

    Querying by JSON Content:
    ```python
        # Find all episodes for a patient
        episodes = PluginData.objects.filter(
            key__startswith="episode:",
            data__patient_id="patient-123"
        )

        # Query nested JSON
        active_episodes = PluginData.objects.filter(
            data__status="active",
            data__metadata__priority="high"
        )

        # Array containment (PostgreSQL @> operator)
        tagged = PluginData.objects.filter(data__tags__contains=["urgent"])

        # Check if key exists in JSON
        with_notes = PluginData.objects.filter(data__has_key="notes")
    ```

    Updating:
    ```python
        # Full replace via upsert
        PluginData.objects.upsert("config", {"api_url": "https://new-url.com"})

        # Partial update (fetch, modify, save)
        config = PluginData.objects.get(key="config")
        config.data["timeout"] = 60
        config.save()
    ```

    Deleting:
    ```python
        # Soft delete (recommended)
        PluginData.objects.filter(key="old-data").soft_delete()

        # Hard delete (use sparingly)
        PluginData.objects.filter(key="old-data").delete()
    ```
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plugin_name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = PluginDataManager()

    class Meta:
        managed = False
        db_table = "plugin_io_plugindata"

    def __str__(self) -> str:
        return f"{self.plugin_name}:{self.key}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the record, ensuring plugin context is set."""
        plugin_name = PluginDataManager.get_current_plugin()
        if not plugin_name:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) first."
            )

        # Ensure plugin_name matches context (prevent spoofing)
        if self.plugin_name and self.plugin_name != plugin_name:
            raise ValueError(
                f"Cannot save PluginData with plugin_name '{self.plugin_name}' "
                f"when configured for '{plugin_name}'"
            )

        self.plugin_name = plugin_name

        # Set the RLS context before save
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.current_plugin = %s", [plugin_name])

        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Hard delete. Consider using soft_delete() instead."""
        plugin_name = PluginDataManager.get_current_plugin()
        if not plugin_name:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) first."
            )

        # Set the RLS context before delete
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.current_plugin = %s", [plugin_name])

        return super().delete(*args, **kwargs)

    def soft_delete(self) -> None:
        """Mark this record as deleted without removing it from the database."""
        self.deleted_at = datetime.now()
        self.save(update_fields=["deleted_at", "modified"])

    @classmethod
    def configure(cls, plugin_name: str) -> None:
        """
        Manually configure the plugin context.

        NOTE: This is typically NOT needed! The plugin runner automatically sets
        the plugin context before calling handler.compute(). Only use this if you
        need to manually set the context (e.g., in tests).

        Args:
            plugin_name: The unique identifier for your plugin
                         (should match 'name' in CANVAS_MANIFEST.json)

        Example:
        ```python
            # Manually set plugin context (mainly for testing)
            PluginData.configure("my_plugin")

            # Now can access plugin data
            data = PluginData.objects.filter(key="config")
        ```
        """
        PluginDataManager.set_current_plugin(plugin_name)


@contextmanager
def plugin_context(plugin_name: str) -> Generator[None, None, None]:
    """
    Context manager to automatically set and clean up plugin context.

    This is primarily used internally by the plugin runner to automatically
    set the plugin context before executing handler code. Plugin developers
    typically don't need to use this directly.

    Args:
        plugin_name: The unique identifier for the plugin

    Example:
    ```python
        # Automatic context management (used by plugin runner)
        with plugin_context("my_plugin"):
            # All PluginData operations here use "my_plugin" context
            PluginData.objects.upsert("key", {"value": 123})
    ```
    """
    # Store previous context to restore later (for nested contexts)
    previous_plugin = PluginDataManager.get_current_plugin()

    try:
        PluginDataManager.set_current_plugin(plugin_name)
        yield
    finally:
        # Restore previous context
        if previous_plugin is not None:
            PluginDataManager.set_current_plugin(previous_plugin)
        else:
            # Clear the context if there was no previous context
            PluginDataManager._thread_local.current_plugin = None
