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
    app.command()(commands.deploy)
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
def test_publish_hardens_git_auth_config(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """Publish resets inherited credential.helper + http.extraHeader for the CR
    host (so osxkeychain or a stale cr-login token can't shadow the helper) and
    registers our helper by absolute path (git invokes it via a bare shell).
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(push_rc=0)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["publish", str(plugin_dir), "--host", HOST])
    assert result.exit_code == 0, result.output

    calls = [c.args[0] for c in mock_run.call_args_list]
    prefix = ["git", "-C", str(plugin_dir), "config"]
    # credential helper list reset, then our helper added by absolute path
    assert prefix + ["credential.https://cr.example.helper", ""] in calls
    add = next(
        c for c in calls if c[3:6] == ["config", "--add", "credential.https://cr.example.helper"]
    )
    assert (
        add[6].startswith("!") and "git-credential" in add[6] and add[6].endswith(f"--host {HOST}")
    )
    # a stale cr-login Authorization extraHeader for the host is reset
    assert prefix + ["http.https://cr.example.extraHeader", ""] in calls


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


# -- deploy + consent --------------------------------------------------------


def _resp(body: dict, code: int = 200) -> Mock:
    """A fake requests.Response with a JSON body."""
    resp = Mock(status_code=code)
    resp.json.return_value = body
    return resp


def _post_router(
    *, deploy: dict, approve: dict | None = None, deny: dict | None = None
) -> Callable[..., Mock]:
    """Route requests.post by URL to the deploy / approve / deny fakes."""

    def post(url: str, **kwargs: object) -> Mock:
        if url.endswith("/control-room/deploy/"):
            return _resp(deploy)
        if url.endswith("/approve/"):
            return _resp(approve or {"ok": True, "dispatched": True})
        if url.endswith("/deny/"):
            return _resp(deny or {"ok": True, "cancelled_record_count": 1})
        return _resp({"error": "unexpected"}, 404)

    return post


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_dispatched(mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path) -> None:
    """A deploy with no consent gate reports dispatched and carries org/name/ref."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "dispatched",
            "matrix": {"id": "m1"},
            "consent_request_count": 0,
        }
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 0, result.output
    assert "dispatched" in result.output.lower()
    body = next(
        c.kwargs["json"] for c in mock_post.call_args_list if c.args[0].endswith("/deploy/")
    )
    assert body == {"plugins": [{"orgSlug": "acme", "name": "my_plugin", "gitRef": "main"}]}


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_pending_consent_auto_approves(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """--yes approves each inlined consent request; the last approval dispatches."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "pending_consent",
            "consent_request_count": 1,
            "consent_requests": [{"id": 7, "title": "hello-reader wants read", "implication": "x"}],
        },
        approve={"ok": True, "dispatched": True},
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST, "--yes"])

    assert result.exit_code == 0, result.output
    assert "dispatched" in result.output.lower()
    approve_urls = [c.args[0] for c in mock_post.call_args_list if c.args[0].endswith("/approve/")]
    assert approve_urls and approve_urls[0].endswith("/plugin-io/consent/7/approve/")


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_consent_denied_interactively(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """Declining a consent prompt denies the request and fails the deploy."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "pending_consent",
            "consent_request_count": 1,
            "consent_requests": [{"id": 7, "title": "hello-reader wants read"}],
        },
    )

    result = runner.invoke(
        _app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST], input="n\nnot this fork\n"
    )

    assert result.exit_code == 1
    deny_urls = [c.args[0] for c in mock_post.call_args_list if c.args[0].endswith("/deny/")]
    assert deny_urls and deny_urls[0].endswith("/plugin-io/consent/7/deny/")


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_failure_exits_nonzero(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A business failure (ok=false) exits non-zero with the CR error surfaced."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={"ok": False, "error": "Plugins not found: ['acme/my_plugin']"}
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "not found" in result.output.lower()
