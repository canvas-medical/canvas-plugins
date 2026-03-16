"""Tests for SQL generation from CustomModel definitions.

Tests cover:
1. CustomModels with all supported data types
2. Foreign key attributes and automatic indexing on key columns
3. All index types: single column, multiple column, GIN, and descending
4. Both PostgreSQL and SQLite SQL generation
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.postgres.indexes import GinIndex
from django.db import connection, models

from canvas_sdk.v1.data.base import CustomModel, Model, ModelExtension
from plugin_runner.ddl import (
    SQL_STATEMENT_DELIMITER,
    generate_constraint_sql,
    generate_create_table_sql,
    generate_field_sql,
    generate_index_sql,
)

# ---------------------------------------------------------------------------
# Test Models with all supported data types
# Note: CustomModelMetaclass sets db_table to the lowercased class name
# ---------------------------------------------------------------------------


class AllDataTypesModel(CustomModel):
    """A model containing all supported field types."""

    class Meta:
        app_label = "test_plugin"

    text_field = models.TextField()
    char_field = models.CharField(max_length=100)
    int_field = models.IntegerField()
    bool_field = models.BooleanField()
    date_field = models.DateField()
    datetime_field = models.DateTimeField()
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
    json_field = models.JSONField()


class DecimalPrecisionModel(CustomModel):
    """A model to test decimal field precision handling."""

    class Meta:
        app_label = "test_plugin"

    default_decimal = models.DecimalField()
    precise_decimal = models.DecimalField(max_digits=30, decimal_places=15)


# ---------------------------------------------------------------------------
# Test Models with foreign key relationships
# ---------------------------------------------------------------------------


class ParentModel(CustomModel):
    """A parent model for foreign key tests."""

    class Meta:
        app_label = "test_plugin"

    name = models.TextField()


class ChildWithForeignKey(CustomModel):
    """A model with a ForeignKey to test automatic index creation."""

    class Meta:
        app_label = "test_plugin"

    parent = models.ForeignKey(ParentModel, on_delete=models.DO_NOTHING)
    description = models.TextField()


class ChildWithOneToOne(CustomModel):
    """A model with a OneToOneField to test automatic index creation."""

    class Meta:
        app_label = "test_plugin"

    parent = models.OneToOneField(ParentModel, on_delete=models.DO_NOTHING)
    extra_data = models.TextField()


class MultipleForeignKeysModel(CustomModel):
    """A model with multiple foreign keys targeting a CustomModel (no namespacing)."""

    class Meta:
        app_label = "test_plugin"

    parent_one = models.ForeignKey(
        ParentModel, on_delete=models.DO_NOTHING, related_name="children_one"
    )
    parent_two = models.ForeignKey(
        ParentModel, on_delete=models.DO_NOTHING, related_name="children_two"
    )
    value = models.IntegerField()


# ---------------------------------------------------------------------------
# Test Models for related_name validation
# ---------------------------------------------------------------------------


class SDKModel(Model):
    """A stand-in for an SDK model (inherits from Model, not CustomModel).

    FK/OneToOne fields targeting this must use a namespaced related_name
    because SDK models are shared across plugins.
    """

    class Meta:
        app_label = "canvas_sdk"
        managed = False


class NamespacedRelatedNameModel(CustomModel):
    """A model with a template-namespaced related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(
        SDKModel, on_delete=models.DO_NOTHING, related_name="%(app_label)s_custom"
    )


class HardcodedNamespacedModel(CustomModel):
    """A model with a hardcoded app_label prefix in related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(
        SDKModel, on_delete=models.DO_NOTHING, related_name="canvas_sdk_hardcoded"
    )


class PlusRelatedNameModel(CustomModel):
    """A model with related_name='+' (no reverse relation) targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.ForeignKey(SDKModel, on_delete=models.DO_NOTHING, related_name="+")


class NoExplicitRelatedNameModel(CustomModel):
    """A model with no explicit related_name targeting an SDK model."""

    class Meta:
        app_label = "test_plugin"

    sdk_ref = models.OneToOneField(SDKModel, on_delete=models.DO_NOTHING)


class CustomModelTargetModel(CustomModel):
    """A model with a non-namespaced related_name on a FK targeting another CustomModel.

    This is allowed because CustomModels are plugin-private and can't collide.
    """

    class Meta:
        app_label = "test_plugin"

    parent = models.ForeignKey(ParentModel, on_delete=models.DO_NOTHING, related_name="children")


class SDKModelProxy(SDKModel, ModelExtension):
    """A proxy of an SDK model, as plugins typically create."""

    class Meta:
        app_label = "test_plugin"
        proxy = True


class ProxyTargetModel(CustomModel):
    """A model with a non-namespaced related_name on a FK targeting a proxy model.

    This is allowed because proxy models are plugin-private.
    """

    class Meta:
        app_label = "test_plugin"

    proxy_ref = models.OneToOneField(
        SDKModelProxy, on_delete=models.DO_NOTHING, related_name="biography"
    )


# ---------------------------------------------------------------------------
# Test Models with uniqueness constraints
# ---------------------------------------------------------------------------


class SingleColumnUniqueModel(CustomModel):
    """A model with a single-column UniqueConstraint."""

    class Meta:
        app_label = "test_plugin"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="uq_email"),
        ]

    email = models.TextField()
    name = models.TextField()


class MultiColumnUniqueModel(CustomModel):
    """A model with a multi-column UniqueConstraint."""

    class Meta:
        app_label = "test_plugin"
        constraints = [
            models.UniqueConstraint(fields=["tenant_id", "slug"], name="uq_tenant_slug"),
        ]

    tenant_id = models.IntegerField()
    slug = models.TextField()
    title = models.TextField()


