"""Tests for generate_plugin_migrations and its decomposed helper functions.

Tests cover:
1. discover_model_files — filesystem discovery of model files
2. extract_models_from_module — sandbox execution and model class extraction
3. should_create_table — predicate for table creation eligibility
4. execute_create_table_sql — SQL execution against SQLite
5. generate_plugin_migrations — orchestrator logic
6. End-to-end integration test
7. is_schema_manager — DDL gating based on Aptible environment
8. wait_for_namespace — non-schema-manager containers wait for namespace readiness
9. register_plugin_app_config — AppConfig registration for plugin models
"""

import os
from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from plugin_runner.ddl import (
    SQL_STATEMENT_DELIMITER,
    discover_model_files,
    execute_create_table_sql,
    extract_models_from_module,
    generate_plugin_migrations,
    should_create_table,
)
from plugin_runner.installation import (
    clear_registered_models,
    register_plugin_app_config,
)
from plugin_runner.namespace import (
    is_schema_manager,
    wait_for_namespace,
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


def test_discover_includes_init(tmp_path: Path) -> None:
    """__init__.py should be returned alongside other model files."""
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "my_model.py").write_text("x = 1")

    result = discover_model_files(tmp_path)

    names = [f.name for f in result]
    assert len(result) == 2
    assert "__init__.py" in names
    assert "my_model.py" in names


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


def test_returns_false_for_overlapping_schema_prefix() -> None:
    """A table in schema 'acme__data_extra' must not match schema 'acme__data'."""
    mock_model = MagicMock()
    mock_model._meta.proxy = False
    mock_model._meta.original_attrs = {"db_table": "acme__data_extra.table"}

    assert should_create_table(mock_model, "acme__data") is False


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


@patch("plugin_runner.ddl.execute_create_table_sql")
@patch("plugin_runner.ddl.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.ddl.should_create_table")
@patch("plugin_runner.ddl.extract_models_from_module")
@patch("plugin_runner.ddl.discover_model_files")
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


@patch("plugin_runner.ddl.execute_create_table_sql")
@patch("plugin_runner.ddl.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.ddl.should_create_table", return_value=True)
@patch("plugin_runner.ddl.extract_models_from_module")
@patch("plugin_runner.ddl.discover_model_files")
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


@patch("plugin_runner.ddl.execute_create_table_sql")
@patch("plugin_runner.ddl.generate_create_table_sql")
@patch("plugin_runner.ddl.should_create_table", return_value=False)
@patch("plugin_runner.ddl.extract_models_from_module")
@patch("plugin_runner.ddl.discover_model_files")
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


@patch("plugin_runner.ddl.discover_model_files", side_effect=RuntimeError("boom"))
def test_raises_on_exception(
    mock_discover: MagicMock,
    tmp_path: Path,
) -> None:
    """Exceptions should be logged and re-raised."""
    with pytest.raises(RuntimeError, match="boom"):
        generate_plugin_migrations("my_plugin", tmp_path)


