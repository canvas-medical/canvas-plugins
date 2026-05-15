"""Tests for write permission enforcement in Model operations.

Tests verify that:
1. NamespaceWriteDenied is raised when saving with read-only access
2. NamespaceWriteDenied is raised when deleting with read-only access
3. Save and delete succeed with read_write access
4. Operations succeed when not in a plugin context
"""

from unittest.mock import patch

import pytest
from django.db import models

from canvas_sdk.v1.data.base import (
    MAX_FIELD_SIZE,
    CustomModel,
    FieldValueTooLarge,
    Model,
    NamespaceWriteDenied,
)
from canvas_sdk.v1.plugin_database_context import (
    _plugin_context,
    clear_current_plugin,
)


class MockModel(CustomModel):
    """A mock model for testing write permission enforcement."""

    class Meta:
        app_label = "test"
        # Not abstract so we can instantiate it, but managed=False to avoid migrations
        managed = False


class MockModelWithFields(CustomModel):
    """A mock model with TextField and JSONField for size validation tests."""

    class Meta:
        app_label = "test"
        managed = False

    text_field = models.TextField(null=True)
    json_field = models.JSONField(null=True)


class TestNamespaceWriteDenied:
    """Tests for the NamespaceWriteDenied exception."""

    def test_exception_is_raised(self) -> None:
        """NamespaceWriteDenied can be raised and caught."""
        with pytest.raises(NamespaceWriteDenied):
            raise NamespaceWriteDenied("Test error")

    def test_exception_message(self) -> None:
        """NamespaceWriteDenied should contain the error message."""
        try:
            raise NamespaceWriteDenied("Custom error message")
        except NamespaceWriteDenied as e:
            assert "Custom error message" in str(e)


class TestModelWritePermissionCheck:
    """Tests for Model._check_write_permission method."""

    def setup_method(self) -> None:
        """Clear any existing plugin context before each test."""
        clear_current_plugin()
        for attr in ("schema", "access_level"):
            if hasattr(_plugin_context, attr):
                delattr(_plugin_context, attr)

    def test_check_write_permission_allows_when_no_context(self) -> None:
        """Write operations should be allowed when not in a plugin context."""
        model = MockModel()
        # Should not raise
        model._check_write_permission()

    def test_check_write_permission_allows_when_read_write_access(self) -> None:
        """Write operations should be allowed when access level is read_write."""
        _plugin_context.schema = "my_namespace"
        _plugin_context.access_level = "read_write"

        model = MockModel()
        # Should not raise
        model._check_write_permission()

    def test_check_write_permission_denies_when_read_only_access(self) -> None:
        """Write operations should be denied when access level is read."""
        _plugin_context.schema = "my_namespace"
        _plugin_context.access_level = "read"

        model = MockModel()
        with pytest.raises(NamespaceWriteDenied) as exc_info:
            model._check_write_permission()

        assert "my_namespace" in str(exc_info.value)
        assert "read-only" in str(exc_info.value)
        assert "read_write" in str(exc_info.value)

    def test_check_write_permission_denies_with_default_access_level(self) -> None:
        """Write operations should be denied when access level defaults to read."""
        _plugin_context.schema = "my_namespace"
        # Don't set access_level - it should default to "read"

        model = MockModel()
        with pytest.raises(NamespaceWriteDenied):
            model._check_write_permission()


class TestModelSaveWritePermission:
    """Tests for write permission enforcement in Model.save()."""

    def setup_method(self) -> None:
        """Clear any existing plugin context before each test."""
        clear_current_plugin()
        for attr in ("schema", "access_level"):
            if hasattr(_plugin_context, attr):
                delattr(_plugin_context, attr)

    def test_save_raises_when_read_only(self) -> None:
        """Model.save() should raise NamespaceWriteDenied when access is read-only."""
        _plugin_context.schema = "test_namespace"
        _plugin_context.access_level = "read"

        model = MockModel()
        with pytest.raises(NamespaceWriteDenied) as exc_info:
            model.save()

        assert "test_namespace" in str(exc_info.value)

    def test_save_calls_parent_when_write_allowed(self) -> None:
        """Model.save() should call parent save when write is allowed."""
        _plugin_context.schema = "test_namespace"
        _plugin_context.access_level = "read_write"

        model = MockModel()

        # Mock the parent save to avoid database operations
        with patch.object(Model.__bases__[0], "save", return_value=None) as mock_save:
            model.save()
            mock_save.assert_called_once()

    def test_save_succeeds_without_context(self) -> None:
        """CustomModel.save() should succeed when not in a plugin context."""
        model = MockModel()

        # Mock the parent save to avoid database operations
        with patch.object(Model.__bases__[0], "save", return_value=None) as mock_save:
            model.save()
            mock_save.assert_called_once()


