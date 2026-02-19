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
from django.db import models

from canvas_sdk.v1.data.base import CustomModel
from plugin_runner.installation import (
    SQL_STATEMENT_DELIMITER,
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
    """A model with multiple foreign keys."""

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
# Tests for generate_field_sql - PostgreSQL
# ===========================================================================


class TestGenerateFieldSqlPostgres:
    """Tests for PostgreSQL field SQL generation."""

    def test_bigautofield_primary_key(self) -> None:
        """BigAutoField with primary_key should generate SERIAL PRIMARY KEY."""
        field: models.Field = models.BigAutoField(primary_key=True)
        assert generate_field_sql(field, is_sqlite=False) == "SERIAL PRIMARY KEY"

    def test_charfield(self) -> None:
        """CharField should generate TEXT for PostgreSQL."""
        field: models.Field = models.CharField(max_length=100)
        assert generate_field_sql(field, is_sqlite=False) == "TEXT"

    def test_textfield(self) -> None:
        """TextField should generate TEXT for PostgreSQL."""
        field: models.Field = models.TextField()
        assert generate_field_sql(field, is_sqlite=False) == "TEXT"

    def test_integerfield(self) -> None:
        """IntegerField should generate INTEGER for PostgreSQL."""
        field: models.Field = models.IntegerField()
        assert generate_field_sql(field, is_sqlite=False) == "INTEGER"

    def test_datefield(self) -> None:
        """DateField should generate DATE for PostgreSQL."""
        field: models.Field = models.DateField()
        assert generate_field_sql(field, is_sqlite=False) == "DATE"

    def test_datetimefield(self) -> None:
        """DateTimeField should generate TIMESTAMP WITH TIME ZONE for PostgreSQL."""
        field: models.Field = models.DateTimeField()
        assert generate_field_sql(field, is_sqlite=False) == "TIMESTAMP WITH TIME ZONE"

    def test_booleanfield(self) -> None:
        """BooleanField should generate BOOLEAN for PostgreSQL."""
        field: models.Field = models.BooleanField()
        assert generate_field_sql(field, is_sqlite=False) == "BOOLEAN"

    def test_foreignkey(self) -> None:
        """ForeignKey should generate INTEGER for PostgreSQL."""
        field: models.Field = models.ForeignKey(ParentModel, on_delete=models.DO_NOTHING)
        assert generate_field_sql(field, is_sqlite=False) == "INTEGER"

    def test_onetoonefield(self) -> None:
        """OneToOneField should generate INTEGER for PostgreSQL."""
        field: models.Field = models.OneToOneField(ParentModel, on_delete=models.DO_NOTHING)
        assert generate_field_sql(field, is_sqlite=False) == "INTEGER"

    def test_decimalfield_with_precision(self) -> None:
        """DecimalField with explicit precision should generate NUMERIC(m,d)."""
        field: models.Field = models.DecimalField(max_digits=10, decimal_places=2)
        assert generate_field_sql(field, is_sqlite=False) == "NUMERIC(10,2)"

    def test_decimalfield_default_precision(self) -> None:
        """DecimalField without precision should default to NUMERIC(20,10)."""
        field: models.Field = models.DecimalField()
        assert generate_field_sql(field, is_sqlite=False) == "NUMERIC(20,10)"

    def test_decimalfield_custom_large_precision(self) -> None:
        """DecimalField with large precision should generate matching NUMERIC."""
        field: models.Field = models.DecimalField(max_digits=30, decimal_places=15)
        assert generate_field_sql(field, is_sqlite=False) == "NUMERIC(30,15)"

    def test_jsonfield(self) -> None:
        """JSONField should generate JSONB for PostgreSQL."""
        field: models.Field = models.JSONField()
        assert generate_field_sql(field, is_sqlite=False) == "JSONB"


# ===========================================================================
# Tests for generate_field_sql - SQLite
# ===========================================================================


class TestGenerateFieldSqlSqlite:
    """Tests for SQLite field SQL generation."""

    def test_bigautofield_primary_key(self) -> None:
        """BigAutoField with primary_key should generate INTEGER PRIMARY KEY AUTOINCREMENT."""
        field: models.Field = models.BigAutoField(primary_key=True)
        assert generate_field_sql(field, is_sqlite=True) == "INTEGER PRIMARY KEY AUTOINCREMENT"

    def test_charfield(self) -> None:
        """CharField should generate TEXT for SQLite."""
        field: models.Field = models.CharField(max_length=100)
        assert generate_field_sql(field, is_sqlite=True) == "TEXT"

    def test_textfield(self) -> None:
        """TextField should generate TEXT for SQLite."""
        field: models.Field = models.TextField()
        assert generate_field_sql(field, is_sqlite=True) == "TEXT"

    def test_integerfield(self) -> None:
        """IntegerField should generate INTEGER for SQLite."""
        field: models.Field = models.IntegerField()
        assert generate_field_sql(field, is_sqlite=True) == "INTEGER"

    def test_datefield(self) -> None:
        """DateField should generate TEXT for SQLite."""
        field: models.Field = models.DateField()
        assert generate_field_sql(field, is_sqlite=True) == "TEXT"

    def test_datetimefield(self) -> None:
        """DateTimeField should generate TEXT for SQLite."""
        field: models.Field = models.DateTimeField()
        assert generate_field_sql(field, is_sqlite=True) == "TEXT"

    def test_booleanfield(self) -> None:
        """BooleanField should generate INTEGER for SQLite."""
        field: models.Field = models.BooleanField()
        assert generate_field_sql(field, is_sqlite=True) == "INTEGER"

    def test_foreignkey(self) -> None:
        """ForeignKey should generate INTEGER for SQLite."""
        field: models.Field = models.ForeignKey(ParentModel, on_delete=models.DO_NOTHING)
        assert generate_field_sql(field, is_sqlite=True) == "INTEGER"

    def test_onetoonefield(self) -> None:
        """OneToOneField should generate INTEGER for SQLite."""
        field: models.Field = models.OneToOneField(ParentModel, on_delete=models.DO_NOTHING)
        assert generate_field_sql(field, is_sqlite=True) == "INTEGER"

    def test_decimalfield(self) -> None:
        """DecimalField should generate REAL for SQLite."""
        field: models.Field = models.DecimalField(max_digits=10, decimal_places=2)
        assert generate_field_sql(field, is_sqlite=True) == "REAL"

    def test_jsonfield(self) -> None:
        """JSONField should generate TEXT for SQLite."""
        field: models.Field = models.JSONField()
        assert generate_field_sql(field, is_sqlite=True) == "TEXT"


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
        assert "dbid INTEGER PRIMARY KEY AUTOINCREMENT" in create_stmt
        assert "text_field TEXT" in create_stmt
        assert "char_field TEXT" in create_stmt
        assert "int_field INTEGER" in create_stmt
        assert "bool_field INTEGER" in create_stmt
        assert "date_field TEXT" in create_stmt
        assert "datetime_field TEXT" in create_stmt
        assert "decimal_field REAL" in create_stmt
        assert "json_field TEXT" in create_stmt

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

    These tests mock the Django settings to simulate a PostgreSQL environment.
    """

    @pytest.fixture
    def postgres_settings(self) -> MagicMock:
        """Create a mock settings object for PostgreSQL."""
        mock_settings = MagicMock()
        mock_settings.DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql"}}
        return mock_settings

    def test_postgres_uses_schema_prefix(self, postgres_settings: MagicMock) -> None:
        """PostgreSQL should use schema prefix in table names."""
        with patch.dict("sys.modules", {"django.conf": MagicMock(settings=postgres_settings)}):
            # Re-import to get the patched version
            import importlib

            import plugin_runner.installation as installation

            importlib.reload(installation)

            sql = installation.generate_create_table_sql("test_plugin", AllDataTypesModel)

            assert "test_plugin.alldatatypesmodel" in sql

            # Restore original module
            importlib.reload(installation)

    def test_postgres_uses_alter_table_for_columns(self, postgres_settings: MagicMock) -> None:
        """PostgreSQL should use ALTER TABLE for adding columns."""
        with patch.dict("sys.modules", {"django.conf": MagicMock(settings=postgres_settings)}):
            import importlib

            import plugin_runner.installation as installation

            importlib.reload(installation)

            sql = installation.generate_create_table_sql("test_plugin", AllDataTypesModel)

            # Should have ALTER TABLE statements
            assert "ALTER TABLE" in sql
            assert "ADD COLUMN IF NOT EXISTS" in sql

            importlib.reload(installation)

    def test_postgres_gin_index(self, postgres_settings: MagicMock) -> None:
        """PostgreSQL should use USING GIN for GIN indexes."""
        with patch.dict("sys.modules", {"django.conf": MagicMock(settings=postgres_settings)}):
            import importlib

            import plugin_runner.installation as installation

            importlib.reload(installation)

            sql = installation.generate_create_table_sql("test_plugin", GinIndexModel)

            assert "USING GIN(metadata)" in sql

            importlib.reload(installation)


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