@patch("plugin_runner.ddl.execute_create_table_sql")
@patch("plugin_runner.ddl.generate_create_table_sql", return_value="CREATE TABLE ...")
@patch("plugin_runner.ddl.should_create_table", return_value=True)
@patch("plugin_runner.ddl.extract_models_from_module")
@patch("plugin_runner.ddl.discover_model_files")
def test_adds_plugin_parent_to_sys_path(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_should: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """The plugin's parent directory should be added to sys.path."""
    import sys

    mock_discover.return_value = []
    plugin_path = tmp_path / "my_plugin"
    plugin_path.mkdir()

    generate_plugin_migrations("my_plugin", plugin_path)

    assert str(tmp_path) in sys.path

    # Cleanup
    sys.path.remove(str(tmp_path))


@patch("plugin_runner.ddl.execute_create_table_sql")
@patch("plugin_runner.ddl.generate_create_table_sql")
@patch("plugin_runner.ddl.extract_models_from_module")
@patch("plugin_runner.ddl.discover_model_files")
def test_raises_on_cross_schema_model(
    mock_discover: MagicMock,
    mock_extract: MagicMock,
    mock_gen_sql: MagicMock,
    mock_exec: MagicMock,
    tmp_path: Path,
) -> None:
    """A model whose db_table references another schema should abort installation."""
    sentinel_file = Path("/fake/models/a.py")
    mock_discover.return_value = [sentinel_file]

    model = MagicMock(__name__="CrossSchemaModel")
    model._meta.proxy = False
    model._meta.original_attrs = {"db_table": "other_schema.forbidden_table"}
    mock_extract.return_value = [model]

    with pytest.raises(RuntimeError, match="references a schema outside of"):
        generate_plugin_migrations("my_plugin", tmp_path, schema_name="my_schema")

    mock_gen_sql.assert_not_called()
    mock_exec.assert_not_called()


# ===========================================================================
# Integration test
# ===========================================================================


@pytest.mark.django_db
def test_end_to_end(tmp_path: Path) -> None:
    """Full pipeline: real temp directory, real sandbox, real SQLite.

    Verifies the model appears in the return list and the table exists in the database.
    """
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

    result = generate_plugin_migrations(plugin_name, plugin_dir, schema_name=plugin_name)

    # Model should appear in return list
    model_names = [m.__name__ for m in result]
    assert "Thing" in model_names

    # Table should exist in SQLite
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thing'")
        assert cursor.fetchone() is not None


# ===========================================================================
# Tests for clear_registered_models
# ===========================================================================


def test_clear_registered_models_removes_existing_entry() -> None:
    """Should remove a previously registered model from apps.all_models."""
    from django.apps import apps

    # Seed the registry with a fake model under a fake plugin name
    fake_plugin = "clear_test_plugin"
    apps.all_models[fake_plugin] = {"fakemodel": MagicMock()}

    clear_registered_models(fake_plugin)

    assert fake_plugin not in apps.all_models


def test_clear_registered_models_noop_when_absent() -> None:
    """Should not raise when the plugin has no registered models."""
    clear_registered_models("nonexistent_plugin_xyz")


@pytest.mark.django_db
def test_model_relocation_does_not_conflict(tmp_path: Path) -> None:
    """Moving a model between files should not raise a conflicting-models error.

    Simulates a plugin that first defines CustomNote in models/__init__.py,
    then relocates it to models/models.py on reinstallation.
    """
    plugin_name = "reloc_test_plugin"
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    models_dir = plugin_dir / "models"
    models_dir.mkdir()

    model_code = dedent("""\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField

        class CustomNote(CustomModel):
            body = TextField()
    """)

    # First installation: model lives in models/__init__.py
    (models_dir / "__init__.py").write_text(model_code)
    generate_plugin_migrations(plugin_name, plugin_dir, schema_name=plugin_name)

    # Second installation: model moves to models/models.py
    (models_dir / "__init__.py").write_text("")
    (models_dir / "models.py").write_text(model_code)

    # This should NOT raise RuntimeError("Conflicting 'customnote' models ...")
    result = generate_plugin_migrations(plugin_name, plugin_dir, schema_name=plugin_name)

    model_names = [m.__name__ for m in result]
    assert "CustomNote" in model_names


# ===========================================================================
# Tests for is_schema_manager
# ===========================================================================


def test_is_schema_manager_outside_aptible() -> None:
    """Without APTIBLE_PROCESS_TYPE, DDL is always allowed (local dev)."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("APTIBLE_PROCESS_TYPE", None)
        os.environ.pop("APTIBLE_PROCESS_INDEX", None)
        assert is_schema_manager() is True


def test_is_schema_manager_cmd_index_zero() -> None:
    """First cmd container should be the schema manager."""
    with patch.dict(os.environ, {"APTIBLE_PROCESS_TYPE": "cmd", "APTIBLE_PROCESS_INDEX": "0"}):
        assert is_schema_manager() is True


def test_is_schema_manager_cmd_index_default() -> None:
    """When APTIBLE_PROCESS_INDEX is absent, it defaults to '0'."""
    with patch.dict(os.environ, {"APTIBLE_PROCESS_TYPE": "cmd"}, clear=False):
        os.environ.pop("APTIBLE_PROCESS_INDEX", None)
        assert is_schema_manager() is True


def test_is_schema_manager_cmd_index_nonzero() -> None:
    """Non-primary cmd containers should not manage schemas."""
    with patch.dict(os.environ, {"APTIBLE_PROCESS_TYPE": "cmd", "APTIBLE_PROCESS_INDEX": "1"}):
        assert is_schema_manager() is False


def test_is_schema_manager_worker_index_zero() -> None:
    """Worker processes should never manage schemas, even at index 0."""
    with patch.dict(os.environ, {"APTIBLE_PROCESS_TYPE": "worker", "APTIBLE_PROCESS_INDEX": "0"}):
        assert is_schema_manager() is False


def test_is_schema_manager_worker_index_nonzero() -> None:
    """Worker processes should never manage schemas."""
    with patch.dict(os.environ, {"APTIBLE_PROCESS_TYPE": "worker", "APTIBLE_PROCESS_INDEX": "1"}):
        assert is_schema_manager() is False


# ===========================================================================
# Tests for wait_for_namespace
# ===========================================================================


@patch("plugin_runner.namespace.namespace_ready", return_value=True)
@patch("plugin_runner.namespace.open_database_connection")
def test_wait_for_namespace_returns_immediately_when_ready(
    mock_open_conn: MagicMock, mock_ready: MagicMock
) -> None:
    """Should return immediately when namespace is already ready (checked after LISTEN)."""
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_open_conn.return_value = mock_conn

    wait_for_namespace("org__data", plugin_name="my_plugin", models_hash="abc123", timeout=10)

    mock_conn.execute.assert_called_once_with("LISTEN ns_ready_org__data")
    mock_ready.assert_called_once_with("org__data", "my_plugin", "abc123")
    mock_conn.notifies.assert_not_called()


@patch("plugin_runner.namespace.namespace_ready", return_value=False)
@patch("plugin_runner.namespace.open_database_connection")
def test_wait_for_namespace_unblocks_on_notify(
    mock_open_conn: MagicMock, mock_ready: MagicMock
) -> None:
    """Should unblock when a matching NOTIFY with correct plugin_name:hash payload is received."""
    from psycopg import Notify

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.notifies.return_value = iter(
        [Notify(channel="ns_ready_org__data", payload="my_plugin:abc123", pid=0)]
    )
    mock_open_conn.return_value = mock_conn

    wait_for_namespace("org__data", plugin_name="my_plugin", models_hash="abc123", timeout=30)

    mock_conn.notifies.assert_called_once_with(timeout=30)


@patch("plugin_runner.namespace.namespace_ready", return_value=False)
@patch("plugin_runner.namespace.open_database_connection")
def test_wait_for_namespace_raises_on_timeout(
    mock_open_conn: MagicMock, mock_ready: MagicMock
) -> None:
    """Should raise PluginInstallationError when no NOTIFY arrives before timeout."""
    from plugin_runner.exceptions import PluginInstallationError

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    # Empty iterator — simulates timeout with no notifications
    mock_conn.notifies.return_value = iter([])
    mock_open_conn.return_value = mock_conn

    with pytest.raises(PluginInstallationError, match="Timed out after 4s"):
        wait_for_namespace("org__data", plugin_name="my_plugin", models_hash="abc123", timeout=4)


def test_namespace_notify_channel_short_name() -> None:
    """Short namespace should produce a plain prefixed channel name."""
    from plugin_runner.namespace import _namespace_notify_channel

    assert _namespace_notify_channel("org__data") == "ns_ready_org__data"


def test_namespace_notify_channel_long_name_uses_hash() -> None:
    """Namespace exceeding NAMEDATALEN should use a hashed channel name."""
    import hashlib

    from plugin_runner.namespace import PG_NAMEDATALEN, _namespace_notify_channel

    long_ns = "a" * (PG_NAMEDATALEN + 1)
    channel = _namespace_notify_channel(long_ns)

    assert len(channel) <= PG_NAMEDATALEN
    expected_hash = hashlib.sha256(long_ns.encode()).hexdigest()[:16]
    assert channel == f"ns_ready_{expected_hash}"


def test_namespace_notify_channel_deterministic() -> None:
    """Same namespace should always produce the same channel name."""
    from plugin_runner.namespace import _namespace_notify_channel

    long_ns = "organization__very_long_namespace_that_exceeds_the_limit_easily"
    assert _namespace_notify_channel(long_ns) == _namespace_notify_channel(long_ns)


# ===========================================================================
# Tests for register_plugin_app_config
# ===========================================================================


def test_register_creates_app_config() -> None:
    """Should create an AppConfig whose models dict is the same object as all_models."""
    from django.apps import apps

    plugin = "reg_test_plugin"
    apps.all_models[plugin] = {"fakemodel": MagicMock()}
    try:
        register_plugin_app_config(plugin)

        assert plugin in apps.app_configs
        assert apps.app_configs[plugin].models is apps.all_models[plugin]
    finally:
        apps.all_models.pop(plugin, None)
        apps.app_configs.pop(plugin, None)
        apps.clear_cache()


def test_register_skips_when_no_models() -> None:
    """Should not create an AppConfig when the plugin has no models in all_models."""
    from django.apps import apps

    register_plugin_app_config("absent_plugin")

    assert "absent_plugin" not in apps.app_configs


def test_register_skips_when_already_registered() -> None:
    """Should not replace an existing AppConfig."""
    from django.apps import apps

    plugin = "already_reg"
    sentinel = object()
    apps.all_models[plugin] = {"fakemodel": MagicMock()}
    apps.app_configs[plugin] = sentinel  # type: ignore[assignment]
    try:
        register_plugin_app_config(plugin)

        assert apps.app_configs[plugin] is sentinel
    finally:
        apps.all_models.pop(plugin, None)
        apps.app_configs.pop(plugin, None)
        apps.clear_cache()


def test_register_app_config_models_visible_to_get_models() -> None:
    """Models in a registered plugin AppConfig should appear in apps.get_models()."""
    from django.apps import apps
    from django.db import models

    plugin = "vis_test"

    # Build a minimal concrete model class with proper Meta.
    model_cls = type(
        "VisTestModel",
        (models.Model,),
        {
            "__module__": f"{plugin}.models",
            "Meta": type("Meta", (), {"app_label": plugin}),
        },
    )

    apps.all_models[plugin] = {"vistestmodel": model_cls}
    try:
        register_plugin_app_config(plugin)

        assert model_cls in list(apps.get_models())
    finally:
        apps.all_models.pop(plugin, None)
        apps.app_configs.pop(plugin, None)
        apps.clear_cache()


# ===========================================================================
# Integration test — register with real plugin models
# ===========================================================================


@pytest.mark.django_db
def test_end_to_end_register_clean_references(tmp_path: Path) -> None:
    """Full pipeline: DDL generation leaves a clean Django registry.

    Model registration is suppressed during generate_plugin_migrations so
    schema-manager containers have the same registry state as non-schema-
    manager containers before load_or_reload_plugin runs.

    Verifies that after generate_plugin_migrations:
    - Plugin is NOT in app_configs (no AppConfig created)
    - Plugin is NOT in all_models (no models registered)
    - No sys.modules entries for the plugin remain
    - FK fields on returned model objects still resolve correctly
      (direct class references are set during ForeignKey.__init__,
      before register_model would have been called)
    """
    from django.apps import apps

    plugin_name = "reg_norm_integ"
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")

    models_dir = plugin_dir / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "things.py").write_text(
        dedent("""\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField, ForeignKey, DO_NOTHING

        class Category(CustomModel):
            name = TextField()

        class Item(CustomModel):
            title = TextField()
            category = ForeignKey(Category, on_delete=DO_NOTHING, null=True)
        """)
    )

    try:
        result = generate_plugin_migrations(plugin_name, plugin_dir, schema_name=plugin_name)

        # Registry should be clean — no AppConfig, no registered models,
        # no pending lazy references.
        assert plugin_name not in apps.app_configs
        assert plugin_name not in apps.all_models
        assert not any(k[0] == plugin_name for k in apps._pending_operations)

        # FK fields on the returned model objects should still resolve
        # correctly — direct class references are set during ForeignKey.__init__
        item_cls = next(m for m in result if m.__name__ == "Item")
        category_cls = next(m for m in result if m.__name__ == "Category")

        fk_field = next(
            f
            for f in item_cls._meta.local_fields
            if hasattr(f, "remote_field")
            and f.remote_field is not None
            and getattr(f.remote_field.model, "_meta", None) is not None
            and f.remote_field.model._meta.model_name == "category"
        )
        assert fk_field.remote_field is not None
        assert fk_field.remote_field.model is category_cls
    finally:
        apps.all_models.pop(plugin_name, None)
        apps.app_configs.pop(plugin_name, None)
        apps.clear_cache()


# ===========================================================================
# Tests for _evaluate_module sandbox behavior
# ===========================================================================


def test_evaluate_module_sandboxes_model_module_and_registers_in_sys_modules(
    tmp_path: Path,
) -> None:
    """_evaluate_module should sandbox model modules and register them in
    sys.modules from the sandbox scope (not via importlib).

    The resulting module should have _safe_import as __import__ in its
    __builtins__, preserving runtime sandbox protection.
    """
    from plugin_runner.sandbox import Sandbox

    plugin_name = "eval_model_plugin"
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    models_dir = plugin_dir / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").write_text("")
    (models_dir / "room.py").write_text(
        dedent("""\
        from canvas_sdk.v1.data.base import CustomModel
        from django.db.models import TextField

        class Room(CustomModel):
            name = TextField()
        """)
    )

    handler_file = plugin_dir / "handler.py"
    handler_file.write_text("x = 1\n")

    import sys

    parent_dir = str(tmp_path)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        sandbox = Sandbox(handler_file, namespace=f"{plugin_name}.handler")

        # Pre-populate _evaluated_modules for the plugin package __init__ so
        # that _evaluate_implicit_imports doesn't trigger a Sandbox for it.
        sandbox._evaluated_modules[plugin_name] = True

        module_name = f"{plugin_name}.models.room"
        sandbox._evaluate_module(module_name)

        # The model module should be registered in sys.modules
        assert module_name in sys.modules

        # The module should have _safe_import as __import__ (sandbox protection)
        mod = sys.modules[module_name]
        assert mod.__builtins__["__import__"].__name__ == "_safe_import"
    finally:
        for key in list(sys.modules.keys()):
            if key.startswith(f"{plugin_name}"):
                del sys.modules[key]
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)


def test_evaluate_module_still_sandboxes_non_model_modules(tmp_path: Path) -> None:
    """_evaluate_module should still call Sandbox.execute() for non-model modules."""
    from plugin_runner.sandbox import Sandbox

    plugin_name = "eval_sandbox_plugin"
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    utils_file = plugin_dir / "utils.py"
    utils_file.write_text("SOME_VALUE = 42\n")

    handler_file = plugin_dir / "handler.py"
    handler_file.write_text("x = 1\n")

    import sys

    parent_dir = str(tmp_path)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        sandbox = Sandbox(handler_file, namespace=f"{plugin_name}.handler")

        # Pre-populate _evaluated_modules for the plugin package __init__
        # so we only test the target module, not implicit imports.
        sandbox._evaluated_modules[plugin_name] = True

        with patch("plugin_runner.sandbox.Sandbox.execute", return_value={}) as mock_execute:
            sandbox._evaluate_module(f"{plugin_name}.utils")

            # Sandbox.execute() SHOULD have been called for a non-model module
            mock_execute.assert_called_once()
    finally:
        for key in list(sys.modules.keys()):
            if key.startswith(f"{plugin_name}"):
                del sys.modules[key]
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)
