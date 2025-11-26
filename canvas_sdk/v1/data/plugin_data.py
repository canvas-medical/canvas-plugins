from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, ClassVar

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

    _current_plugin: ClassVar[str | None] = None

    @classmethod
    def set_current_plugin(cls, plugin_name: str) -> None:
        """Set the current plugin context for RLS."""
        cls._current_plugin = plugin_name

    @classmethod
    def get_current_plugin(cls) -> str | None:
        """Get the current plugin context."""
        return cls._current_plugin

    def _set_plugin_context(self) -> None:
        """Set the PostgreSQL session variable for RLS."""
        if not self._current_plugin:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) "
                "before accessing plugin data."
            )
        with connection.cursor() as cursor:
            cursor.execute("SET app.current_plugin = %s", [self._current_plugin])

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
    Each plugin's data is isolated via PostgreSQL Row-Level Security.

    Setup:
        At the top of your plugin's main handler file, configure the plugin name:
    ```python
        from canvas_sdk.v1.data.plugin_data import PluginData

        PLUGIN_NAME = "my_awesome_plugin"
        PluginData.configure(PLUGIN_NAME)
    ```

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
            cursor.execute("SET app.current_plugin = %s", [plugin_name])

        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Hard delete. Consider using soft_delete() instead."""
        plugin_name = PluginDataManager.get_current_plugin()
        if not plugin_name:
            raise RuntimeError(
                "Plugin context not set. Call PluginData.configure(plugin_name) first."
            )

        with connection.cursor() as cursor:
            cursor.execute("SET app.current_plugin = %s", [plugin_name])

        return super().delete(*args, **kwargs)

    def soft_delete(self) -> None:
        """Mark this record as deleted without removing it from the database."""
        self.deleted_at = datetime.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    @classmethod
    def configure(cls, plugin_name: str) -> None:
        """
        Configure the plugin context for data isolation.

        This MUST be called before any PluginData operations.
        Call this at module load time with your PLUGIN_NAME constant.

        Args:
            plugin_name: The unique identifier for your plugin
                         (should match 'name' in CANVAS_MANIFEST.json)

        Example:
        ```python
            PLUGIN_NAME = "my_plugin"
            PluginData.configure(PLUGIN_NAME)
        ```
        """
        PluginDataManager.set_current_plugin(plugin_name)