class MultipleUniqueConstraintsModel(CustomModel):
    """A model with multiple UniqueConstraints."""

    class Meta:
        app_label = "test_plugin"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_code"),
            models.UniqueConstraint(fields=["category", "name"], name="uq_cat_name"),
        ]

    code = models.TextField()
    category = models.TextField()
    name = models.TextField()


# ---------------------------------------------------------------------------
# Test Models with OneToOneField(primary_key=True)
# ---------------------------------------------------------------------------


class OneToOnePKModel(CustomModel):
    """A model where a OneToOneField is the primary key, replacing dbid."""

    class Meta:
        app_label = "test_plugin"

    parent = models.OneToOneField(ParentModel, on_delete=models.DO_NOTHING, primary_key=True)
    extra = models.TextField()


# ---------------------------------------------------------------------------
# Test Models with various index types
# ---------------------------------------------------------------------------


class SingleColumnIndexModel(CustomModel):
    """A model with a single column index."""

    class Meta:
        app_label = "test_plugin"
        indexes = [
            models.Index(fields=["name"], name="idx_name"),
        ]

    name = models.TextField()
    value = models.IntegerField()


class MultiColumnIndexModel(CustomModel):
    """A model with a multi-column index."""

    class Meta:
        app_label = "test_plugin"
        indexes = [
            models.Index(fields=["first_name", "last_name"], name="idx_full_name"),
        ]

    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()


class DescendingIndexModel(CustomModel):
    """A model with descending order indexes."""

    class Meta:
        app_label = "test_plugin"
        indexes = [
            models.Index(fields=["-created_at"], name="idx_created_desc"),
            models.Index(fields=["category", "-priority"], name="idx_cat_pri_desc"),
        ]

    category = models.TextField()
    priority = models.IntegerField()
    created_at = models.DateTimeField()


class GinIndexModel(CustomModel):
    """A model with a GIN index on a JSONB field."""

    class Meta:
        app_label = "test_plugin"
        indexes = [
            GinIndex(fields=["metadata"], name="idx_metadata_gin"),
        ]

    metadata = models.JSONField()
    title = models.TextField()


class MixedIndexesModel(CustomModel):
    """A model with multiple index types combined."""

    class Meta:
        app_label = "test_plugin"
        indexes = [
            models.Index(fields=["status"], name="idx_status"),
            models.Index(fields=["category", "status"], name="idx_cat_status"),
            models.Index(fields=["-updated_at"], name="idx_updated_desc"),
            GinIndex(fields=["tags"], name="idx_tags_gin"),
        ]

    status = models.TextField()
    category = models.TextField()
    updated_at = models.DateTimeField()
    tags = models.JSONField()


# ===========================================================================
# Helper to create a mock PostgreSQL connection
# ===========================================================================


def _make_pg_connection() -> MagicMock:
    """Create a mock connection that simulates a PostgreSQL backend."""
    conn = MagicMock()
    conn.data_types = {
        "AutoField": "integer",
        "BigAutoField": "bigint",
        "BinaryField": "bytea",
        "BooleanField": "boolean",
        "CharField": "varchar(%(max_length)s)",
        "DateField": "date",
        "DateTimeField": "timestamp with time zone",
        "DecimalField": "numeric(%(max_digits)s, %(decimal_places)s)",
        "DurationField": "interval",
        "FloatField": "double precision",
        "IntegerField": "integer",
        "BigIntegerField": "bigint",
        "JSONField": "jsonb",
        "OneToOneField": "integer",
        "SmallAutoField": "smallint",
        "SmallIntegerField": "smallint",
        "TextField": "text",
    }
    conn.data_types_suffix = {
        "AutoField": "GENERATED BY DEFAULT AS IDENTITY",
        "BigAutoField": "GENERATED BY DEFAULT AS IDENTITY",
        "SmallAutoField": "GENERATED BY DEFAULT AS IDENTITY",
    }
    return conn


# ===========================================================================
# Tests for generate_field_sql - PostgreSQL
# ===========================================================================


class TestGenerateFieldSqlPostgres:
    """Tests for PostgreSQL field SQL generation."""

    def setup_method(self) -> None:
        """Set up the mock connection."""
        self.pg_connection = _make_pg_connection()

    def test_bigautofield_primary_key(self) -> None:
        """BigAutoField should generate bigint PRIMARY KEY with IDENTITY suffix."""
        field: models.Field = models.BigAutoField(primary_key=True)
        assert (
            generate_field_sql(field, self.pg_connection)
            == "bigint PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY"
        )

    def test_charfield(self) -> None:
        """CharField should generate text (overridden to avoid varchar migrations)."""
        field: models.Field = models.CharField(max_length=100)
        assert generate_field_sql(field, self.pg_connection) == "text"

    def test_textfield(self) -> None:
        """TextField should generate text for PostgreSQL."""
        field: models.Field = models.TextField()
        assert generate_field_sql(field, self.pg_connection) == "text"

    def test_integerfield(self) -> None:
        """IntegerField should generate integer for PostgreSQL."""
        field: models.Field = models.IntegerField()
        assert generate_field_sql(field, self.pg_connection) == "integer"

    def test_datefield(self) -> None:
        """DateField should generate date for PostgreSQL."""
        field: models.Field = models.DateField()
        assert generate_field_sql(field, self.pg_connection) == "date"

    def test_datetimefield(self) -> None:
        """DateTimeField should generate timestamp with time zone for PostgreSQL."""
        field: models.Field = models.DateTimeField()
        assert generate_field_sql(field, self.pg_connection) == "timestamp with time zone"

    def test_booleanfield(self) -> None:
        """BooleanField should generate boolean for PostgreSQL."""
        field: models.Field = models.BooleanField()
        assert generate_field_sql(field, self.pg_connection) == "boolean"

    def test_foreignkey(self) -> None:
        """ForeignKey to BigAutoField pk should generate bigint for PostgreSQL."""
        field: models.Field = ChildWithForeignKey._meta.get_field("parent")  # type: ignore[assignment]
        assert generate_field_sql(field, self.pg_connection) == "bigint"

    def test_onetoonefield(self) -> None:
        """OneToOneField to BigAutoField pk should generate bigint for PostgreSQL."""
        field: models.Field = ChildWithOneToOne._meta.get_field("parent")  # type: ignore[assignment]
        assert generate_field_sql(field, self.pg_connection) == "bigint"

    def test_decimalfield_with_precision(self) -> None:
        """DecimalField with explicit precision should generate numeric(m, d)."""
        field: models.Field = models.DecimalField(max_digits=10, decimal_places=2)
        assert generate_field_sql(field, self.pg_connection) == "numeric(10, 2)"

    def test_decimalfield_default_precision(self) -> None:
        """DecimalField without precision should default to numeric(20, 10)."""
        field: models.Field = models.DecimalField()
        assert generate_field_sql(field, self.pg_connection) == "numeric(20, 10)"

    def test_decimalfield_custom_large_precision(self) -> None:
        """DecimalField with large precision should generate matching numeric."""
        field: models.Field = models.DecimalField(max_digits=30, decimal_places=15)
        assert generate_field_sql(field, self.pg_connection) == "numeric(30, 15)"

    def test_jsonfield(self) -> None:
        """JSONField should generate jsonb for PostgreSQL."""
        field: models.Field = models.JSONField()
        assert generate_field_sql(field, self.pg_connection) == "jsonb"


