"""Tests for the created/modified columns generated on every custom table.

Tests verify that:
1. A concrete CustomModel is given created and modified
2. The generated fields are auto_now_add / auto_now and nullable
3. Abstract and proxy CustomModels are left alone
4. A model bringing its own created or modified keeps it
5. Each model gets its own field instances
6. The columns reach the generated DDL
7. save(), bulk_create(), update() and bulk_update() all populate them
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from django.db import models
from freezegun import freeze_time

from canvas_sdk.v1.data.base import (
    CustomModel,
    CustomModelManager,
    auto_now_field_names,
    build_auto_timestamp_fields,
)
from plugin_runner.ddl import execute_create_table_sql, generate_create_table_sql

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class PlainCustomModel(CustomModel):
    """A model that declares no metadata of its own."""

    class Meta:
        app_label = "test_plugin"

    name = models.TextField(null=True)


class SecondPlainCustomModel(CustomModel):
    """A second bare model, used to prove field instances are not shared."""

    class Meta:
        app_label = "test_plugin"


class AbstractCustomBase(CustomModel):
    """An abstract intermediate, which should get no columns of its own."""

    class Meta:
        abstract = True
        app_label = "test_plugin"

    note = models.TextField(null=True)


class ConcreteFromAbstract(AbstractCustomBase):
    """A concrete model whose parent is an abstract CustomModel."""

    class Meta:
        app_label = "test_plugin"


class DeclaresOwnCreated(CustomModel):
    """A model that already spells created its own way, as a free-text column."""

    class Meta:
        app_label = "test_plugin"

    created = models.TextField(null=True)


class LegacyTimestampMixin(models.Model):
    """A plain abstract Model supplying created, the shape plugins use today."""

    class Meta:
        abstract = True
        app_label = "test_plugin"

    created = models.DateTimeField(auto_now_add=True, null=True)


class InheritsCreatedFromMixin(LegacyTimestampMixin, CustomModel):
    """A concrete model taking created from a mixin and modified from the SDK."""

    class Meta:
        app_label = "test_plugin"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def plain_table(db: None) -> None:
    """Create PlainCustomModel's table using the production DDL path."""
    execute_create_table_sql(generate_create_table_sql("test_plugin", PlainCustomModel))


# ---------------------------------------------------------------------------
# Field generation
# ---------------------------------------------------------------------------


def test_concrete_model_is_given_both_timestamps() -> None:
    """A CustomModel declaring no metadata should still have created and modified."""
    field_names = {field.name for field in PlainCustomModel._meta.local_fields}

    assert {"created", "modified"} <= field_names


def test_created_is_populated_on_insert_only() -> None:
    """The created column should be auto_now_add, so later saves leave it alone."""
    created = PlainCustomModel._meta.get_field("created")

    assert isinstance(created, models.DateTimeField)
    assert created.auto_now_add is True
    assert created.auto_now is False


def test_modified_is_populated_on_every_save() -> None:
    """The modified column should be auto_now."""
    modified = PlainCustomModel._meta.get_field("modified")

    assert isinstance(modified, models.DateTimeField)
    assert modified.auto_now is True
    assert modified.auto_now_add is False


def test_generated_timestamps_are_nullable() -> None:
    """Rows written before the column existed hold NULL, so the fields allow it."""
    for field_name in ("created", "modified"):
        field = PlainCustomModel._meta.get_field(field_name)
        assert isinstance(field, models.DateTimeField)
        assert field.null is True


def test_each_model_gets_its_own_field_instances() -> None:
    """A Field instance belongs to one model, so the two models must not share one."""
    first = PlainCustomModel._meta.get_field("created")
    second = SecondPlainCustomModel._meta.get_field("created")

    assert first is not second


def test_abstract_custom_model_gets_no_timestamps() -> None:
    """An abstract intermediate should not declare the columns itself."""
    field_names = {field.name for field in AbstractCustomBase._meta.local_fields}

    assert "created" not in field_names
    assert "modified" not in field_names


def test_concrete_child_of_abstract_gets_them_exactly_once() -> None:
    """The concrete model below an abstract CustomModel gets one of each."""
    names = [field.name for field in ConcreteFromAbstract._meta.local_fields]

    assert names.count("created") == 1
    assert names.count("modified") == 1


def test_declared_created_is_left_alone() -> None:
    """A model declaring its own created keeps that field, whatever its type."""
    created = DeclaresOwnCreated._meta.get_field("created")

    assert isinstance(created, models.TextField)


def test_declared_created_still_receives_modified() -> None:
    """Only the name the model already uses is skipped; the other is still added."""
    modified = DeclaresOwnCreated._meta.get_field("modified")

    assert isinstance(modified, models.DateTimeField)
    assert modified.auto_now is True


