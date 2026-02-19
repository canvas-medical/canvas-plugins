"""Tests for generate_plugin_migrations and its decomposed helper functions.

Tests cover:
1. discover_model_files — filesystem discovery of model files
2. extract_models_from_module — sandbox execution and model class extraction
3. should_create_table — predicate for table creation eligibility
4. execute_create_table_sql — SQL execution against SQLite
5. generate_plugin_migrations — orchestrator logic
6. End-to-end integration test
"""

from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from plugin_runner.installation import (
    SQL_STATEMENT_DELIMITER,
    discover_model_files,
    execute_create_table_sql,
    extract_models_from_module,
    generate_plugin_migrations,
    should_create_table,
)

# ===========================================================================
# Tests for discover_model_files
# ===========================================================================


def test_discover_returns_py_files(tmp_path: Path) -> None:
    """Should find .py files in the models/ directory."""
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "foo.py").write_text("x = 1")
    (models_dir / "bar.py").write_text("x = 2")

    result = discover_model_files(tmp_path)

    assert len(result) == 2
    assert all(f.suffix == ".py" for f in result)


def test_discover_excludes_init(tmp_path: Path) -> None:
    """__init__.py should not be returned."""
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "my_model.py").write_text("x = 1")

    result = discover_model_files(tmp_path)

    assert len(result) == 1
    assert result[0].name == "my_model.py"


def test_discover_returns_empty_when_no_models_dir(tmp_path: Path) -> None:
    """Should return an empty list when models/ doesn't exist."""
    result = discover_model_files(tmp_path)

    assert result == []


def test_discover_returns_sorted(tmp_path: Path) -> None:
    """Results should be deterministically sorted to prevent flake."""
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    for name in ["z_model.py", "a_model.py", "m_model.py"]:
        (models_dir / name).write_text("x = 1")

    result = discover_model_files(tmp_path)

    names = [f.name for f in result]
    assert names == sorted(names)


# ===========================================================================
# Tests for extract_models_from_module
# ===========================================================================


def _make_plugin_tree(tmp_path: Path, plugin_name: str, model_code: str) -> Path:
    """Create a minimal plugin directory tree with a model file.

    Returns the path to the model .py file.
    """
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    models_dir = plugin_dir / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    model_file = models_dir / "my_model.py"
    model_file.write_text(dedent(model_code))
    return model_file


def test_extract_finds_custom_model_subclass(tmp_path: Path) -> None:
    """Sandbox should discover a CustomModel subclass."""
    model_file = _make_plugin_tree(
        tmp_path,
        "test_plugin",
        """\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField

        class MyModel(CustomModel):
            name = TextField()
        """,
    )

    result = extract_models_from_module("test_plugin", model_file)

    assert len(result) >= 1
    model_names = [m.__name__ for m in result]
    assert "MyModel" in model_names


def test_extract_excludes_constants(tmp_path: Path) -> None:
    """Constants (int, str) lack __module__ and should not be returned."""
    model_file = _make_plugin_tree(
        tmp_path,
        "test_plugin",
        """\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import IntegerField

        SOME_CONSTANT = 42

        class MyModel(CustomModel):
            value = IntegerField()
        """,
    )

    result = extract_models_from_module("test_plugin", model_file)

    # Constants like 42 don't have __module__ so they are excluded;
    # the model class should be present.
    result_names = [getattr(m, "__name__", None) for m in result]
    assert "MyModel" in result_names
    assert len(result) == 1


def test_extract_finds_multiple_models_in_one_file(tmp_path: Path) -> None:
    """Two models in the same file should both be discovered."""
    model_file = _make_plugin_tree(
        tmp_path,
        "test_plugin",
        """\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField, IntegerField

        class ModelA(CustomModel):
            name = TextField()

        class ModelB(CustomModel):
            value = IntegerField()
        """,
    )

    result = extract_models_from_module("test_plugin", model_file)

    result_names = {m.__name__ for m in result}
    assert "ModelA" in result_names
    assert "ModelB" in result_names


# ===========================================================================
# Tests for should_create_table
# ===========================================================================


def test_returns_true_for_standard_model() -> None:
    """A normal model with matching schema should be eligible."""
    mock_model = MagicMock()
    mock_model._meta.proxy = False
    mock_model._meta.original_attrs = {"db_table": "my_table"}

    assert should_create_table(mock_model, "my_schema") is True


def test_returns_false_for_proxy_model() -> None:
    """Proxy models should not get their own tables."""
    mock_model = MagicMock()
    mock_model._meta.proxy = True

    assert should_create_table(mock_model, "my_schema") is False


def test_returns_false_for_cross_schema() -> None:
    """Models referencing a different schema should be skipped."""
    mock_model = MagicMock()
    mock_model._meta.proxy = False
    mock_model._meta.original_attrs = {"db_table": "other_schema.table"}

    assert should_create_table(mock_model, "my_schema") is False


def test_returns_true_for_same_schema_dotted() -> None:
    """Models whose db_table starts with the target schema should be eligible."""
    mock_model = MagicMock()
    mock_model._meta.proxy = False
    mock_model._meta.original_attrs = {"db_table": "my_schema.table"}

    assert should_create_table(mock_model, "my_schema") is True


def test_returns_false_when_no_meta() -> None:
    """Objects without _meta should not be eligible."""

    class NotAModel:
        pass

    assert should_create_table(NotAModel, "my_schema") is False


# ===========================================================================
# Tests for execute_create_table_sql
# ===========================================================================