class TestModelDeleteWritePermission:
    """Tests for write permission enforcement in Model.delete()."""

    def setup_method(self) -> None:
        """Clear any existing plugin context before each test."""
        clear_current_plugin()
        for attr in ("schema", "access_level"):
            if hasattr(_plugin_context, attr):
                delattr(_plugin_context, attr)

    def test_delete_raises_when_read_only(self) -> None:
        """Model.delete() should raise NamespaceWriteDenied when access is read-only."""
        _plugin_context.schema = "test_namespace"
        _plugin_context.access_level = "read"

        model = MockModel()
        with pytest.raises(NamespaceWriteDenied) as exc_info:
            model.delete()

        assert "test_namespace" in str(exc_info.value)

    def test_delete_calls_parent_when_write_allowed(self) -> None:
        """Model.delete() should call parent delete when write is allowed."""
        _plugin_context.schema = "test_namespace"
        _plugin_context.access_level = "read_write"

        model = MockModel()

        # Mock the parent delete to avoid database operations
        with patch.object(
            Model.__bases__[0], "delete", return_value=(1, {"test.MockModel": 1})
        ) as mock_delete:
            result = model.delete()
            mock_delete.assert_called_once()
            assert result == (1, {"test.MockModel": 1})

    def test_delete_succeeds_without_context(self) -> None:
        """Model.delete() should succeed when not in a plugin context."""
        model = MockModel()

        # Mock the parent delete to avoid database operations
        with patch.object(
            Model.__bases__[0], "delete", return_value=(1, {"test.MockModel": 1})
        ) as mock_delete:
            model.delete()
            mock_delete.assert_called_once()


class TestWritePermissionWithContextManager:
    """Tests for write permission with plugin_database_context."""

    def test_write_denied_in_read_only_context(self) -> None:
        """Write operations should be denied in a read-only context."""
        from canvas_sdk.v1.plugin_database_context import plugin_database_context

        with plugin_database_context("my_plugin", namespace="shared_ns", access_level="read"):
            model = MockModel()
            with pytest.raises(NamespaceWriteDenied):
                model.save()

    def test_write_allowed_in_read_write_context(self) -> None:
        """Write operations should be allowed in a read_write context."""
        from canvas_sdk.v1.plugin_database_context import plugin_database_context

        with plugin_database_context("my_plugin", namespace="shared_ns", access_level="read_write"):
            model = MockModel()
            # Mock parent save to avoid database operations
            with patch.object(Model.__bases__[0], "save", return_value=None):
                model.save()  # Should not raise


class TestFieldSizeValidation:
    """Tests for field size validation in CustomModel.save()."""

    def test_save_raises_when_text_field_exceeds_limit(self) -> None:
        """save() should raise FieldValueTooLarge when a TextField value exceeds the limit."""
        model = MockModelWithFields()
        model.text_field = "x" * (MAX_FIELD_SIZE + 1)

        with pytest.raises(FieldValueTooLarge, match="text_field"):
            model.save()

    def test_save_raises_when_json_field_exceeds_limit(self) -> None:
        """save() should raise FieldValueTooLarge when a JSONField serialized value exceeds the limit."""
        model = MockModelWithFields()
        model.json_field = {"data": "x" * MAX_FIELD_SIZE}

        with pytest.raises(FieldValueTooLarge, match="json_field"):
            model.save()

    def test_save_allows_text_field_at_limit(self) -> None:
        """save() should allow a TextField value exactly at the limit."""
        model = MockModelWithFields()
        model.text_field = "x" * MAX_FIELD_SIZE

        with patch.object(Model.__bases__[0], "save", return_value=None):
            model.save()  # Should not raise

    def test_save_allows_none_values(self) -> None:
        """save() should allow None values on TextField and JSONField."""
        model = MockModelWithFields()
        model.text_field = None
        model.json_field = None

        with patch.object(Model.__bases__[0], "save", return_value=None):
            model.save()  # Should not raise
