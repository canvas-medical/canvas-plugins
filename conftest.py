import shutil
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def setup_test_plugin(request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Copies a specified plugin from the fixtures directory to the data directory
    and removes it after the test.

    Parameters:
    - request.param: The name of the plugin package to copy.

    Yields:
    - Path to the copied plugin directory.
    """
    # Define base directories
    base_dir = Path("./plugin_runner/tests")
    fixture_plugin_dir = base_dir / "fixtures" / "plugins"
    data_plugin_dir = base_dir / "data" / "plugins"

    # The plugin name should be passed as a parameter to the fixture
    plugin_name = request.param  # Expected to be a str
    src_plugin_path = fixture_plugin_dir / plugin_name
    dest_plugin_path = data_plugin_dir / plugin_name

    # Ensure the data plugin directory exists
    data_plugin_dir.mkdir(parents=True, exist_ok=True)

    # Copy the specific plugin from fixtures to data
    try:
        shutil.copytree(src_plugin_path, dest_plugin_path)
        yield dest_plugin_path  # Provide the path to the test
    finally:
        # Cleanup: remove data/plugins directory after the test
        if dest_plugin_path.exists():
            shutil.rmtree(dest_plugin_path)
