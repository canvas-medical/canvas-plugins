import sys
from collections.abc import Generator
from pathlib import Path

import pytest


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
    django_db_setup, django_db_blocker, request: pytest.FixtureRequest
) -> None:
    """Create tables for plugin custom models in the SQLite test database.

    This fixture automatically detects which plugin is being tested and creates
    database tables for any custom models defined in the plugin's models/ directory.

    Since custom models have managed=True in SQLite but no Django migration files
    exist, we must manually create the tables using the same SQL generation logic
    used in production PostgreSQL installations.

    This fixture runs once per test session, after django_db_setup creates the test
    database but before any tests run.
    """
    from django.conf import settings

    # Only run for SQLite (test environments)
    if "sqlite3" not in settings.DATABASES["default"]["ENGINE"]:
        return

    # Detect plugin name and path from the test directory structure
    # Expected structure: /path/to/plugin_name/tests/...
    test_dir = Path(request.config.rootdir)
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

    from plugin_runner.installation import generate_plugin_migrations

    with django_db_blocker.unblock():
        # Generate and execute CREATE TABLE statements for custom models
        # This will detect SQLite and generate SQLite-compatible SQL
        generate_plugin_migrations(plugin_name, plugin_path)