# ===========================================================================
# Tests for generate_field_sql - SQLite
# ===========================================================================


class TestGenerateFieldSqlSqlite:
    """Tests for SQLite field SQL generation.

    Uses the real Django SQLite connection from the test environment.
    """

    def test_bigautofield_primary_key(self) -> None:
        """BigAutoField should generate integer PRIMARY KEY AUTOINCREMENT."""
        field: models.Field = models.BigAutoField(primary_key=True)
        assert generate_field_sql(field, connection) == "integer PRIMARY KEY AUTOINCREMENT"

    def test_charfield(self) -> None:
        """CharField should generate text (overridden to avoid varchar migrations)."""
        field: models.Field = models.CharField(max_length=100)
        assert generate_field_sql(field, connection) == "text"

    def test_textfield(self) -> None:
        """TextField should generate text for SQLite."""
        field: models.Field = models.TextField()
        assert generate_field_sql(field, connection) == "text"

    def test_integerfield(self) -> None:
        """IntegerField should generate integer for SQLite."""
        field: models.Field = models.IntegerField()
        assert generate_field_sql(field, connection) == "integer"

    def test_datefield(self) -> None:
        """DateField should generate date for SQLite."""
        field: models.Field = models.DateField()
        assert generate_field_sql(field, connection) == "date"

    def test_datetimefield(self) -> None:
        """DateTimeField should generate datetime for SQLite."""
        field: models.Field = models.DateTimeField()
        assert generate_field_sql(field, connection) == "datetime"

    def test_booleanfield(self) -> None:
        """BooleanField should generate bool for SQLite."""
        field: models.Field = models.BooleanField()
        assert generate_field_sql(field, connection) == "bool"

    def test_foreignkey(self) -> None:
        """ForeignKey to BigAutoField pk should generate bigint for SQLite."""
        field: models.Field = ChildWithForeignKey._meta.get_field("parent")  # type: ignore[assignment]
        assert generate_field_sql(field, connection) == "bigint"

    def test_onetoonefield(self) -> None:
        """OneToOneField to BigAutoField pk should generate bigint for SQLite."""
        field: models.Field = ChildWithOneToOne._meta.get_field("parent")  # type: ignore[assignment]
        assert generate_field_sql(field, connection) == "bigint"

    def test_decimalfield(self) -> None:
        """DecimalField should generate decimal for SQLite."""
        field: models.Field = models.DecimalField(max_digits=10, decimal_places=2)
        assert generate_field_sql(field, connection) == "decimal"

    def test_jsonfield(self) -> None:
        """JSONField should generate text for SQLite."""
        field: models.Field = models.JSONField()
        assert generate_field_sql(field, connection) == "text"


# ===========================================================================
# Tests for generate_index_sql - PostgreSQL
# ===========================================================================


class TestGenerateIndexSqlPostgres:
    """Tests for PostgreSQL index SQL generation."""

    def test_single_column_index(self) -> None:
        """Single column index should reference schema-qualified table."""
        index = models.Index(fields=["name"], name="idx_name")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql == "CREATE INDEX IF NOT EXISTS test_plugin_idx_name ON test_plugin.my_table (name);"
        )

    def test_multi_column_index(self) -> None:
        """Multi-column index should list all columns."""
        index = models.Index(fields=["first_name", "last_name"], name="idx_full_name")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_full_name ON test_plugin.my_table (first_name, last_name);"
        )

    def test_descending_single_column_index(self) -> None:
        """Descending index should append DESC to the column."""
        index = models.Index(fields=["-created_at"], name="idx_created_desc")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_created_desc ON test_plugin.my_table (created_at DESC);"
        )

    def test_descending_mixed_index(self) -> None:
        """Mixed ascending/descending index should only append DESC where needed."""
        index = models.Index(fields=["category", "-priority"], name="idx_cat_pri")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_cat_pri ON test_plugin.my_table (category, priority DESC);"
        )

    def test_gin_index(self) -> None:
        """GIN index should use USING GIN syntax."""
        index = GinIndex(fields=["metadata"], name="idx_metadata_gin")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_metadata_gin ON test_plugin.my_table USING GIN(metadata);"
        )

    def test_gin_index_multiple_fields(self) -> None:
        """GIN index with multiple fields should list all columns."""
        index = GinIndex(fields=["data", "tags"], name="idx_multi_gin")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=False)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_multi_gin ON test_plugin.my_table USING GIN(data, tags);"
        )


