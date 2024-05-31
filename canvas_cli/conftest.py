from pathlib import Path

import pytest

import canvas_cli.main
from canvas_cli.utils.context import context


@pytest.fixture(autouse=True)
def monkeypatch_app_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatch `get_app_dir` in order to return a temp dir when testing, so we don't overwrite our config file."""

    def app_dir() -> str:
        return str(tmp_path)

    monkeypatch.setattr(canvas_cli.main, "get_app_dir", app_dir)


@pytest.fixture(autouse=True)
def reset_context_variables() -> None:
    """Reset the context properties to their default value.
    This is needed because we cannot build a `reset` method in the CLIContext class,
    because `load_from_file` loads properties dynamically.
    Also since this is a CLI, it's not expected to keep the global context in memory for more than a run,
    which definitely happens with tests run
    """
    context._default_host = None
