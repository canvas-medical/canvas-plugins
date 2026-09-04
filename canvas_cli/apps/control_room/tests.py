"""Tests for the headless Control Room CLI commands (KOALA-5923)."""

from __future__ import annotations

import json
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
    app.command(name="cr-init")(commands.cr_init)
    app.command()(commands.deploy)
    app.command(name="set-variables")(commands.set_variables)
    app.command(name="unset-variables")(commands.unset_variables)
    app.command(name="uninstall")(commands.uninstall)
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
    staged_files: list[str] | None = None,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Fake `subprocess.run` for the git calls cr-init (and the deploy/consent
    flow) make.

    ``remote_exists`` toggles whether `remote get-url cr` finds an existing
    remote (→ set-url vs add). The fetch/merge/dirty/staged knobs remain for
    completeness. Everything else falls through to rc=0.
    """

    def run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        sub = cmd[3:]  # cmd == ["git", "-C", <dir>, <subcommand>, ...]
        if sub[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return subprocess.CompletedProcess(cmd, 0, "true\n", "")
        if sub[:3] == ["remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(cmd, 0 if remote_exists else 1, "", "")
        if sub[:2] == ["push", "origin"]:
            return subprocess.CompletedProcess(cmd, push_rc, "", push_stderr)
        if sub[0] == "fetch":
            return subprocess.CompletedProcess(cmd, fetch_rc, "", fetch_stderr)
        if sub[0] == "merge":
            stdout = "" if merge_rc else "Already up to date.\n"
            return subprocess.CompletedProcess(cmd, merge_rc, stdout, merge_stderr)
        if sub[:3] == ["diff", "--cached", "--quiet"]:
            return subprocess.CompletedProcess(cmd, 1 if dirty else 0, "", "")
        if sub[:2] == ["diff", "--cached"] and "--name-only" in sub:
            payload = "\0".join(staged_files) + "\0" if staged_files else ""
            return subprocess.CompletedProcess(cmd, 0, payload, "")
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


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.post")
def test_git_credential_forbidden_surfaces_remediation(mock_post: Mock, _token: Mock) -> None:
    """A 403 from the role gate prints the actionable remediation (which git shows)
    instead of a raw '403 Client Error', and emits no credential.
    """
    mock_post.return_value = Mock(status_code=403)
    mock_post.return_value.json.return_value = {
        "code": "plugin_role_required",
        "remediation": "Ask a Canvas administrator to grant you either role.",
    }
    result = runner.invoke(
        _app(),
        ["git-credential", "--host", HOST, "get"],
        input="protocol=https\nhost=cr.example\n\n",
    )
    assert result.exit_code == 1
    assert "Ask a Canvas administrator to grant you either role." in result.output
    assert "username=git" not in result.output  # no credential emitted


# -- cr-init -----------------------------------------------------------------


@patch("requests.post")
@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_cr_init_configures_remote_and_helper(
    mock_run: Mock, mock_get: Mock, _token: Mock, mock_post: Mock, tmp_path: Path
) -> None:
    """cr-init discovers CR, registers the repo with Control Room, points `origin`
    at it, and registers the push credential helper — but never commits or pushes
    (the user does plain git).
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_post.return_value = _resp({"ok": True, "created": True})
    mock_run.side_effect = _git_side_effect()
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["cr-init", str(plugin_dir), "--host", HOST])

    assert result.exit_code == 0, result.output
    assert "Connected acme/my_plugin to Control Room" in result.output
    # Registered the repo with CR (ensurePluginRepo) before wiring the remote.
    ensure = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/ensure-repo/")
    )
    assert ensure.kwargs["json"] == {"orgSlug": "acme", "name": "my_plugin"}
    assert "git push origin HEAD:main" in result.output  # guidance for plain-git publish
    calls = [c.args[0] for c in mock_run.call_args_list]
    # origin pointed at the discovered {git_url}/{org}/{name}.git
    assert [
        "git",
        "-C",
        str(plugin_dir),
        "remote",
        "add",
        "origin",
        "https://cr.example/git/acme/my_plugin.git",
    ] in calls
    # the credential helper is registered by absolute path for the CR host
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
    # cr-init is setup-only: it never commits or pushes — that's the user's job now
    assert not any(c[3] == "commit" for c in calls)
    assert not any(c[3:5] == ["push", "origin"] for c in calls)


