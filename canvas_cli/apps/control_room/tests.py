"""Tests for the headless Control Room CLI commands (KOALA-5923)."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import typer
from typer.testing import CliRunner

from canvas_cli.apps.control_room import commands

runner = CliRunner()
HOST = "https://acme.canvasmedical.com"
INFO = {"git_url": "https://cr.example/git", "org_slug": "acme"}


def _app() -> typer.Typer:
    """A local app so tests don't depend on the CONTROL_ROOM_BETA gate in main."""
    app = typer.Typer(rich_markup_mode=None)
    app.command(name="git-credential")(commands.git_credential)
    app.command()(commands.publish)
    app.command()(commands.pull)
    return app


def _plugin_dir(tmp_path: Path, name: str = "my_plugin") -> Path:
    """Create a plugin directory with a minimal CANVAS_MANIFEST.json."""
    directory = tmp_path / name
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": name}))
    return directory


def _git_side_effect(
    *, push_rc: int = 0, push_stderr: str = "", remote_exists: bool = False
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Fake `subprocess.run` for the git calls publish/pull make."""

    def run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        sub = cmd[3:]  # cmd == ["git", "-C", <dir>, <subcommand>, ...]
        if sub[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return subprocess.CompletedProcess(cmd, 0, "true\n", "")
        if sub[:3] == ["remote", "get-url", "cr"]:
            return subprocess.CompletedProcess(cmd, 0 if remote_exists else 1, "", "")
        if sub[:2] == ["push", "cr"]:
            return subprocess.CompletedProcess(cmd, push_rc, "", push_stderr)
        if sub[0] == "fetch":
            return subprocess.CompletedProcess(cmd, 0, "", "")
        if sub[0] == "merge":
            return subprocess.CompletedProcess(cmd, 0, "Already up to date.\n", "")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    return run


# -- git-credential ----------------------------------------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.post")
def test_git_credential_get_mints_jwt(mock_post: Mock, _token: Mock) -> None:
    """`get` returns username=git and a freshly minted JWT as the password."""
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.raise_for_status = Mock()
    mock_post.return_value.json.return_value = {"jwt": "JWT123", "expires_in": 300}

    result = runner.invoke(
        _app(),
        ["git-credential", "--host", HOST, "get"],
        input="protocol=https\nhost=cr.example\n\n",
    )

    assert result.exit_code == 0, result.output
    assert "username=git" in result.output
    assert "password=JWT123" in result.output
    assert "password_expiry_utc=" in result.output
    # Minted against the instance's endpoint, not the CR git host.
    assert mock_post.call_args.args[0].endswith("/plugin-io/control-room/mint-git-jwt/")


@patch("requests.post")
def test_git_credential_store_is_noop(mock_post: Mock) -> None:
    """`store`/`erase` do nothing — JWTs are ephemeral."""
    result = runner.invoke(_app(), ["git-credential", "--host", HOST, "store"], input="x=y\n\n")
    assert result.exit_code == 0
    assert result.output.strip() == ""
    mock_post.assert_not_called()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.post", side_effect=requests.RequestException("boom"))
def test_git_credential_get_failure_exits_nonzero(_post: Mock, _token: Mock) -> None:
    """A mint failure exits non-zero rather than making git prompt interactively."""
    result = runner.invoke(_app(), ["git-credential", "--host", HOST, "get"], input="")
    assert result.exit_code == 1


# -- publish -----------------------------------------------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_configures_remote_and_pushes(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """Publish discovers CR, points `cr` at the repo, and pushes HEAD to main."""
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(push_rc=0)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["publish", str(plugin_dir), "--host", HOST])

    assert result.exit_code == 0, result.output
    assert "Published acme/my_plugin" in result.output
    calls = [c.args[0] for c in mock_run.call_args_list]
    # cr remote pointed at the discovered {git_url}/{org}/{name}.git
    assert [
        "git",
        "-C",
        str(plugin_dir),
        "remote",
        "add",
        "cr",
        "https://cr.example/git/acme/my_plugin.git",
    ] in calls
    # pushed current HEAD to CR's canonical main ref
    assert any(c[3:6] == ["push", "cr", "HEAD:main"] for c in calls)


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_non_fast_forward_suggests_pull(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A rejected (non-fast-forward) push tells the author to `canvas pull`."""
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(
        push_rc=1, push_stderr="! [rejected] HEAD -> main (non-fast-forward)"
    )

    result = runner.invoke(_app(), ["publish", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "canvas pull" in result.output


@patch("subprocess.run")
def test_publish_requires_git_repo(mock_run: Mock, tmp_path: Path) -> None:
    """Publish refuses a non-git directory before making any network call."""
    mock_run.return_value = subprocess.CompletedProcess([], 128, "", "not a git repository")
    result = runner.invoke(_app(), ["publish", str(_plugin_dir(tmp_path)), "--host", HOST])
    assert result.exit_code != 0
    assert "not a git repository" in result.output


# -- pull --------------------------------------------------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_pull_fetches_and_merges(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """Pull fetches `cr` and merges `cr/main` into the working copy."""
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(remote_exists=True)

    result = runner.invoke(_app(), ["pull", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 0, result.output
    assert "up to date" in result.output.lower()
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert any(c[3:5] == ["fetch", "cr"] for c in calls)
    assert any(c[3:5] == ["merge", "--no-edit"] and c[5] == "cr/main" for c in calls)
