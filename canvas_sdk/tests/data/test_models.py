import importlib
import inspect
import pkgutil
import uuid
from unittest.mock import patch

import pytest
from django.contrib.postgres.fields import ArrayField
from django.core.management import call_command
from django.db import models as django_models

from canvas_sdk.v1 import data
from canvas_sdk.v1.data.base import IdentifiableModel, Model


@pytest.fixture(scope="module")
def TestModel() -> type[IdentifiableModel]:
    """Fixture to create a test model with an ArrayField."""

    class TestModel(IdentifiableModel):
        """A test model."""

        array_field = ArrayField(django_models.CharField(max_length=64))

        class Meta:
            app_label = "tests"

    return TestModel


def get_django_model_classes_from_data() -> set[str]:
    """Collect names of all top-level Django model classes."""
    model_class_names = set()

    for _, module_name, _ in pkgutil.iter_modules(data.__path__):
        if module_name.startswith("_"):
            continue

        full_module_name = f"{data.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                obj.__module__ == full_module_name
                and issubclass(obj, django_models.Model)
                and not getattr(obj._meta, "abstract", False)
            ):
                model_class_names.add(name)

    return model_class_names


def test_django_model_checks() -> None:
    """Run Django's system checks limited to the 'models' tag."""
    call_command("check", "--tag", "models")


def test_all_django_models_are_exported() -> None:
    """Ensure all concrete Django models are exported in the data module's __all__."""
    declared_exports = set(getattr(data, "__all__", []))
    model_classes = get_django_model_classes_from_data()

    missing = model_classes - declared_exports
    assert not missing, f"Django models missing from __all__: {sorted(missing)}"


def test_postgres_array_field_swapped(TestModel: type[IdentifiableModel]) -> None:
    """Ensure that ArrayField is swapped with JSONField for SQLite."""
    field = TestModel._meta.get_field("array_field")

    assert isinstance(field, django_models.JSONField), (
        f"Expected `array_field` to be swapped to JSONField, got {type(field)}"
    )


def test_model_meta_property_managed_is_populated_correctly(
    TestModel: type[IdentifiableModel],
) -> None:
    """Ensure that the `managed` property is set correctly based on the database type."""
    assert TestModel._meta.managed

    with patch("canvas_sdk.v1.data.base.IS_SQLITE", False):
        # Simulate a non-SQLite environment
        class TestModelNonSqlite(Model):
            class Meta:
                app_label = "tests"

        assert not TestModelNonSqlite._meta.managed

    class TestModelManagedFalse(Model):
        """A test model that sets managed prop."""

        class Meta:
            app_label = "tests"
            managed = False

    assert not TestModelManagedFalse._meta.managed


def test_identifiable_model_has_uuid_field(TestModel: type[IdentifiableModel]) -> None:
    """Ensure that IdentifiableModel generates UUID by default."""
    model = TestModel()
    assert isinstance(model.id, uuid.UUID)
