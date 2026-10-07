"""Tests for the authentication and deployment notice."""

import json
import time
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from canvas_cli.apps.plugin.plugin import install
from canvas_cli.main import app
from canvas_cli.utils.platform_notice import (
    MIGRATION_URL,
    NOTICE_INTERVAL_SECONDS,
    show_platform_notice,
)


def test_notice_prints_and_records_when_never_shown(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The first run prints the notice and records when it was shown."""
    show_platform_notice(str(tmp_path))

    assert MIGRATION_URL in capsys.readouterr().err
    assert json.loads((tmp_path / "platform_notice.json").read_text())["last_shown"] > 0


def test_notice_is_quiet_within_a_day(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A second run inside the interval prints nothing."""
    show_platform_notice(str(tmp_path))
    capsys.readouterr()

    show_platform_notice(str(tmp_path))

    assert capsys.readouterr().err == ""


def test_notice_prints_again_after_a_day(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Once the interval has passed, the notice prints again."""
    shown_at = time.time() - NOTICE_INTERVAL_SECONDS - 1
    (tmp_path / "platform_notice.json").write_text(json.dumps({"last_shown": shown_at}))

    show_platform_notice(str(tmp_path))

    assert MIGRATION_URL in capsys.readouterr().err


def test_notice_prints_over_a_corrupt_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unreadable record counts as never shown."""
    (tmp_path / "platform_notice.json").write_text("not json")

    show_platform_notice(str(tmp_path))

    assert MIGRATION_URL in capsys.readouterr().err


def test_every_command_shows_the_notice_once_a_day(tmp_path: Path) -> None:
    """Any subcommand shows the notice, and a second run the same day does not."""
    runner = CliRunner(mix_stderr=False)

    first = runner.invoke(app, ["validate-manifest", str(tmp_path)])
    second = runner.invoke(app, ["validate-manifest", str(tmp_path)])

    assert MIGRATION_URL in first.stderr
    assert MIGRATION_URL not in second.stderr


def test_git_credential_does_not_show_the_notice() -> None:
    """The credential helper, which git runs itself, never prints the notice."""
    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(app, ["git-credential", "erase"], input="")

    assert result.exit_code == 0
    assert MIGRATION_URL not in result.stderr


def test_install_warns_that_direct_installs_are_deprecated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`canvas install` prints the deprecation warning on every run."""
    with pytest.raises(typer.BadParameter):
        install(plugin_name=tmp_path, secrets=[], variables=[], is_enabled=True, host=None)

    err = capsys.readouterr().err
    assert "deprecated" in err
    assert MIGRATION_URL in err
