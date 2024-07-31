import shutil
from pathlib import Path

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


def test_canvas_init() -> None:
    """Tests that the CLI successfully creates a plugin with init."""
    result = runner.invoke(app, "init", input="testing_init")
    assert result.exit_code == 0

    # plugin directory exists
    plugin = Path("./testing_init")
    assert plugin.exists()
    assert plugin.is_dir()

    # manifest file exists
    manifest = Path("./testing_init/CANVAS_MANIFEST.json")
    assert manifest.exists()
    assert manifest.is_file()
    manifest_result = runner.invoke(app, "validate-manifest testing_init")
    assert manifest_result.exit_code == 0

    # readme file exists
    readme = Path("./testing_init/README.md")
    assert readme.exists()
    assert readme.is_file()

    # protocols dir exists
    protocols = Path("./testing_init/protocols")
    assert protocols.exists()
    assert protocols.is_dir()

    # protocol file exists in protocols dir
    protocol = Path("./testing_init/protocols/my_protocol.py")
    assert protocol.exists()
    assert protocol.is_file()

    shutil.rmtree(plugin)
