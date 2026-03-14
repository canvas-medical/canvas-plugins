import importlib
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from pytest_django.plugin import DjangoDbBlocker


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(
    early_config: pytest.Config,
    parser: pytest.Parser,
    args: list[str],
) -> None:
    """Ensure canvas_sdk is imported to register its models and settings."""
    import canvas_sdk  # noqa: F401


@pytest.fixture(autouse=True)
def transaction(db: None) -> Generator[None, None, None]:
    """Ensure each test runs within a transaction."""
    yield


@pytest.fixture(scope="session", autouse=True)
def create_plugin_custom_model_tables(
    django_db_setup: None, django_db_blocker: DjangoDbBlocker, request: pytest.FixtureRequest
) -> None:
    """Create tables for plugin custom models in the SQLite test database.

    This fixture automatically detects which plugin is being tested and creates
    database tables for any custom models defined in the plugin's models/ directory.

    Since custom models have managed=True in SQLite but no Django migration files
    exist, we must manually create the tables using the same SQL generation logic
    used in production PostgreSQL installations.

    This fixture runs once per test session, after django_db_setup creates the test
    database but before any tests run.

    IMPORTANT: We deliberately avoid calling ``generate_plugin_migrations`` here
    because it re-executes model files via ``Sandbox.execute()``, creating new
    class objects distinct from those already imported by test code.  That causes
    Django's model registry to hold class-v2 while test code still references
    class-v1, breaking reverse relations (CASCADE, related_objects, M2M through).
    Instead we import model modules with ``importlib.import_module`` so the
    registered classes are the *same* objects that tests use, then create their
    tables directly.
    """
    from django.conf import settings

    # Only run for SQLite (test environments)
    if "sqlite3" not in settings.DATABASES["default"]["ENGINE"]:
        return

    # Detect plugin name and path from the test directory structure
    # Expected structure: /path/to/plugin_name/tests/...
    test_dir = Path(request.config.rootpath)
    plugin_name = test_dir.name.replace("-", "_")  # Convert plugin-name to plugin_name
    plugin_path = test_dir / plugin_name

    # Check if this is a plugin with custom models
    models_path = plugin_path / "models"
    if not models_path.exists():
        # No custom models, nothing to do
        return

    # Add canvas-plugins parent directory to path so we can import plugin_runner
    canvas_plugins_dir = Path(__file__).parent.parent.parent
    if str(canvas_plugins_dir) not in sys.path:
        sys.path.insert(0, str(canvas_plugins_dir))

    # Ensure the plugin's parent is on sys.path so intra-plugin imports resolve
    parent_dir = str(plugin_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Import all model modules so every CustomModel is registered in Django's
    # app registry.  Using importlib (not Sandbox) means the class objects in
    # the registry are identical to those imported by test code — no stale
    # references, no need for normalize_plugin_model_references.
    for model_file in sorted(models_path.glob("*.py")):
        if model_file.name == "__init__.py":
            module_name = f"{plugin_name}.models"
        else:
            module_name = f"{plugin_name}.models.{model_file.stem}"
        importlib.import_module(module_name)

    from django.apps import apps

    from plugin_runner.installation import (
        execute_create_table_sql,
        generate_create_table_sql,
        register_plugin_app_config,
        should_create_table,
    )

    with django_db_blocker.unblock():
        plugin_models = apps.all_models.get(plugin_name, {})
        for model_class in plugin_models.values():
            if should_create_table(model_class, plugin_name):
                create_sql = generate_create_table_sql(plugin_name, model_class)  # type: ignore[arg-type]
                execute_create_table_sql(create_sql)

        register_plugin_app_config(plugin_name)
