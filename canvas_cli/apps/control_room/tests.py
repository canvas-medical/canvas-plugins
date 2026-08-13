"""Tests for the headless Control Room CLI commands (KOALA-5923)."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
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
    *,
    push_rc: int = 0,
    push_stderr: str = "",
    remote_exists: bool = False,
    fetch_rc: int = 0,
    fetch_stderr: str = "",
    merge_rc: int = 0,
    merge_stderr: str = "",
    dirty: bool = False,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Fake `subprocess.run` for the git calls publish/pull make.

    ``dirty`` models an uncommitted working tree: `diff --cached --quiet` reports
    a staged diff and `status --porcelain` lists a change. Everything else
    (`add`, `commit`, `config user.*`) falls through to the rc=0 default.
    """

    def run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        sub = cmd[3:]  # cmd == ["git", "-C", <dir>, <subcommand>, ...]
        if sub[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return subprocess.CompletedProcess(cmd, 0, "true\n", "")
        if sub[:3] == ["remote", "get-url", "cr"]:
            return subprocess.CompletedProcess(cmd, 0 if remote_exists else 1, "", "")
        if sub[:2] == ["push", "cr"]:
            return subprocess.CompletedProcess(cmd, push_rc, "", push_stderr)
        if sub[0] == "fetch":
            return subprocess.CompletedProcess(cmd, fetch_rc, "", fetch_stderr)
        if sub[0] == "merge":
            stdout = "" if merge_rc else "Already up to date.\n"
            return subprocess.CompletedProcess(cmd, merge_rc, stdout, merge_stderr)
        if sub[:3] == ["diff", "--cached", "--quiet"]:
            return subprocess.CompletedProcess(cmd, 1 if dirty else 0, "", "")
        if sub[:2] == ["status", "--porcelain"]:
            return subprocess.CompletedProcess(cmd, 0, "M hello/x.py\n" if dirty else "", "")
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
def test_publish_registers_helper_and_isolates_push_config(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """Publish registers our credential helper by absolute path (git invokes it
    via a bare shell) as the sole helper for the CR host, and runs the push with
    global/system git config ignored so nothing above the repo — a stale
    cr-login extraHeader or osxkeychain — can shadow it.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(push_rc=0)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["publish", str(plugin_dir), "--host", HOST])
    assert result.exit_code == 0, result.output

    calls = [c.args[0] for c in mock_run.call_args_list]
    # our helper is registered by absolute path, replacing any prior local entry
    helper = next(
        c
        for c in calls
        if c[3:6] == ["config", "--replace-all", "credential.https://cr.example.helper"]
    )
    assert (
        helper[6].startswith("!")
        and "git-credential" in helper[6]
        and helper[6].endswith(f"--host {HOST}")
    )
    # the push runs with global + system git config redirected to /dev/null
    push_call = next(c for c in mock_run.call_args_list if c.args[0][3:6] == ["push", "cr", "HEAD:main"])
    push_env = push_call.kwargs["env"]
    assert push_env["GIT_CONFIG_GLOBAL"] == os.devnull
    assert push_env["GIT_CONFIG_SYSTEM"] == os.devnull
    # config-setting calls are NOT isolated (writes go to local config normally)
    helper_call = next(
        c for c in mock_run.call_args_list if c.args[0][3:5] == ["config", "--replace-all"]
    )
    assert "GIT_CONFIG_GLOBAL" not in helper_call.kwargs.get("env", {})


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


@patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory", "git"))
@patch("canvas_cli.apps.control_room.commands.shutil.which", return_value=None)
def test_publish_without_git_installed_gives_actionable_error(
    _which: Mock, mock_run: Mock, tmp_path: Path
) -> None:
    """Publish on a git-less system fails with an install hint, not a raw
    FileNotFoundError traceback, and never tries to spawn git.
    """
    result = runner.invoke(_app(), ["publish", str(_plugin_dir(tmp_path)), "--host", HOST])
    assert result.exit_code != 0
    assert "git-scm.com/downloads" in result.output
    # The preflight fires before any git subprocess — no FileNotFoundError leaks.
    assert not isinstance(result.exception, FileNotFoundError)
    mock_run.assert_not_called()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_auto_commits_working_tree(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A dirty tree is staged + committed for the author (git stays invisible),
    then pushed. The commit falls back to a Canvas identity when none is set.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(push_rc=0, dirty=True)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(
        _app(), ["publish", str(plugin_dir), "--host", HOST, "-m", "my snapshot"]
    )
    assert result.exit_code == 0, result.output

    calls = [c.args[0] for c in mock_run.call_args_list]
    assert ["git", "-C", str(plugin_dir), "add", "-A"] in calls
    commit = next(c for c in mock_run.call_args_list if c.args[0][3] == "commit")
    assert "my snapshot" in commit.args[0]  # our message is used
    # no configured identity in this repo → Canvas fallback, and the commit is
    # NOT config-isolated (so a configured identity would be honored)
    assert commit.kwargs["env"]["GIT_AUTHOR_NAME"] == "Canvas CLI"
    assert "GIT_CONFIG_GLOBAL" not in commit.kwargs["env"]
    assert any(c[3:6] == ["push", "cr", "HEAD:main"] for c in calls)


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_no_commit_skips_snapshot_and_warns(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """--no-commit publishes HEAD as-is: no commit is made, and the author is
    warned that uncommitted changes won't ship.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_run.side_effect = _git_side_effect(push_rc=0, dirty=True)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["publish", str(plugin_dir), "--host", HOST, "--no-commit"])
    assert result.exit_code == 0, result.output
    assert "won't ship" in result.output

    calls = [c.args[0] for c in mock_run.call_args_list]
    assert not any(c[3] == "commit" for c in calls)  # nothing committed
    assert any(c[3:6] == ["push", "cr", "HEAD:main"] for c in calls)


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_clean_tree_reports_nothing_new(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A clean tree already on CR reports 'nothing new', not a misleading
    'Published'.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    # clean tree (no commit) + git's up-to-date push message
    mock_run.side_effect = _git_side_effect(push_stderr="Everything up-to-date", dirty=False)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["publish", str(plugin_dir), "--host", HOST])
    assert result.exit_code == 0, result.output
    assert "Nothing new to publish" in result.output
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert not any(c[3] == "commit" for c in calls)


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


# -- Control Room discovery / proxy transport errors -------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get", side_effect=requests.RequestException("network down"))
@patch("subprocess.run")
def test_publish_control_room_unreachable_exits(
    mock_run: Mock, _get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """An unreachable instance during CR discovery fails with a clear message."""
    mock_run.side_effect = _git_side_effect()

    result = runner.invoke(_app(), ["publish", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "could not reach" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
def test_deploy_control_room_unconfigured_exits(
    mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A non-200 from control-room/info surfaces the JSON error detail."""
    mock_get.return_value = _resp({"error": "CR not enabled"}, code=503)

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "not available" in result.output.lower()
    assert "CR not enabled" in result.output


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post", side_effect=requests.RequestException("boom"))
def test_deploy_post_transport_error_exits(
    _post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A transport error POSTing the deploy fails loudly rather than hanging."""
    mock_get.return_value = _resp(INFO)

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "could not reach" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_post_non_200_exits(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A non-200 from the deploy proxy surfaces the raw body when it isn't JSON."""
    mock_get.return_value = _resp(INFO)
    bad = Mock(status_code=502, text="502 Bad Gateway")
    bad.json.side_effect = ValueError("no json")
    mock_post.return_value = bad

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "502" in result.output
    assert "Bad Gateway" in result.output


# -- _manifest_name edge cases -----------------------------------------------


def test_manifest_name_missing_file(tmp_path: Path) -> None:
    """A plugin dir without a manifest is rejected."""
    (tmp_path / "plug").mkdir()
    with pytest.raises(typer.BadParameter) as exc:
        commands._manifest_name(tmp_path / "plug")
    assert "CANVAS_MANIFEST.json" in str(exc.value)


def test_manifest_name_invalid_json(tmp_path: Path) -> None:
    """A manifest that isn't valid JSON is reported, not swallowed."""
    directory = tmp_path / "plug"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text("{not json")
    with pytest.raises(typer.BadParameter) as exc:
        commands._manifest_name(directory)
    assert "Could not read" in str(exc.value)


def test_manifest_name_missing_name(tmp_path: Path) -> None:
    """A manifest with no `name` key is rejected."""
    directory = tmp_path / "plug"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text("{}")
    with pytest.raises(typer.BadParameter) as exc:
        commands._manifest_name(directory)
    assert "name" in str(exc.value)


# -- host / directory guards -------------------------------------------------


def test_publish_requires_host(tmp_path: Path) -> None:
    """Publish refuses to run without a resolved host."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.publish(tmp_path, host=None)
    assert "specify a host" in str(exc.value)


def test_publish_requires_directory(tmp_path: Path) -> None:
    """Publish refuses a plugin path that isn't a directory."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.publish(tmp_path / "missing", host=HOST)
    assert "valid directory" in str(exc.value)


def test_pull_requires_host(tmp_path: Path) -> None:
    """Pull refuses to run without a resolved host."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.pull(tmp_path, host=None)
    assert "specify a host" in str(exc.value)


def test_pull_requires_directory(tmp_path: Path) -> None:
    """Pull refuses a plugin path that isn't a directory."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.pull(tmp_path / "missing", host=HOST)
    assert "valid directory" in str(exc.value)


def test_deploy_requires_host(tmp_path: Path) -> None:
    """Deploy refuses to run without a resolved host."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.deploy(tmp_path, host=None)
    assert "specify a host" in str(exc.value)


def test_deploy_requires_directory(tmp_path: Path) -> None:
    """Deploy refuses a plugin path that isn't a directory."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.deploy(tmp_path / "missing", host=HOST)
    assert "valid directory" in str(exc.value)


# -- publish / pull git failures ---------------------------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_publish_push_failure_reports_stderr(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A push failure unrelated to fast-forward surfaces git's stderr."""
    mock_get.return_value = _resp(INFO)
    mock_run.side_effect = _git_side_effect(
        push_rc=1, push_stderr="fatal: Authentication failed for 'cr'"
    )

    result = runner.invoke(_app(), ["publish", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "Authentication failed" in result.output


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_pull_fetch_failure_exits(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A failed `git fetch` from Control Room exits non-zero with git's stderr."""
    mock_get.return_value = _resp(INFO)
    mock_run.side_effect = _git_side_effect(
        remote_exists=True, fetch_rc=1, fetch_stderr="fatal: could not read from remote"
    )

    result = runner.invoke(_app(), ["pull", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "could not read from remote" in result.output


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_pull_merge_conflict_asks_for_resolution(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A merge conflict tells the author to resolve, commit, and publish again."""
    mock_get.return_value = _resp(INFO)
    mock_run.side_effect = _git_side_effect(
        remote_exists=True, merge_rc=1, merge_stderr="CONFLICT (content): Merge conflict in a.py"
    )

    result = runner.invoke(_app(), ["pull", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "manual resolution" in result.output.lower()


# -- _handle_consent edge cases ----------------------------------------------


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_pending_consent_without_details_exits(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A pending_consent status with no inlined requests is an error, not a silent pass."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={"ok": True, "status": "pending_consent", "consent_request_count": 2}
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code == 1
    assert "no request details" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_consent_approval_failure_exits(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A failed approval POST aborts the deploy non-zero."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "pending_consent",
            "consent_request_count": 1,
            "consent_requests": [{"id": 7, "title": "hello-reader wants read"}],
        },
        approve={"ok": False, "error": "operator lacks permission"},
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST, "--yes"])

    assert result.exit_code == 1
    assert "approval failed" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_consent_recorded_pending_other_approvals(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """An approval that doesn't itself dispatch reports consent recorded, exit 0."""
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "pending_consent",
            "consent_request_count": 1,
            "consent_requests": [{"id": 7, "title": "hello-reader wants read"}],
        },
        approve={"ok": True, "dispatched": False},
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST, "--yes"])

    assert result.exit_code == 0, result.output
    assert "consent recorded" in result.output.lower()


# -- CONTROL_ROOM_BETA registration gate -------------------------------------


def test_main_registers_control_room_commands_with_beta_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """publish/pull/deploy/git-credential are registered when CONTROL_ROOM_BETA=true."""
    import importlib

    import canvas_cli.main

    monkeypatch.setenv("CONTROL_ROOM_BETA", "true")
    try:
        importlib.reload(canvas_cli.main)
        names = [
            (c.callback.__name__ if c.callback else None)
            for c in canvas_cli.main.app.registered_commands
        ]
        assert "publish" in names
        assert "pull" in names
        assert "deploy" in names
        assert "git_credential" in names
    finally:
        # Restore the module without the beta flag so other tests aren't polluted.
        monkeypatch.delenv("CONTROL_ROOM_BETA", raising=False)
        importlib.reload(canvas_cli.main)