def test_created_inherited_from_a_mixin_does_not_clash() -> None:
    """A created supplied by a plain abstract mixin suppresses the generated one.

    Two fields of the same name is a hard error at class-definition time, which
    would keep the plugin from loading at all.
    """
    names = [field.name for field in InheritsCreatedFromMixin._meta.local_fields]

    assert names.count("created") == 1
    assert names.count("modified") == 1


def test_build_auto_timestamp_fields_returns_new_objects() -> None:
    """Each call should hand back unattached field instances."""
    first = build_auto_timestamp_fields()
    second = build_auto_timestamp_fields()

    assert first.keys() == {"created", "modified"}
    assert first["created"] is not second["created"]


def test_auto_now_field_names_finds_only_auto_now_fields() -> None:
    """The helper should report modified and not created."""
    assert auto_now_field_names(PlainCustomModel) == ["modified"]


def test_auto_now_field_names_ignores_a_non_datetime_field() -> None:
    """A model whose created is free text should not have it reported."""
    assert auto_now_field_names(DeclaresOwnCreated) == ["modified"]


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------


def test_generated_ddl_includes_both_columns() -> None:
    """The columns should reach the SQL the plugin installer runs."""
    sql = generate_create_table_sql("test_plugin", PlainCustomModel)

    assert "created datetime" in sql
    assert "modified datetime" in sql


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_save_populates_both_timestamps(plain_table: None) -> None:
    """An inserted row should carry both timestamps."""
    with freeze_time("2026-09-10 12:00:00"):
        row = PlainCustomModel.objects.create(name="first")

    assert row.created == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    assert row.modified == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_resaving_advances_modified_and_leaves_created(plain_table: None) -> None:
    """A second save should move modified only."""
    with freeze_time("2026-09-10 12:00:00"):
        row = PlainCustomModel.objects.create(name="first")

    with freeze_time("2026-09-10 13:00:00"):
        row.name = "second"
        row.save()

    row.refresh_from_db()

    assert row.created == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    assert row.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_bulk_create_populates_both_timestamps(plain_table: None) -> None:
    """Rows inserted through bulk_create should be stamped too."""
    with freeze_time("2026-09-10 12:00:00"):
        PlainCustomModel.objects.bulk_create(
            [PlainCustomModel(name="a"), PlainCustomModel(name="b")]
        )

    for row in PlainCustomModel.objects.all():
        assert row.created == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
        assert row.modified == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_queryset_update_advances_modified(plain_table: None) -> None:
    """A set-based update should stamp modified, which Django itself skips."""
    with freeze_time("2026-09-10 12:00:00"):
        PlainCustomModel.objects.create(name="first")

    with freeze_time("2026-09-10 13:00:00"):
        PlainCustomModel.objects.filter(name="first").update(name="second")

    row = PlainCustomModel.objects.get()

    assert row.created == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    assert row.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_queryset_update_keeps_an_explicit_modified(plain_table: None) -> None:
    """A caller writing modified itself should win over the stamp."""
    with freeze_time("2026-09-10 12:00:00"):
        PlainCustomModel.objects.create(name="first")

    chosen = datetime(2020, 1, 1, tzinfo=UTC)
    with freeze_time("2026-09-10 13:00:00"):
        PlainCustomModel.objects.all().update(modified=chosen)

    assert PlainCustomModel.objects.get().modified == chosen


@pytest.mark.django_db
def test_bulk_update_advances_modified(plain_table: None) -> None:
    """bulk_update should stamp modified without the caller listing the field."""
    with freeze_time("2026-09-10 12:00:00"):
        row = PlainCustomModel.objects.create(name="first")

    with freeze_time("2026-09-10 13:00:00"):
        row.name = "second"
        PlainCustomModel.objects.bulk_update([row], ["name"])

    stored = PlainCustomModel.objects.get()

    assert stored.name == "second"
    assert stored.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_update_returns_the_row_count(plain_table: None) -> None:
    """Stamping must not change what update() reports."""
    PlainCustomModel.objects.create(name="first")
    PlainCustomModel.objects.create(name="second")

    assert PlainCustomModel.objects.all().update(name="same") == 2


def test_custom_model_uses_the_stamping_manager() -> None:
    """CustomModel subclasses should get the manager that stamps auto_now fields."""
    assert isinstance(PlainCustomModel.objects, CustomModelManager)


def test_manager_passes_through_unknown_kwargs() -> None:
    """The queryset should still be a plain Django queryset for everything else."""
    queryset: Any = PlainCustomModel.objects.filter(name="x")

    assert isinstance(queryset, models.QuerySet)
