from typer.testing import CliRunner

from .main import app

runner = CliRunner()


def test_version_callback_exits_successfully() -> None:
    """Tests the CLI exits with 0 when calling with `--version`."""
    result = runner.invoke(app, "--version")
    assert result.exit_code == 0
