import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from plugin_runner.plugin_runner import EVENT_HANDLER_MAP, LOADED_PLUGINS, load_plugins

BASE_DIR = Path(__file__).parent
FIXTURES_PLUGIN_DIR = BASE_DIR / "plugin_runner" / "tests" / "fixtures" / "plugins"
DATA_PLUGIN_DIR = BASE_DIR / "plugin_runner" / "tests" / "data" / "plugins"
INTEGRATION_TESTS_PLUGINS_DIR = BASE_DIR / "integration_tests"


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    """Return a CliRunner."""
    return CliRunner()


@pytest.fixture(scope="session", autouse=True)
def setup_plugins_dir() -> Generator[None, None, None]:
    """Set up the plugins directory before running tests."""
    DATA_PLUGIN_DIR.mkdir(exist_ok=True, parents=True)
    INTEGRATION_TESTS_PLUGINS_DIR.mkdir(exist_ok=True, parents=True)
    yield
    shutil.rmtree(DATA_PLUGIN_DIR.parent)
    shutil.rmtree(INTEGRATION_TESTS_PLUGINS_DIR)


@pytest.fixture
def install_test_plugin(request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Copies a specified plugin from the fixtures directory to the data directory
    and removes it after the test.

    Parameters:
    - request.param: The name of the plugin package to copy.

    Yields:
    - Path to the copied plugin directory.
    """
    # The plugin name should be passed as a parameter to the fixture
    plugin_name = request.param  # Expected to be a str
    src_plugin_path = FIXTURES_PLUGIN_DIR / plugin_name
    dest_plugin_path = DATA_PLUGIN_DIR / plugin_name

    # Copy the specific plugin from fixtures to data
    try:
        shutil.copytree(src_plugin_path, dest_plugin_path)
        yield dest_plugin_path  # Provide the path to the test
    finally:
        # Cleanup: remove data/plugins directory after the test
        if dest_plugin_path.exists():
            shutil.rmtree(dest_plugin_path)


@pytest.fixture
def load_test_plugins() -> Generator[None, None, None]:
    """Manages the lifecycle of test plugins by loading and unloading them."""
    try:
        load_plugins()
        yield
    finally:
        LOADED_PLUGINS.clear()
        EVENT_HANDLER_MAP.clear()


@pytest.fixture(scope="session")
def integration_tests_plugins_dir(setup_plugins_dir: None) -> Path:
    """Fixture to provide the path to the integration test plugins' directory."""
    return INTEGRATION_TESTS_PLUGINS_DIR