# ===========================================================================
# Tests for generate_index_sql - SQLite
# ===========================================================================


class TestGenerateIndexSqlSqlite:
    """Tests for SQLite index SQL generation."""

    def test_single_column_index(self) -> None:
        """Single column index should not use schema-qualified table name."""
        index = models.Index(fields=["name"], name="idx_name")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=True)
        assert sql == "CREATE INDEX IF NOT EXISTS test_plugin_idx_name ON my_table (name);"

    def test_multi_column_index(self) -> None:
        """Multi-column index should list all columns without schema prefix."""
        index = models.Index(fields=["first_name", "last_name"], name="idx_full_name")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=True)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_full_name ON my_table (first_name, last_name);"
        )

    def test_descending_index(self) -> None:
        """Descending index should append DESC to the column on SQLite."""
        index = models.Index(fields=["-created_at"], name="idx_created_desc")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=True)
        assert (
            sql
            == "CREATE INDEX IF NOT EXISTS test_plugin_idx_created_desc ON my_table (created_at DESC);"
        )

    def test_gin_index_falls_back_to_btree(self) -> None:
        """SQLite doesn't support GIN indexes, so it should fall back to regular index."""
        index = GinIndex(fields=["metadata"], name="idx_metadata_gin")
        sql = generate_index_sql("test_plugin", "my_table", index, is_sqlite=True)
        # GIN falls back to regular index for SQLite
        assert (
            sql == "CREATE INDEX IF NOT EXISTS test_plugin_idx_metadata_gin ON my_table (metadata);"
        )


# ===========================================================================
# Tests for generate_create_table_sql - SQLite (default test environment)
# ===========================================================================


class TestGenerateCreateTableSqlSqlite:
    """Tests for SQLite CREATE TABLE SQL generation.

    The test environment uses SQLite, so these tests run against the actual
    database configuration.
    """

    def test_all_data_types_creates_single_table_statement(self) -> None:
        """SQLite should have all fields in CREATE TABLE, no ALTER statements."""
        sql = generate_create_table_sql("test_plugin", AllDataTypesModel)
        statements = sql.split(SQL_STATEMENT_DELIMITER)

        create_stmt = statements[0]
        assert "CREATE TABLE IF NOT EXISTS alldatatypesmodel" in create_stmt
        # No schema prefix for SQLite
        assert "test_plugin.alldatatypesmodel" not in create_stmt

        # All fields should be in CREATE TABLE for SQLite
        assert "dbid integer PRIMARY KEY AUTOINCREMENT" in create_stmt
        assert "text_field text" in create_stmt
        assert "char_field text" in create_stmt
        assert "int_field integer" in create_stmt
        assert "bool_field bool" in create_stmt
        assert "date_field date" in create_stmt
        assert "datetime_field datetime" in create_stmt
        assert "decimal_field decimal" in create_stmt
        assert "json_field text" in create_stmt

        # No ALTER TABLE statements for SQLite
        alter_stmts = [s for s in statements if "ALTER TABLE" in s]
        assert len(alter_stmts) == 0

    def test_no_schema_prefix_in_table_name(self) -> None:
        """SQLite table names should not have a schema prefix."""
        sql = generate_create_table_sql("test_plugin", ParentModel)

        assert "CREATE TABLE IF NOT EXISTS parentmodel" in sql
        assert "test_plugin.parentmodel" not in sql

    def test_no_schema_prefix_in_indexes(self) -> None:
        """SQLite index definitions should not use schema-qualified table names."""
        sql = generate_create_table_sql("test_plugin", SingleColumnIndexModel)

        assert "ON singlecolumnindexmodel" in sql
        assert "ON test_plugin.singlecolumnindexmodel" not in sql

    def test_gin_index_falls_back_to_btree(self) -> None:
        """GIN indexes should fall back to regular indexes on SQLite."""
        sql = generate_create_table_sql("test_plugin", GinIndexModel)

        assert "USING GIN" not in sql
        assert (
            "CREATE INDEX IF NOT EXISTS test_plugin_idx_metadata_gin ON ginindexmodel (metadata)"
            in sql
        )

    def test_foreign_key_creates_index(self) -> None:
        """ForeignKey columns should have an auto-generated index."""
        sql = generate_create_table_sql("test_plugin", ChildWithForeignKey)

        assert "CREATE INDEX IF NOT EXISTS" in sql
        assert "parent_id" in sql

    def test_one_to_one_creates_index(self) -> None:
        """OneToOneField columns should have an auto-generated index."""
        sql = generate_create_table_sql("test_plugin", ChildWithOneToOne)

        assert "CREATE INDEX IF NOT EXISTS" in sql
        assert "parent_id" in sql

    def test_multiple_foreign_keys_create_multiple_indexes(self) -> None:
        """Each ForeignKey column should have its own auto-generated index."""
        sql = generate_create_table_sql("test_plugin", MultipleForeignKeysModel)

        assert sql.count("CREATE INDEX IF NOT EXISTS") >= 2
        assert "parent_one_id" in sql
        assert "parent_two_id" in sql

    def test_single_column_index(self) -> None:
        """Single column index should appear in generated SQL."""
        sql = generate_create_table_sql("test_plugin", SingleColumnIndexModel)

        assert (
            "CREATE INDEX IF NOT EXISTS test_plugin_idx_name ON singlecolumnindexmodel (name)"
            in sql
        )

    def test_multi_column_index(self) -> None:
        """Multi-column index should list all columns in generated SQL."""
        sql = generate_create_table_sql("test_plugin", MultiColumnIndexModel)

        assert (
            "CREATE INDEX IF NOT EXISTS test_plugin_idx_full_name ON multicolumnindexmodel (first_name, last_name)"
            in sql
        )

    def test_descending_index(self) -> None:
        """Descending indexes should include DESC in generated SQL."""
        sql = generate_create_table_sql("test_plugin", DescendingIndexModel)

        assert "created_at DESC" in sql
        assert "category, priority DESC" in sql

    def test_mixed_indexes_without_gin(self) -> None:
        """Test that mixed indexes work, with GIN falling back to regular index."""
        sql = generate_create_table_sql("test_plugin", MixedIndexesModel)

        assert "idx_status" in sql
        assert "idx_cat_status" in sql
        assert "updated_at DESC" in sql
        # GIN falls back to regular index
        assert "idx_tags_gin" in sql
        assert "USING GIN" not in sql


