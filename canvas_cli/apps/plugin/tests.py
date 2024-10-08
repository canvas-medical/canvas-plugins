import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
import typer
from typer.testing import CliRunner

from canvas_cli.main import app

from .plugin import validate_package

runner = CliRunner()


def test_validate_package_unexistant_path() -> None:
    """Tests the validate_package callback with an invalid folder."""
    with pytest.raises(typer.BadParameter):
        validate_package(Path("/a_random_url_that_will_not_exist_or_so_I_hope"))


def test_validate_package_wrong_file_type(tmp_path: Path) -> None:
    """Tests the validate_package callback with an invalid file type."""
    invalid_file = tmp_path / "tmp_file.zip"
    invalid_file.write_text("definitely not a python package")

    with pytest.raises(typer.BadParameter):
        validate_package(invalid_file)


def test_validate_package_valid_file(tmp_path: Path) -> None:
    """Tests the validate_package callback with a valid file type."""
    package_path = tmp_path / "test-package.whl"
    package_path.write_text("something")
    result = validate_package(package_path)
    assert result == package_path


@pytest.fixture(scope="session")
def init_plugin_name() -> str:
    """The plugin name to be used for the canvas cli init test"""
    return f"testing_init-{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(autouse=True, scope="session")
def clean_up_plugin(init_plugin_name: str) -> Generator[Any, Any, Any]:
    yield
    if Path(f"./{init_plugin_name}").exists():
        shutil.rmtree(Path(f"./{init_plugin_name}"))


def test_canvas_init(init_plugin_name: str) -> None:
    """Tests that the CLI successfully creates a plugin with init."""
    result = runner.invoke(app, "init", input=init_plugin_name)
    assert result.exit_code == 0

    # plugin directory exists
    plugin = Path(f"./{init_plugin_name}")
    assert plugin.exists()
    assert plugin.is_dir()

    # manifest file exists
    manifest = Path(f"./{init_plugin_name}/CANVAS_MANIFEST.json")
    assert manifest.exists()
    assert manifest.is_file()
    manifest_result = runner.invoke(app, f"validate-manifest {init_plugin_name}")
    assert manifest_result.exit_code == 0

    # readme file exists
    readme = Path(f"./{init_plugin_name}/README.md")
    assert readme.exists()
    assert readme.is_file()

    # protocols dir exists
    protocols = Path(f"./{init_plugin_name}/protocols")
    assert protocols.exists()
    assert protocols.is_dir()

    # protocol file exists in protocols dir
    protocol = Path(f"./{init_plugin_name}/protocols/my_protocol.py")
    assert protocol.exists()
    assert protocol.is_file()
