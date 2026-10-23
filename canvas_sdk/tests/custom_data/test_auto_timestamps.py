"""Tests for the created/modified columns generated on every custom table.

Tests verify that:
1. A concrete CustomModel is given created and modified
2. The generated fields are auto_now_add / auto_now and nullable
3. An abstract intermediate passes them down exactly once
4. A model bringing its own created or modified keeps it
5. Each model gets its own field instances
6. The columns reach the generated DDL
7. save(), bulk_create(), update() and bulk_update() all populate them
8. A mixin listed ahead of CustomModel keeps its fields and the stamping manager;
   one listed after it, which would lose them, is refused
9. A row written before the columns existed reads NULL and gains modified on its next write
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from django.db import connection, models
from freezegun import freeze_time

from canvas_sdk.v1.data.base import (
    CustomModel,
    CustomModelManager,
    auto_now_field_names,
)
from plugin_runner.ddl import (
    execute_create_table_sql,
    generate_create_table_sql,
    generate_field_sql,
)

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
    """An abstract intermediate between CustomModel and a concrete table."""

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

    created = models.TextField(null=True)  # type: ignore[assignment]


class DeclaresOwnModifiedAsText(CustomModel):
    """A model holding modified as an ISO-8601 string, as some deployed plugins do."""

    class Meta:
        app_label = "test_plugin"

    modified = models.CharField(max_length=64, null=True)  # type: ignore[assignment]


class CreatedIsAProperty(CustomModel):
    """A model exposing created as a computed property rather than a column."""

    class Meta:
        app_label = "test_plugin"

    @property
    def created(self) -> str:  # type: ignore[override]
        """Return a computed value."""
        return "computed"


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


class AuditedFieldsMixin(models.Model):
    """Strive's AuditedFields shape: both timestamps, non-null, on a plain abstract Model."""

    class Meta:
        abstract = True
        app_label = "test_plugin"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class InheritsBothFromMixin(AuditedFieldsMixin, CustomModel):  # type: ignore[misc]
    """A concrete model listing the mixin ahead of CustomModel, as Strive's plugins do."""

    class Meta:
        app_label = "test_plugin"

    name = models.TextField(null=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def plain_table(db: None) -> None:
    """Create PlainCustomModel's table using the production DDL path."""
    execute_create_table_sql(generate_create_table_sql("test_plugin", PlainCustomModel))


@pytest.fixture
def mixin_table(db: None) -> None:
    """Create InheritsBothFromMixin's table using the production DDL path."""
    execute_create_table_sql(generate_create_table_sql("test_plugin", InheritsBothFromMixin))


@pytest.fixture
def legacy_plain_table(db: None) -> None:
    """Build PlainCustomModel's table as it stood before the timestamps, holding one row.

    Then add the two columns the way a deploy does: a bare ADD COLUMN with the
    installer's column type and no default.
    """
    table = PlainCustomModel._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE TABLE {table} (dbid integer PRIMARY KEY AUTOINCREMENT, name text)")
        cursor.execute(f"INSERT INTO {table} (name) VALUES ('written before the deploy')")
        for field in PlainCustomModel._meta.local_fields:
            if field.name not in ("created", "modified"):
                continue
            column_type = generate_field_sql(field, connection)
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {field.column} {column_type}")


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
    """A created supplied by an abstract mixin listed first wins over CustomModel's."""
    names = [field.name for field in InheritsCreatedFromMixin._meta.local_fields]

    assert names.count("created") == 1
    assert names.count("modified") == 1


def test_declared_modified_string_is_left_alone() -> None:
    """A model storing modified as ISO-8601 text keeps its text column."""
    modified = DeclaresOwnModifiedAsText._meta.get_field("modified")

    assert isinstance(modified, models.CharField)
    assert auto_now_field_names(DeclaresOwnModifiedAsText) == []


def test_created_property_suppresses_the_column() -> None:
    """A model defining created as a property keeps the property and gets no column."""
    field_names = {field.name for field in CreatedIsAProperty._meta.local_fields}

    assert "created" not in field_names
    assert "modified" in field_names
    assert CreatedIsAProperty(dbid=1).created == "computed"


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


def test_mixin_fields_win_when_listed_first() -> None:
    """A mixin supplying both timestamps keeps its own fields, non-null as declared."""
    created = InheritsBothFromMixin._meta.get_field("created")
    modified = InheritsBothFromMixin._meta.get_field("modified")

    assert isinstance(created, models.DateTimeField)
    assert isinstance(modified, models.DateTimeField)
    assert created.model is InheritsBothFromMixin
    assert created.null is False
    assert modified.null is False
    assert auto_now_field_names(InheritsBothFromMixin) == ["modified"]


def test_field_mixin_listed_after_custom_model_is_rejected() -> None:
    """CustomModel's field would silently replace the mixin's, so the class must not load."""

    class TextTimestampMixin(models.Model):
        class Meta:
            abstract = True
            app_label = "test_plugin"

        created = models.TextField(null=True)

    with pytest.raises(ValueError, match="list TextTimestampMixin before CustomModel"):

        class ListsFieldMixinLast(CustomModel, TextTimestampMixin):  # type: ignore[misc]
            class Meta:
                app_label = "test_plugin"


def test_property_mixin_listed_after_custom_model_is_rejected() -> None:
    """A plain class supplying modified as a property loses it the same way."""

    class ComputedModified:
        @property
        def modified(self) -> str:
            return "computed"

    with pytest.raises(ValueError, match="list ComputedModified before CustomModel"):

        class ListsPropertyMixinLast(CustomModel, ComputedModified):  # type: ignore[misc]
            class Meta:
                app_label = "test_plugin"


def test_mixin_after_an_intermediate_that_declares_its_own_is_allowed() -> None:
    """When an earlier base already supplies created, CustomModel's field is not in play."""

    class DeclaresCreatedBase(CustomModel):
        class Meta:
            abstract = True
            app_label = "test_plugin"

        created = models.TextField(null=True)  # type: ignore[assignment]

    class OtherCreated:
        created = "unused"

    class Allowed(DeclaresCreatedBase, OtherCreated):  # type: ignore[misc]
        class Meta:
            app_label = "test_plugin"

    assert isinstance(Allowed._meta.get_field("created"), models.TextField)


def test_mixin_first_model_uses_the_stamping_manager() -> None:
    """Listing a plain abstract mixin first must not displace CustomModel's manager."""
    assert isinstance(InheritsBothFromMixin.objects, CustomModelManager)


@pytest.mark.django_db
def test_queryset_update_advances_a_mixin_supplied_modified(mixin_table: None) -> None:
    """update() should stamp a modified that comes from the plugin's own mixin."""
    with freeze_time("2026-09-10 12:00:00"):
        InheritsBothFromMixin.objects.create(name="first")

    with freeze_time("2026-09-10 13:00:00"):
        InheritsBothFromMixin.objects.filter(name="first").update(name="second")

    row = InheritsBothFromMixin.objects.get()

    assert row.created == datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    assert row.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_row_written_before_the_columns_existed_reads_null(legacy_plain_table: None) -> None:
    """A row older than the columns loads, with both timestamps unknown."""
    row = PlainCustomModel.objects.get()

    assert row.name == "written before the deploy"
    assert row.created is None
    assert row.modified is None


@pytest.mark.django_db
def test_resaving_a_pre_deploy_row_stamps_modified_only(legacy_plain_table: None) -> None:
    """Saving an old row records the write, and created stays unknown rather than invented."""
    row = PlainCustomModel.objects.get()

    with freeze_time("2026-09-10 13:00:00"):
        row.name = "edited"
        row.save()

    row.refresh_from_db()

    assert row.created is None
    assert row.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


@pytest.mark.django_db
def test_update_stamps_a_pre_deploy_row(legacy_plain_table: None) -> None:
    """A set-based update on an old row stamps modified and leaves created unknown."""
    with freeze_time("2026-09-10 13:00:00"):
        PlainCustomModel.objects.all().update(name="edited")

    row = PlainCustomModel.objects.get()

    assert row.created is None
    assert row.modified == datetime(2026, 9, 10, 13, 0, tzinfo=UTC)


def test_custom_model_uses_the_stamping_manager() -> None:
    """CustomModel subclasses should get the manager that stamps auto_now fields."""
    assert isinstance(PlainCustomModel.objects, CustomModelManager)


def test_manager_passes_through_unknown_kwargs() -> None:
    """The queryset should still be a plain Django queryset for everything else."""
    queryset: Any = PlainCustomModel.objects.filter(name="x")

    assert isinstance(queryset, models.QuerySet)