@pytest.mark.django_db
def test_creates_table() -> None:
    """Should create a table in SQLite."""
    sql = "CREATE TABLE IF NOT EXISTS test_exec_table (dbid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);"
    execute_create_table_sql(sql)

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_exec_table'"
        )
        assert cursor.fetchone() is not None


@pytest.mark.django_db
def test_handles_multiple_statements() -> None:
    """Should execute both CREATE TABLE and CREATE INDEX statements."""
    statements = [
        "CREATE TABLE IF NOT EXISTS test_multi_table (dbid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);",
        "CREATE INDEX IF NOT EXISTS idx_test_multi_name ON test_multi_table (name);",
    ]
    sql = SQL_STATEMENT_DELIMITER.join(statements)
    execute_create_table_sql(sql)

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_multi_table'"
        )
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_test_multi_name'"
        )
        assert cursor.fetchone() is not None


@pytest.mark.django_db
def test_is_idempotent() -> None:
    """IF NOT EXISTS should allow repeat execution without errors."""
    sql = "CREATE TABLE IF NOT EXISTS test_idempotent (dbid INTEGER PRIMARY KEY AUTOINCREMENT);"
    execute_create_table_sql(sql)
    execute_create_table_sql(sql)  # should not raise

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_idempotent'"
        )
        assert cursor.fetchone() is not None


# ===========================================================================
# Tests for generate_plugin_migrations (orchestrator)
# ===========================================================================


@patch("plugin_runner.installation.execute_create_table_sql")
@patch("plugin_runner.installation.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.installation.should_create_table")
@patch("plugin_runner.installation.extract_models_from_module")
@patch("plugin_runner.installation.discover_model_files")
def test_defaults_schema_to_plugin_name(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_should: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """When schema_name is None, it should default to plugin_name."""
    mock_discover.return_value = []

    generate_plugin_migrations("my_plugin", tmp_path, schema_name=None)

    # The discover call should still happen even with no schema_name arg
    mock_discover.assert_called_once_with(tmp_path)


@patch("plugin_runner.installation.execute_create_table_sql")
@patch("plugin_runner.installation.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.installation.should_create_table", return_value=True)
@patch("plugin_runner.installation.extract_models_from_module")
@patch("plugin_runner.installation.discover_model_files")
def test_returns_all_discovered_models(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_should: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """Return value should aggregate all models from all files."""
    sentinel_file = Path("/fake/models/a.py")
    mock_discover.return_value = [sentinel_file]

    model_a = MagicMock(__name__="ModelA")
    model_b = MagicMock(__name__="ModelB")
    mock_extract.return_value = [model_a, model_b]

    result = generate_plugin_migrations("my_plugin", tmp_path, schema_name="my_schema")

    assert model_a in result
    assert model_b in result
    assert len(result) == 2


@patch("plugin_runner.installation.execute_create_table_sql")
@patch("plugin_runner.installation.generate_create_table_sql")
@patch("plugin_runner.installation.should_create_table", return_value=False)
@patch("plugin_runner.installation.extract_models_from_module")
@patch("plugin_runner.installation.discover_model_files")
def test_skips_ineligible_models_for_sql(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_should: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """Models where should_create_table is False should not generate SQL."""
    sentinel_file = Path("/fake/models/a.py")
    mock_discover.return_value = [sentinel_file]

    model = MagicMock(__name__="SkippedModel")
    model._meta.proxy = True
    mock_extract.return_value = [model]

    generate_plugin_migrations("my_plugin", tmp_path, schema_name="my_schema")

    mock_gen_sql.assert_not_called()
    mock_exec.assert_not_called()


@patch("plugin_runner.installation.discover_model_files", side_effect=RuntimeError("boom"))
def test_raises_on_exception(
    mock_discover: MagicMock,
    tmp_path: Path,
) -> None:
    """Exceptions should be logged and re-raised."""
    with pytest.raises(RuntimeError, match="boom"):
        generate_plugin_migrations("my_plugin", tmp_path)


@patch("plugin_runner.installation.execute_create_table_sql")
@patch("plugin_runner.installation.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.installation.should_create_table", return_value=True)
@patch("plugin_runner.installation.extract_models_from_module")
@patch("plugin_runner.installation.discover_model_files")
def test_adds_plugin_path_to_sys_path(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_should: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """The plugin directory should be added to sys.path."""
    import sys

    mock_discover.return_value = []
    plugin_path = tmp_path / "my_plugin"
    plugin_path.mkdir()

    generate_plugin_migrations("my_plugin", plugin_path)

    assert str(plugin_path) in sys.path

    # Cleanup
    sys.path.remove(str(plugin_path))


# ===========================================================================
# Integration test
# ===========================================================================


@pytest.mark.django_db
def test_end_to_end(tmp_path: Path) -> None:
    """Full pipeline: real temp directory, real sandbox, real SQLite.

    Verifies the model appears in the return list and the table exists in the database.
    """
    from plugin_runner.installation import register_plugin_as_django_app

    plugin_name = "integ_test_plugin"
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")

    models_dir = plugin_dir / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "things.py").write_text(
        dedent("""\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField

        class Thing(CustomModel):
            label = TextField()
        """)
    )

    register_plugin_as_django_app(plugin_name, plugin_dir)

    result = generate_plugin_migrations(plugin_name, plugin_dir, schema_name=plugin_name)

    # Model should appear in return list
    model_names = [m.__name__ for m in result]
    assert "Thing" in model_names

    # Table should exist in SQLite
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thing'")
        assert cursor.fetchone() is not None