@patch("requests.post")
@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_cr_init_idempotent_updates_existing_remote(
    mock_run: Mock, mock_get: Mock, _token: Mock, mock_post: Mock, tmp_path: Path
) -> None:
    """Re-running updates the existing `cr` URL (set-url) rather than re-adding."""
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_post.return_value = _resp({"ok": True, "created": False})
    mock_run.side_effect = _git_side_effect(remote_exists=True)
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["cr-init", str(plugin_dir), "--host", HOST])

    assert result.exit_code == 0, result.output
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert any(c[3:6] == ["remote", "set-url", "origin"] for c in calls)
    assert not any(c[3:6] == ["remote", "add", "origin"] for c in calls)


@patch("requests.post")
@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_cr_init_aborts_when_repo_registration_fails(
    mock_run: Mock, mock_get: Mock, _token: Mock, mock_post: Mock, tmp_path: Path
) -> None:
    """If Control Room refuses to register the repo (e.g. no push permission),
    cr-init fails before wiring the `origin` remote.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_post.return_value = _resp({"ok": False, "error": "Permission denied"})
    mock_run.side_effect = _git_side_effect()
    plugin_dir = _plugin_dir(tmp_path)

    result = runner.invoke(_app(), ["cr-init", str(plugin_dir), "--host", HOST])

    assert result.exit_code != 0
    assert "Permission denied" in result.output
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert not any(c[3:6] == ["remote", "add", "origin"] for c in calls)


@patch("requests.post")
@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_cr_init_repo_name_decouples_git_repo_from_manifest(
    mock_run: Mock, mock_get: Mock, _token: Mock, mock_post: Mock, tmp_path: Path
) -> None:
    """--repo-name sets the git-repo identity independent of the manifest/package
    name (they're separate concepts in Control Room; canvas-plugins#1820). The
    manifest here is `my_plugin`, but the repo is named by the explicit id.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = INFO
    mock_post.return_value = _resp({"ok": True, "created": True})
    mock_run.side_effect = _git_side_effect()
    plugin_dir = _plugin_dir(tmp_path)  # manifest name == "my_plugin"

    result = runner.invoke(
        _app(),
        ["cr-init", str(plugin_dir), "--host", HOST, "--repo-name", "acme-abc123-my-plugin"],
    )

    assert result.exit_code == 0, result.output
    assert "Connected acme/acme-abc123-my-plugin" in result.output
    # The repo registered with CR uses the explicit repo id, not the manifest name.
    ensure = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/ensure-repo/")
    )
    assert ensure.kwargs["json"] == {"orgSlug": "acme", "name": "acme-abc123-my-plugin"}
    calls = [c.args[0] for c in mock_run.call_args_list]
    # remote points at the explicit repo id, NOT the manifest name
    assert [
        "git",
        "-C",
        str(plugin_dir),
        "remote",
        "add",
        "origin",
        "https://cr.example/git/acme/acme-abc123-my-plugin.git",
    ] in calls
    assert not any(c[3:5] == ["remote", "add"] and "my_plugin.git" in c[-1] for c in calls)


@patch("subprocess.run")
def test_cr_init_requires_git_repo(mock_run: Mock, tmp_path: Path) -> None:
    """cr-init refuses a non-git directory before any network call."""
    mock_run.return_value = subprocess.CompletedProcess([], 128, "", "not a git repository")
    result = runner.invoke(_app(), ["cr-init", str(_plugin_dir(tmp_path)), "--host", HOST])
    assert result.exit_code != 0
    assert "not a git repository" in result.output


@patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory", "git"))
@patch("canvas_cli.apps.control_room.commands.shutil.which", return_value=None)
def test_cr_init_without_git_installed_gives_actionable_error(
    _which: Mock, mock_run: Mock, tmp_path: Path
) -> None:
    """cr-init on a git-less system fails with an install hint, never spawning git."""
    result = runner.invoke(_app(), ["cr-init", str(_plugin_dir(tmp_path)), "--host", HOST])
    assert result.exit_code != 0
    assert "git-scm.com/downloads" in result.output
    assert not isinstance(result.exception, FileNotFoundError)
    mock_run.assert_not_called()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("subprocess.run")
def test_cr_init_fails_fast_without_plugin_role(
    mock_run: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """cr-init reads can_manage_plugins from info and bails with the remediation
    before configuring any git remote — so the user learns at setup, not from an
    opaque failure mid `git push`.
    """
    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = {**INFO, "can_manage_plugins": False}
    mock_run.side_effect = _git_side_effect()

    result = runner.invoke(_app(), ["cr-init", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "Administrative Developer or Clinical Developer" in result.output
    # Never configured git — no remote was added.
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert not any(c[3:5] == ["remote", "add"] for c in calls)


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


def _get_router(*, matrix: dict | None = None) -> Callable[..., Mock]:
    """Route requests.get: ``/info/`` → INFO, ``/deploy-status/<id>/`` → matrix.

    The default matrix is a settled ``succeeded`` (one cell), so the poll returns
    on the first read with no sleep. Pass ``matrix`` to settle failed/skipped.
    """
    settled = matrix or {"id": "m1", "status": "succeeded", "rollupCounts": {"succeeded": 1}}

    def get(url: str, **kwargs: object) -> Mock:
        if "/deploy-status/" in url:
            return _resp({"matrix": settled})
        return _resp(INFO)

    return get


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_polls_to_terminal_success(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A deploy dispatches, then polls the matrix to a terminal verdict and reports
    the real outcome (succeeded) rather than trusting the dispatch response.
    """
    mock_get.side_effect = _get_router()  # /info/ + /deploy-status/ → succeeded
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
    assert "succeeded" in result.output.lower()
    # The deploy (matrix) id is surfaced so a user can track it.
    assert "m1" in result.output
    # Polled the deploy-status endpoint for that matrix.
    assert any("/deploy-status/m1/" in c.args[0] for c in mock_get.call_args_list)
    body = next(
        c.kwargs["json"] for c in mock_post.call_args_list if c.args[0].endswith("/deploy/")
    )
    assert body == {"plugins": [{"orgSlug": "acme", "name": "my_plugin", "gitRef": "main"}]}


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_reports_failure_when_matrix_settles_failed(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A deploy that dispatches ``ok`` but whose matrix settles FAILED in the async
    CR flow exits nonzero — not masked as a dispatched success.
    """
    mock_get.side_effect = _get_router(
        matrix={"id": "m1", "status": "failed", "rollupCounts": {"failed": 1}}
    )
    mock_post.side_effect = _post_router(
        deploy={"ok": True, "status": "dispatched", "matrix": {"id": "m1"}}
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "did not succeed" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_deploy_forbidden_renders_remediation(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A 403 on deploy renders the actionable remediation, not 'not available'."""
    mock_get.return_value = _resp(INFO)
    mock_post.return_value = _resp(
        {"code": "plugin_role_required", "remediation": "Ask an admin to grant you either role."},
        403,
    )

    result = runner.invoke(_app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST])

    assert result.exit_code != 0
    assert "Ask an admin to grant you either role." in result.output
    assert "not available" not in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_set_variables_routes_through_cr(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """A bare ``KEY=value`` updates an existing variable and sends no ``sensitive``
    (unspecified) — Control Room keeps the stored sensitivity.
    """
    mock_get.side_effect = _get_router()  # /info/ discovery + /deploy-status/ → succeeded
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(
        _app(),
        ["set-variables", "my_plugin", "--host", HOST, "API_KEY=secret", "URL=https://x"],
    )

    assert result.exit_code == 0, result.output
    call = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/set-variables/")
    )
    assert call.kwargs["json"] == {
        "plugins": [
            {
                "orgSlug": "acme",
                "name": "my_plugin",
                "variables": [
                    {"key": "API_KEY", "value": "secret"},
                    {"key": "URL", "value": "https://x"},
                ],
            }
        ]
    }


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_set_variables_secret_and_variable_flags(
    mock_post: Mock, mock_get: Mock, _token: Mock
) -> None:
    """``--secret`` declares a sensitive variable, ``--variable`` a plain one; both
    are mixable in one call and carry an explicit ``sensitive`` flag.
    """
    mock_get.side_effect = _get_router()
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(
        _app(),
        [
            "set-variables", "my_plugin", "--host", HOST,
            "--secret", "API_KEY=abc",
            "--variable", "API_URL=https://x",
        ],
    )

    assert result.exit_code == 0, result.output
    call = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/set-variables/")
    )
    assert call.kwargs["json"]["plugins"][0]["variables"] == [
        {"key": "API_KEY", "value": "abc", "sensitive": True},
        {"key": "API_URL", "value": "https://x", "sensitive": False},
    ]


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_set_variables_requires_at_least_one(
    mock_post: Mock, mock_get: Mock, _token: Mock
) -> None:
    """With no positional and no flag, the command fails locally — no network call."""
    result = runner.invoke(_app(), ["set-variables", "my_plugin", "--host", HOST])
    assert result.exit_code != 0
    assert "at least one variable" in result.output.lower()
    mock_post.assert_not_called()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_set_variables_rejects_bad_format(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """A malformed variable fails locally (before any network call)."""
    result = runner.invoke(_app(), ["set-variables", "my_plugin", "--host", HOST, "noequals"])
    assert result.exit_code != 0
    assert "key=value" in result.output.lower()
    mock_post.assert_not_called()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_set_variables_warns_when_plugin_not_installed(
    mock_post: Mock, mock_get: Mock, _token: Mock
) -> None:
    """An all-SKIPPED CONFIGURE settles ``succeeded`` in CR but applied nothing
    (plugin not installed). The rollup — not the status — is authoritative, so the
    CLI tells the user the values were stored but not applied, and still exits 0.
    """
    mock_get.side_effect = _get_router(
        matrix={"id": "m1", "status": "succeeded", "rollupCounts": {"skipped": 1}}
    )
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(_app(), ["set-variables", "my_plugin", "--host", HOST, "API_KEY=secret"])

    assert result.exit_code == 0, result.output
    assert "not installed" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_unset_variables_routes_through_cr(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """`config unset` discovers the org and POSTs the keys to clear-variables, then
    polls the CONFIGURE matrix to a terminal verdict.
    """
    mock_get.side_effect = _get_router()  # /info/ + /deploy-status/ → succeeded
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(
        _app(), ["unset-variables", "my_plugin", "--host", HOST, "API_KEY", "URL"]
    )

    assert result.exit_code == 0, result.output
    call = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/clear-variables/")
    )
    assert call.kwargs["json"] == {
        "plugins": [{"orgSlug": "acme", "name": "my_plugin", "keys": ["API_KEY", "URL"]}]
    }
    assert any("/deploy-status/m1/" in c.args[0] for c in mock_get.call_args_list)


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_unset_variables_not_installed_is_ok(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """An all-SKIPPED CONFIGURE (plugin not installed) has nothing to unset on the
    instance — no failed records, so the unset still exits 0.
    """
    mock_get.side_effect = _get_router(
        matrix={"id": "m1", "status": "succeeded", "rollupCounts": {"skipped": 1}}
    )
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(_app(), ["unset-variables", "my_plugin", "--host", HOST, "API_KEY"])

    assert result.exit_code == 0, result.output


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_unset_variables_reports_failure(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """A CONFIGURE that settles FAILED exits nonzero."""
    mock_get.side_effect = _get_router(
        matrix={"id": "m1", "status": "failed", "rollupCounts": {"failed": 1}}
    )
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(_app(), ["unset-variables", "my_plugin", "--host", HOST, "API_KEY"])

    assert result.exit_code != 0
    assert "failed" in result.output.lower()


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_uninstall_routes_through_cr(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """`uninstall` (beta) discovers the org and POSTs to the uninstall proxy."""
    mock_get.side_effect = _get_router()  # /info/ discovery + /deploy-status/ → succeeded
    mock_post.return_value = _resp({"ok": True, "matrix": {"id": "m1"}})

    result = runner.invoke(_app(), ["uninstall", "my_plugin", "--host", HOST])

    assert result.exit_code == 0, result.output
    call = next(
        c for c in mock_post.call_args_list if c.args[0].endswith("/control-room/uninstall/")
    )
    assert call.kwargs["json"] == {"plugins": [{"orgSlug": "acme", "name": "my_plugin"}]}


@patch("canvas_cli.apps.control_room.commands.get_or_request_api_token", return_value="tok")
@patch("requests.get")
@patch("requests.post")
def test_uninstall_surfaces_cr_error(mock_post: Mock, mock_get: Mock, _token: Mock) -> None:
    """A CR business failure (ok=false) exits non-zero with the message."""
    mock_get.return_value = _resp(INFO)
    mock_post.return_value = _resp({"ok": False, "error": "Permission denied"})

    result = runner.invoke(_app(), ["uninstall", "my_plugin", "--host", HOST])

    assert result.exit_code != 0
    assert "Permission denied" in result.output


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
def test_deploy_consent_deny_rejected_by_server_surfaces_error(
    mock_post: Mock, mock_get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """A denial the server rejects (ok=false) must be surfaced, not reported as
    'Denied' — otherwise the operator thinks the request was cancelled when it's
    still live.
    """
    mock_get.return_value = _resp(INFO)
    mock_post.side_effect = _post_router(
        deploy={
            "ok": True,
            "status": "pending_consent",
            "consent_request_count": 1,
            "consent_requests": [{"id": 7, "title": "hello-reader wants read"}],
        },
        deny={"ok": False, "error": "Permission denied"},
    )

    result = runner.invoke(
        _app(), ["deploy", str(_plugin_dir(tmp_path)), "--host", HOST], input="n\nnope\n"
    )

    assert result.exit_code == 1
    assert "Denial failed" in result.output
    assert "Permission denied" in result.output


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
def test_cr_init_control_room_unreachable_exits(
    mock_run: Mock, _get: Mock, _token: Mock, tmp_path: Path
) -> None:
    """An unreachable instance during CR discovery fails with a clear message."""
    mock_run.side_effect = _git_side_effect()

    result = runner.invoke(_app(), ["cr-init", str(_plugin_dir(tmp_path)), "--host", HOST])

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


def test_cr_init_requires_host(tmp_path: Path) -> None:
    """cr-init refuses to run without a resolved host."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.cr_init(tmp_path, host=None)
    assert "specify a host" in str(exc.value)


def test_cr_init_requires_directory(tmp_path: Path) -> None:
    """cr-init refuses a plugin path that isn't a directory."""
    with pytest.raises(typer.BadParameter) as exc:
        commands.cr_init(tmp_path / "missing", host=HOST)
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
    """cr-init/deploy/git-credential are registered when CONTROL_ROOM_BETA=true;
    the retired publish/pull wrappers are not.
    """
    import importlib

    import canvas_cli.main

    monkeypatch.setenv("CONTROL_ROOM_BETA", "true")
    try:
        importlib.reload(canvas_cli.main)
        names = [
            (c.callback.__name__ if c.callback else None)
            for c in canvas_cli.main.app.registered_commands
        ]
        assert "cr_init" in names
        assert "deploy" in names
        assert "git_credential" in names
        assert "publish" not in names
        assert "pull" not in names
    finally:
        # Restore the module without the beta flag so other tests aren't polluted.
        monkeypatch.delenv("CONTROL_ROOM_BETA", raising=False)
        importlib.reload(canvas_cli.main)