# ===========================================================================
# Tests for generate_create_table_sql - PostgreSQL (mocked)
# ===========================================================================


class TestGenerateCreateTableSqlPostgres:
    """Tests for PostgreSQL CREATE TABLE SQL generation.

    These tests patch IS_SQLITE to False to simulate a PostgreSQL environment.
    """

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_postgres_uses_schema_prefix(self) -> None:
        """PostgreSQL should use schema prefix in table names."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", AllDataTypesModel)

        assert "test_plugin.alldatatypesmodel" in sql

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_postgres_uses_alter_table_for_columns(self) -> None:
        """PostgreSQL should use ALTER TABLE for adding columns."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", AllDataTypesModel)

        # Should have ALTER TABLE statements
        assert "ALTER TABLE" in sql
        assert "ADD COLUMN IF NOT EXISTS" in sql

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_postgres_gin_index(self) -> None:
        """PostgreSQL should use USING GIN for GIN indexes."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", GinIndexModel)

        assert "USING GIN(metadata)" in sql


# ===========================================================================
# Tests for CustomModelMetaclass automatic index creation
# ===========================================================================


class TestCustomModelMetaclassIndexing:
    """Tests that CustomModelMetaclass automatically creates indexes for foreign keys."""

    def test_foreign_key_auto_indexed(self) -> None:
        """Foreign keys should automatically get indexes via metaclass."""
        indexes = ChildWithForeignKey._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert any("parent_id" in fields for fields in index_fields)

    def test_one_to_one_auto_indexed(self) -> None:
        """OneToOneField should automatically get indexes via metaclass."""
        indexes = ChildWithOneToOne._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert any("parent_id" in fields for fields in index_fields)

    def test_multiple_foreign_keys_all_indexed(self) -> None:
        """Multiple foreign keys should all get indexes."""
        indexes = MultipleForeignKeysModel._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert any("parent_one_id" in fields for fields in index_fields)
        assert any("parent_two_id" in fields for fields in index_fields)

    def test_explicit_indexes_preserved(self) -> None:
        """Explicitly defined indexes should be preserved alongside auto-generated ones."""
        indexes = MixedIndexesModel._meta.indexes
        index_names = [idx.name for idx in indexes]

        assert "idx_status" in index_names
        assert "idx_cat_status" in index_names
        assert "idx_updated_desc" in index_names
        assert "idx_tags_gin" in index_names

    def test_auto_generated_index_exists_for_fk(self) -> None:
        """Auto-generated indexes for FKs should exist."""
        indexes = ChildWithForeignKey._meta.indexes
        fk_indexes = [idx for idx in indexes if "parent_id" in idx.fields]

        assert len(fk_indexes) == 1
        # Django auto-generates a name for indexes
        assert fk_indexes[0].name is not None


# ===========================================================================
# Tests for CustomModel db_table naming
# ===========================================================================


class TestCustomModelDbTableNaming:
    """Tests that CustomModelMetaclass correctly sets db_table."""

    def test_db_table_is_lowercased_class_name(self) -> None:
        """db_table should be the lowercased class name."""
        assert AllDataTypesModel._meta.db_table == "alldatatypesmodel"
        assert ParentModel._meta.db_table == "parentmodel"
        assert ChildWithForeignKey._meta.db_table == "childwithforeignkey"

    def test_db_table_used_in_sql_generation(self) -> None:
        """Generated SQL should use the db_table value."""
        sql = generate_create_table_sql("test_plugin", AllDataTypesModel)

        assert "alldatatypesmodel" in sql
        # Should not use a different table name
        assert "all_data_types" not in sql


# ===========================================================================
# Tests for CustomModelMetaclass related_name auto-namespacing
# ===========================================================================


class TestCustomModelMetaclassRelatedName:
    """Tests that CustomModelMetaclass rejects non-namespaced related_name on
    FK/OneToOne fields targeting SDK models, while allowing them on fields
    targeting other CustomModels.
    """

    def test_non_namespaced_related_name_to_sdk_model_raises(self) -> None:
        """A bare related_name on a FK to an SDK model should raise ValueError."""
        with pytest.raises(ValueError, match="related_name='status'.*SDK model.*SDKModel"):
            type(
                "BadModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "BadModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "sdk_ref": models.ForeignKey(
                        SDKModel, on_delete=models.DO_NOTHING, related_name="status"
                    ),
                },
            )

    def test_template_namespaced_related_name_to_sdk_model_is_allowed(self) -> None:
        """A %(app_label)s-prefixed related_name on a FK to an SDK model should be accepted."""
        field = NamespacedRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "canvas_sdk_custom"

    def test_hardcoded_namespaced_related_name_to_sdk_model_is_allowed(self) -> None:
        """A related_name with hardcoded app_label_ prefix should be accepted."""
        field = HardcodedNamespacedModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "canvas_sdk_hardcoded"

    def test_plus_related_name_to_sdk_model_is_allowed(self) -> None:
        """related_name='+' should be accepted for SDK model targets."""
        field = PlusRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "+"

    def test_no_explicit_related_name_to_sdk_model_is_allowed(self) -> None:
        """No explicit related_name on a FK to an SDK model should be accepted."""
        # Django assigns None as the related_name when not specified.
        field = NoExplicitRelatedNameModel._meta.get_field("sdk_ref")
        assert isinstance(field, models.OneToOneField)
        assert field.remote_field.related_name is None

    def test_non_namespaced_related_name_to_custom_model_is_allowed(self) -> None:
        """A bare related_name on a FK to a CustomModel should be accepted."""
        field = CustomModelTargetModel._meta.get_field("parent")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.related_name == "children"

    def test_multiple_fk_to_custom_model_are_allowed(self) -> None:
        """Multiple FKs to a CustomModel with bare related_name should be accepted."""
        field_one = MultipleForeignKeysModel._meta.get_field("parent_one")
        field_two = MultipleForeignKeysModel._meta.get_field("parent_two")
        assert isinstance(field_one, models.ForeignKey)
        assert isinstance(field_two, models.ForeignKey)
        assert field_one.remote_field.related_name == "children_one"
        assert field_two.remote_field.related_name == "children_two"

    def test_non_namespaced_related_name_to_proxy_model_is_allowed(self) -> None:
        """A bare related_name on a FK to a proxy model should be accepted."""
        field = ProxyTargetModel._meta.get_field("proxy_ref")
        assert isinstance(field, models.OneToOneField)
        assert field.remote_field.related_name == "biography"

    def test_error_message_includes_fix_suggestion(self) -> None:
        """The error message should suggest the namespaced form."""
        with pytest.raises(ValueError, match=r"%\(app_label\)s_my_rel"):
            type(
                "BadModel2",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "BadModel2",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "sdk_ref": models.ForeignKey(
                        SDKModel, on_delete=models.DO_NOTHING, related_name="my_rel"
                    ),
                },
            )


# ===========================================================================
# Tests for CustomModelMetaclass unique=True rejection
# ===========================================================================


class TestCustomModelMetaclassUniqueFieldRejection:
    """Tests that CustomModelMetaclass rejects unique=True on fields."""

    def test_unique_true_on_field_raises(self) -> None:
        """unique=True on a field should raise ValueError."""
        with pytest.raises(ValueError, match="unique=True.*UniqueConstraint"):
            type(
                "UniqueFieldModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "UniqueFieldModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "email": models.TextField(unique=True),
                },
            )

    def test_error_message_suggests_unique_constraint(self) -> None:
        """The error message should include a UniqueConstraint example."""
        with pytest.raises(ValueError, match=r"UniqueConstraint\(fields=\['code'\]"):
            type(
                "UniqueFieldModel2",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "UniqueFieldModel2",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "code": models.CharField(max_length=50, unique=True),
                },
            )

    def test_unsupported_constraint_type_raises(self) -> None:
        """Non-UniqueConstraint constraints should raise ValueError."""
        with pytest.raises(ValueError, match="Only UniqueConstraint is supported"):
            type(
                "CheckConstraintModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "CheckConstraintModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "constraints": [
                                models.CheckConstraint(
                                    condition=models.Q(age__gte=0), name="ck_age_positive"
                                ),
                            ],
                        },
                    ),
                    "age": models.IntegerField(),
                },
            )

    def test_unique_constraint_in_indexes_raises(self) -> None:
        """UniqueConstraint in Meta.indexes should raise ValueError."""
        with pytest.raises(ValueError, match="Move it to Meta.constraints"):
            type(
                "MisplacedConstraintModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "MisplacedConstraintModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "indexes": [
                                models.UniqueConstraint(fields=["name"], name="uq_name"),
                            ],
                        },
                    ),
                    "name": models.TextField(),
                },
            )

    def test_descending_field_in_unique_constraint_raises(self) -> None:
        """Descending order in UniqueConstraint fields should raise ValueError."""
        with pytest.raises(ValueError, match="Sort order has no effect on uniqueness"):
            type(
                "DescUniqueModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "DescUniqueModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "constraints": [
                                models.UniqueConstraint(fields=["-name"], name="uq_name_desc"),
                            ],
                        },
                    ),
                    "name": models.TextField(),
                },
            )

    def test_unique_constraint_is_allowed(self) -> None:
        """UniqueConstraint in Meta.constraints should be accepted."""
        assert hasattr(SingleColumnUniqueModel, "_meta")
        constraints = SingleColumnUniqueModel._meta.constraints
        assert len(constraints) == 1
        assert constraints[0].name == "uq_email"


# ===========================================================================
# Tests for duplicate index detection
# ===========================================================================


class TestCustomModelMetaclassDuplicateIndexDetection:
    """Tests that CustomModelMetaclass rejects explicit indexes or constraints
    that duplicate auto-indexed FK/OneToOne columns.
    """

    def test_explicit_index_on_fk_column_raises(self) -> None:
        """An explicit index on a FK column (using column name) should raise."""
        with pytest.raises(ValueError, match="indexed automatically.*remove the duplicate"):
            type(
                "DuplicateFKIndexModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "DuplicateFKIndexModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "indexes": [
                                models.Index(fields=["parent_id"], name="idx_parent"),
                            ],
                        },
                    ),
                    "parent": models.ForeignKey(
                        ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                    ),
                },
            )

    def test_explicit_index_on_fk_field_name_raises(self) -> None:
        """An explicit index using the field name (not column name) should raise."""
        with pytest.raises(ValueError, match="indexed automatically.*remove the duplicate"):
            type(
                "DuplicateFKFieldNameIndexModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "DuplicateFKFieldNameIndexModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "indexes": [
                                models.Index(fields=["parent"], name="idx_parent"),
                            ],
                        },
                    ),
                    "parent": models.ForeignKey(
                        ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                    ),
                },
            )

    def test_explicit_unique_constraint_on_one_to_one_raises(self) -> None:
        """A UniqueConstraint on a OneToOneField column should raise."""
        with pytest.raises(ValueError, match="already have a unique index.*remove the duplicate"):
            type(
                "DuplicateO2OConstraintModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "DuplicateO2OConstraintModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "constraints": [
                                models.UniqueConstraint(fields=["parent_id"], name="uq_parent"),
                            ],
                        },
                    ),
                    "parent": models.OneToOneField(
                        ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                    ),
                },
            )

    def test_multi_column_index_including_fk_is_allowed(self) -> None:
        """A multi-column index that includes a FK column should be accepted."""
        Model = type(
            "MultiColWithFKModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "MultiColWithFKModel",
                "Meta": type(
                    "Meta",
                    (),
                    {
                        "app_label": "some_plugin",
                        "indexes": [
                            models.Index(fields=["parent_id", "name"], name="idx_parent_name"),
                        ],
                    },
                ),
                "parent": models.ForeignKey(
                    ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                ),
                "name": models.TextField(),
            },
        )
        index_names = [idx.name for idx in Model._meta.indexes]  # type: ignore[attr-defined]
        assert "idx_parent_name" in index_names

    def test_multi_column_unique_constraint_including_fk_is_allowed(self) -> None:
        """A multi-column UniqueConstraint that includes a FK column should be accepted."""
        Model = type(
            "MultiColUniqueWithFKModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "MultiColUniqueWithFKModel",
                "Meta": type(
                    "Meta",
                    (),
                    {
                        "app_label": "some_plugin",
                        "constraints": [
                            models.UniqueConstraint(
                                fields=["parent_id", "slug"], name="uq_parent_slug"
                            ),
                        ],
                    },
                ),
                "parent": models.ForeignKey(
                    ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                ),
                "slug": models.TextField(),
            },
        )
        constraint_names = [c.name for c in Model._meta.constraints]  # type: ignore[attr-defined]
        assert "uq_parent_slug" in constraint_names

    def test_index_on_non_fk_column_is_allowed(self) -> None:
        """An index on a non-FK column should be accepted."""
        Model = type(
            "RegularIndexModel",
            (CustomModel,),
            {
                "__module__": "some_plugin.models",
                "__qualname__": "RegularIndexModel",
                "Meta": type(
                    "Meta",
                    (),
                    {
                        "app_label": "some_plugin",
                        "indexes": [
                            models.Index(fields=["email"], name="idx_email"),
                        ],
                    },
                ),
                "email": models.TextField(),
            },
        )
        index_names = [idx.name for idx in Model._meta.indexes]  # type: ignore[attr-defined]
        assert "idx_email" in index_names

    def test_descending_index_on_fk_column_raises(self) -> None:
        """A descending index on a FK column should also be caught."""
        with pytest.raises(ValueError, match="indexed automatically.*remove the duplicate"):
            type(
                "DescFKIndexModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "DescFKIndexModel",
                    "Meta": type(
                        "Meta",
                        (),
                        {
                            "app_label": "some_plugin",
                            "indexes": [
                                models.Index(fields=["-parent_id"], name="idx_parent_desc"),
                            ],
                        },
                    ),
                    "parent": models.ForeignKey(
                        ParentModel, on_delete=models.DO_NOTHING, related_name="+"
                    ),
                },
            )


# ===========================================================================
# Tests for generate_constraint_sql
# ===========================================================================


class TestGenerateConstraintSqlPostgres:
    """Tests for PostgreSQL unique constraint SQL generation."""

    def test_single_column_unique(self) -> None:
        """Single column UniqueConstraint should generate UNIQUE INDEX."""
        constraint = models.UniqueConstraint(fields=["email"], name="uq_email")
        sql = generate_constraint_sql("test_plugin", "my_table", constraint, is_sqlite=False)
        assert (
            sql
            == "CREATE UNIQUE INDEX IF NOT EXISTS test_plugin_uq_email ON test_plugin.my_table (email);"
        )

    def test_multi_column_unique(self) -> None:
        """Multi-column UniqueConstraint should list all columns."""
        constraint = models.UniqueConstraint(fields=["tenant_id", "slug"], name="uq_tenant_slug")
        sql = generate_constraint_sql("test_plugin", "my_table", constraint, is_sqlite=False)
        assert (
            sql
            == "CREATE UNIQUE INDEX IF NOT EXISTS test_plugin_uq_tenant_slug ON test_plugin.my_table (tenant_id, slug);"
        )


class TestGenerateConstraintSqlSqlite:
    """Tests for SQLite unique constraint SQL generation."""

    def test_single_column_unique_no_schema(self) -> None:
        """SQLite should not use schema prefix."""
        constraint = models.UniqueConstraint(fields=["email"], name="uq_email")
        sql = generate_constraint_sql("test_plugin", "my_table", constraint, is_sqlite=True)
        assert sql == "CREATE UNIQUE INDEX IF NOT EXISTS test_plugin_uq_email ON my_table (email);"

    def test_multi_column_unique_no_schema(self) -> None:
        """SQLite multi-column should not use schema prefix."""
        constraint = models.UniqueConstraint(fields=["tenant_id", "slug"], name="uq_tenant_slug")
        sql = generate_constraint_sql("test_plugin", "my_table", constraint, is_sqlite=True)
        assert (
            sql
            == "CREATE UNIQUE INDEX IF NOT EXISTS test_plugin_uq_tenant_slug ON my_table (tenant_id, slug);"
        )


# ===========================================================================
# Tests for UniqueConstraint in generate_create_table_sql
# ===========================================================================


class TestCreateTableSqlWithUniqueConstraints:
    """Tests that generate_create_table_sql includes unique constraints."""

    def test_single_column_unique_in_create_table(self) -> None:
        """CREATE TABLE output should include UNIQUE INDEX for UniqueConstraint."""
        sql = generate_create_table_sql("test_plugin", SingleColumnUniqueModel)
        assert "CREATE UNIQUE INDEX IF NOT EXISTS" in sql
        assert "uq_email" in sql
        assert "email" in sql

    def test_multi_column_unique_in_create_table(self) -> None:
        """CREATE TABLE output should include multi-column UNIQUE INDEX."""
        sql = generate_create_table_sql("test_plugin", MultiColumnUniqueModel)
        assert "CREATE UNIQUE INDEX IF NOT EXISTS" in sql
        assert "uq_tenant_slug" in sql
        assert "tenant_id, slug" in sql

    def test_multiple_unique_constraints_in_create_table(self) -> None:
        """Multiple UniqueConstraints should all appear in output."""
        sql = generate_create_table_sql("test_plugin", MultipleUniqueConstraintsModel)
        assert sql.count("CREATE UNIQUE INDEX IF NOT EXISTS") == 2
        assert "uq_code" in sql
        assert "uq_cat_name" in sql

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_postgres_unique_constraint_has_schema_prefix(self) -> None:
        """PostgreSQL UNIQUE INDEX should use schema-qualified table name."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", SingleColumnUniqueModel)
        assert "ON test_plugin.singlecolumnuniquemodel" in sql

    def test_one_to_one_field_generates_unique_index(self) -> None:
        """OneToOneField should automatically get a UNIQUE INDEX on its column."""
        sql = generate_create_table_sql("test_plugin", ChildWithOneToOne)
        assert "CREATE UNIQUE INDEX IF NOT EXISTS" in sql
        assert "uq_parent_id" in sql

    def test_foreign_key_does_not_generate_unique_index(self) -> None:
        """ForeignKey should NOT get a UNIQUE INDEX (only a regular index)."""
        sql = generate_create_table_sql("test_plugin", ChildWithForeignKey)
        assert "CREATE UNIQUE INDEX" not in sql

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_one_to_one_unique_index_has_schema_prefix_postgres(self) -> None:
        """PostgreSQL OneToOneField UNIQUE INDEX should use schema-qualified table name."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", ChildWithOneToOne)
        assert (
            "CREATE UNIQUE INDEX IF NOT EXISTS test_plugin_uq_parent_id ON test_plugin.childwithonetoone (parent_id);"
            in sql
        )

    def test_one_to_one_pk_does_not_generate_unique_index(self) -> None:
        """OneToOneField with primary_key=True should NOT get a separate UNIQUE INDEX."""
        sql = generate_create_table_sql("test_plugin", OneToOnePKModel)
        assert "CREATE UNIQUE INDEX" not in sql


# ===========================================================================
# Tests for OneToOneField(primary_key=True) support
# ===========================================================================


class TestOneToOnePrimaryKey:
    """Tests that CustomModelMetaclass supports OneToOneField(primary_key=True)."""

    def test_dbid_is_suppressed(self) -> None:
        """The inherited dbid field should not exist when another field is the PK."""
        field_names = [f.name for f in OneToOnePKModel._meta.local_fields]
        assert "dbid" not in field_names

    def test_one_to_one_is_primary_key(self) -> None:
        """The OneToOneField should be the model's primary key."""
        assert OneToOnePKModel._meta.pk is not None
        assert OneToOnePKModel._meta.pk.name == "parent"

    def test_no_auto_index_on_pk_field(self) -> None:
        """PK fields should not get a redundant auto-generated index."""
        index_field_lists = [idx.fields for idx in OneToOnePKModel._meta.indexes]
        assert not any("parent_id" in fields for fields in index_field_lists)

    def test_sql_has_pk_column(self) -> None:
        """Generated SQL should include the FK column as PRIMARY KEY."""
        sql = generate_create_table_sql("test_plugin", OneToOnePKModel)
        assert "parent_id" in sql
        assert "PRIMARY KEY" in sql

    def test_sql_has_no_dbid(self) -> None:
        """Generated SQL should not include a dbid column."""
        sql = generate_create_table_sql("test_plugin", OneToOnePKModel)
        assert "dbid" not in sql

    def test_sql_no_autoincrement(self) -> None:
        """PK should not have AUTOINCREMENT/IDENTITY since it's a FK, not an AutoField."""
        sql = generate_create_table_sql("test_plugin", OneToOnePKModel)
        assert "AUTOINCREMENT" not in sql
        assert "IDENTITY" not in sql

    @patch("plugin_runner.ddl.IS_SQLITE", False)
    def test_postgres_sql_structure(self) -> None:
        """PostgreSQL SQL should have FK column as PK with no IDENTITY suffix."""
        from plugin_runner.ddl import generate_create_table_sql

        sql = generate_create_table_sql("test_plugin", OneToOnePKModel)
        assert "parent_id bigint PRIMARY KEY" in sql
        assert "dbid" not in sql
        assert "IDENTITY" not in sql

    def test_foreign_key_primary_key_raises(self) -> None:
        """ForeignKey(primary_key=True) should raise ValueError."""
        with pytest.raises(ValueError, match="Use a OneToOneField instead"):
            type(
                "FKPKModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "FKPKModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "parent": models.ForeignKey(
                        ParentModel, on_delete=models.DO_NOTHING, primary_key=True
                    ),
                },
            )

    def test_regular_field_primary_key_raises(self) -> None:
        """primary_key=True on a non-relationship field should raise ValueError."""
        with pytest.raises(ValueError, match="auto-generated primary key"):
            type(
                "CustomPKModel",
                (CustomModel,),
                {
                    "__module__": "some_plugin.models",
                    "__qualname__": "CustomPKModel",
                    "Meta": type("Meta", (), {"app_label": "some_plugin"}),
                    "custom_id": models.IntegerField(primary_key=True),
                },
            )
