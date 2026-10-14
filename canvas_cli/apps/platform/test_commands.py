"""Tests for the Canvas Platform commands: deploy, clone, init, config, uninstall and the git helper.

HTTP is mocked with requests-mock; git is real, pushing to a bare repository on
disk through a ``file://`` URL standing in for platform's git server.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests_mock as requests_mock_module
import typer
from typer.testing import CliRunner

from canvas_cli.apps.platform import auth, commands, git
from canvas_cli.main import app

runner = CliRunner()
PLATFORM = "https://platform.example"
API = f"{PLATFORM}/api/v1"
NAME = "acme__intake"

ACME: dict[str, Any] = {
    "slug": "acme",
    "name": "Acme Health",
    "plugin_prefix": "acme",
    "capabilities": [
        "view_org_assets",
        "push_plugin_code",
        "deploy_plugin",
        "configure_plugin",
        "uninstall_plugin",
    ],
}
ME: dict[str, Any] = {
    "email": "dana@acme.example",
    "name": "Dana Reyes",
    "canvas_employee": False,
    "organizations": [ACME],
}


def _instance(slug: str, *capabilities: str, managed: bool = True) -> dict:
    return {
        "slug": slug,
        "organization": "acme",
        "stage": "staging",
        "production": False,
        "managed": managed,
        "capabilities": list(capabilities),
    }


def _deployment(status: str, *, action: str = "deploy", targets: list[dict] | None = None) -> dict:
    return {
        "id": "6f1c",
        "action": action,
        "status": status,
        "organization": "acme",
        "targets": targets
        if targets is not None
        else [
            {
                "plugin": NAME,
                "instance": "acme-staging",
                "status": "succeeded" if status == "succeeded" else "pending",
                "error": "",
                "undeclared_values": [],
            }
        ],
        "consent_requests": [],
    }


def _git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _helpers(directory: Path) -> list[str]:
    """Every credential helper entry for the git server, in order, empty ones included."""
    output = subprocess.run(
        ["git", "-C", str(directory), "config", "--get-all", "credential.file://.helper"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return output.removesuffix("\n").split("\n")


@pytest.fixture(autouse=True)
def _git_identity_and_fast_polling(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(variable, "Test")
    for variable in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(variable, "test@example.com")
    monkeypatch.setattr(commands, "POLL_INTERVAL_SECONDS", 0)


@pytest.fixture
def signed_in() -> None:
    """A stored session with the test platform, which becomes the default."""
    auth.save_tokens(
        PLATFORM,
        {"access_token": "cnvs_ua_1", "refresh_token": "cnvs_rt_1", "expires_in": 3600},
        make_default=True,
    )


@pytest.fixture
def bare(tmp_path: Path) -> Path:
    """A bare repository standing in for platform's git server."""
    path = tmp_path / "server" / f"{NAME}.git"
    path.mkdir(parents=True)
    _git(path, "init", "--bare", "--initial-branch=main")
    return path


@pytest.fixture
def package(tmp_path: Path) -> Path:
    """A committed plugin package at ``<repo>/acme__intake``."""
    repo = tmp_path / "work"
    directory = repo / NAME
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "add", NAME)
    _git(repo, "commit", "-m", "first")
    return directory


@pytest.fixture
def api(requests_mock: requests_mock_module.Mocker, bare: Path) -> requests_mock_module.Mocker:
    """The platform endpoints a deploy reads, answering for a plugin pushed to ``bare``."""
    requests_mock.get(f"{API}/me", json=ME)
    requests_mock.get(
        f"{API}/instances",
        json={"instances": [_instance("acme-staging", "deploy_plugin", "configure_plugin")]},
    )
    requests_mock.post(
        f"{API}/orgs/acme/plugins",
        status_code=201,
        json={
            "name": NAME,
            "publisher": "acme",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("in_progress"))
    requests_mock.get(f"{API}/deployments/6f1c", json=_deployment("succeeded"))
    return requests_mock


def _requests_to(mock: requests_mock_module.Mocker, method: str, suffix: str) -> list:
    return [r for r in mock.request_history if r.method == method and r.url.endswith(suffix)]


# -- deploy: validation first ------------------------------------------------


@patch("subprocess.run")
def test_deploy_refuses_an_unprefixed_name_before_any_git_or_network(
    mock_run: Mock,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """An unprefixed manifest name is refused before git runs or platform is called."""
    directory = tmp_path / "intake"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "intake"}))

    result = runner.invoke(app, ["deploy", str(directory), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "publisher-prefixed name like `<your org prefix>__intake`" in result.output
    mock_run.assert_not_called()
    assert not requests_mock.called


@patch("subprocess.run")
def test_deploy_refuses_a_prefix_of_no_organization_the_person_belongs_to(
    mock_run: Mock,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A well-formed name with someone else's prefix is refused, listing the person's prefixes."""
    requests_mock.get(f"{API}/me", json=ME)
    directory = tmp_path / "beta__intake"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "beta__intake"}))

    result = runner.invoke(app, ["deploy", str(directory)])

    assert result.exit_code == 2
    assert "<your org prefix>__intake" in result.output
    assert "acme" in result.output
    mock_run.assert_not_called()


def test_deploy_needs_a_session(package: Path) -> None:
    """Signed out, deploy says to run `canvas login`."""
    result = runner.invoke(app, ["deploy", str(package)])

    assert result.exit_code == 1
    assert "canvas login" in result.output


# -- deploy: the flow --------------------------------------------------------


def test_deploy_registers_pushes_and_deploys_the_pushed_commit(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """Deploy registers the plugin, points origin at its repository, pushes HEAD to main and
    deploys that exact commit, then reports each target.
    """
    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    head = _git(package, "rev-parse", "HEAD")
    assert _git(bare, "rev-parse", "main") == head

    register = _requests_to(api, "POST", "/orgs/acme/plugins")
    assert register[0].json() == {"name": NAME}
    deployment = _requests_to(api, "POST", "/deployments")[0].json()
    assert deployment == {
        "action": "deploy",
        "plugins": [{"name": NAME, "ref": head}],
        "instances": ["acme-staging"],
    }

    assert _git(package, "remote", "get-url", "origin") == bare.as_uri()
    assert _git(package, "config", "credential.file://.useHttpPath") == "true"
    # The empty entry resets helpers inherited from above the repository, such as
    # macOS's osxkeychain, so only `canvas` answers for the git server.
    reset, helper = _helpers(package)
    assert reset == ""
    assert helper.startswith("!") and helper.endswith(f"git-credential --platform {PLATFORM}")

    assert f"{NAME} on acme-staging: succeeded" in result.output
    assert f"Deploy of {NAME} succeeded." in result.output


def test_deploy_targets_the_only_instance_the_person_can_deploy_to(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """Without --instance, the single deployable managed instance is chosen and named."""
    api.get(
        f"{API}/instances",
        json={
            "instances": [
                _instance("acme-staging", "deploy_plugin"),
                _instance("acme-prod", "configure_plugin"),
                _instance("acme-old", "deploy_plugin", managed=False),
            ]
        },
    )

    result = runner.invoke(app, ["deploy", str(package)])

    assert result.exit_code == 0, result.output
    assert "Targeting acme-staging" in result.output
    assert _requests_to(api, "POST", "/deployments")[0].json()["instances"] == ["acme-staging"]


def test_deploy_lists_the_choices_when_several_instances_qualify(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """Several deployable instances and no --instance is refused before anything is pushed."""
    api.get(
        f"{API}/instances",
        json={
            "instances": [
                _instance("acme-staging", "deploy_plugin"),
                _instance("acme-prod", "deploy_plugin"),
            ]
        },
    )

    result = runner.invoke(app, ["deploy", str(package)])

    assert result.exit_code == 2
    assert "acme-prod, acme-staging" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")
    assert _git(bare, "for-each-ref") == ""


@patch("subprocess.run")
def test_deploy_no_push_deploys_main_without_git(
    mock_run: Mock, api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """--no-push deploys the pushed main as-is and never runs git."""
    result = runner.invoke(app, ["deploy", str(package), "--no-push", "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": NAME, "ref": "main"}
    ]
    mock_run.assert_not_called()


@patch("subprocess.run")
def test_deploy_ref_deploys_that_ref(
    mock_run: Mock, api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """--ref deploys the named ref without pushing."""
    result = runner.invoke(
        app, ["deploy", str(package), "--ref", "v1.2.0", "--instance", "acme-staging"]
    )

    assert result.exit_code == 0, result.output
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": NAME, "ref": "v1.2.0"}
    ]
    mock_run.assert_not_called()


def test_deploy_push_only_pushes_head_and_deploys_nothing(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """--push-only registers the plugin and pushes HEAD to main, and never looks for an
    instance or starts a deployment.
    """
    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 0, result.output
    head = _git(package, "rev-parse", "HEAD")
    assert _git(bare, "rev-parse", "main") == head
    assert _requests_to(api, "POST", "/orgs/acme/plugins")
    assert not _requests_to(api, "GET", "/instances")
    assert not _requests_to(api, "POST", "/deployments")
    assert f"Pushed {head[:12]} to main." in result.output
    assert "Not deployed" in result.output


def test_deploy_push_only_needs_no_instance(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """A publisher with no instance it can deploy to can still push."""
    api.get(f"{API}/instances", json={"instances": []})

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", "main") == _git(package, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    "extra", [["--instance", "acme-staging"], ["--ref", "v1.2.0"], ["--no-push"]]
)
def test_deploy_push_only_refuses_the_deploy_options(
    extra: list[str],
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    signed_in: None,
) -> None:
    """--push-only with an option only a deployment uses is refused before anything runs."""
    result = runner.invoke(app, ["deploy", str(package), "--push-only", *extra])

    assert result.exit_code == 2
    assert "--push-only pushes without deploying" in result.output
    assert not api.called
    assert _git(bare, "for-each-ref") == ""


def test_deploy_push_only_still_needs_the_push_capability(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """A member without the Plugin developer role cannot push with --push-only either."""
    reader = {**ACME, "capabilities": ["view_org_assets", "deploy_plugin"]}
    api.get(f"{API}/me", json={**ME, "organizations": [reader]})

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "Plugin developer" in result.output
    assert _git(bare, "for-each-ref") == ""


def test_deploy_commits_a_dirty_tree_after_confirmation(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At a terminal, uncommitted work is shown, committed with the given message, and pushed."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    (package / "handler.py").write_text("x = 1\n")

    result = runner.invoke(
        app, ["deploy", str(package), "--instance", "acme-staging"], input="y\nAdd handler\n"
    )

    assert result.exit_code == 0, result.output
    assert "acme__intake/handler.py" in result.output
    assert _git(bare, "log", "-1", "--format=%s", "main") == "Add handler"


def test_deploy_refuses_a_dirty_tree_without_a_terminal(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """Without a terminal, deploy never commits someone's working tree."""
    (package / "handler.py").write_text("x = 1\n")

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "uncommitted changes" in result.output
    assert _git(bare, "for-each-ref") == ""


def test_deploy_refuses_a_package_nested_deeper_in_a_repository(
    api: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """A package whose parent is not the repository root would push the whole repository."""
    monorepo = tmp_path / "monorepo"
    directory = monorepo / "plugins" / NAME
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))
    _git(monorepo, "init")

    result = runner.invoke(app, ["deploy", str(directory), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "must be rooted at the directory containing the package" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


def test_deploy_reports_a_failed_target_and_exits_nonzero(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """Each target's error is printed, and anything but success exits non-zero."""
    failed = _deployment(
        "failed",
        targets=[
            {
                "plugin": NAME,
                "instance": "acme-staging",
                "status": "failed",
                "error": "Install refused by the instance.",
                "undeclared_values": ["OLD_FLAG"],
            }
        ],
    )
    api.get(f"{API}/deployments/6f1c", json=failed)

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 1
    assert "acme-staging: failed: Install refused by the instance." in result.output
    assert "does not declare them: OLD_FLAG" in result.output
    assert f"Deploy of {NAME} failed." in result.output


def test_deploy_surfaces_a_refused_dispatch(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """A refused deployment prints platform's sentence."""
    api.post(
        f"{API}/deployments",
        status_code=400,
        json={"error": "acme-prod is not managed by this platform.", "code": "unmanaged"},
    )

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-prod"])

    assert result.exit_code == 1
    assert "acme-prod is not managed by this platform." in result.output


def test_deploy_stops_waiting_after_the_timeout(
    api: requests_mock_module.Mocker,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A deployment still running at the deadline is reported as unfinished, not as done."""
    monkeypatch.setattr(commands, "POLL_TIMEOUT_SECONDS", 0)
    api.get(f"{API}/deployments/6f1c", json=_deployment("in_progress"))

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 1
    assert "is still running" in result.output


def test_deploy_polling_rides_out_a_server_error(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """A 5xx while polling is retried rather than reported as a failed deploy."""
    api.get(
        f"{API}/deployments/6f1c",
        [{"status_code": 502, "text": "bad gateway"}, {"json": _deployment("succeeded")}],
    )

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output


# -- deploy: consent ---------------------------------------------------------


def _pending_consent() -> dict:
    deployment = _deployment("pending_consent")
    deployment["consent_requests"] = [
        {
            "id": 41,
            "status": "pending",
            "plugin": NAME,
            "namespace": "beta__reader",
            "access": "read",
            "instances": ["acme-staging"],
        }
    ]
    return deployment


def _consent_answers(mock: requests_mock_module.Mocker) -> list:
    return [r for r in mock.request_history if "/consent-requests/" in r.url]


def test_deploy_with_yes_lists_consent_and_answers_none(
    api: requests_mock_module.Mocker,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--yes never answers consent, even at a terminal: it lists the requests and exits non-zero."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    api.post(f"{API}/deployments", status_code=202, json=_pending_consent())

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging", "--yes"])

    assert result.exit_code == 1
    output = " ".join(result.output.split())
    assert "read access to the custom data namespace 'beta__reader' on acme-staging" in output
    assert "Deployment 6f1c is waiting on these requests, and --yes does not answer" in output
    assert _consent_answers(api) == []
    assert not _requests_to(api, "GET", "/deployments/6f1c")


def test_deploy_without_a_terminal_lists_consent_and_answers_none(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """With nobody at the terminal to ask, consent requests are listed and left unanswered."""
    api.post(f"{API}/deployments", status_code=202, json=_pending_consent())

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 1
    assert "there is no terminal to ask at" in result.output
    assert _consent_answers(api) == []


def test_deploy_with_yes_commits_a_dirty_tree_without_prompting(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """--yes commits uncommitted work with the default message, with no terminal to prompt at."""
    (package / "handler.py").write_text("x = 1\n")

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging", "--yes"])

    assert result.exit_code == 0, result.output
    assert "Commit these and deploy?" not in result.output
    assert _git(bare, "log", "-1", "--format=%s", "main") == git.DEFAULT_COMMIT_MESSAGE


def test_deploy_approves_consent_interactively(
    api: requests_mock_module.Mocker,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At a terminal, an approved request is approved and the deployment followed to its outcome."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    api.post(f"{API}/deployments", status_code=202, json=_pending_consent())
    api.post(f"{API}/consent-requests/41/approve", json={})

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"], input="y\n")

    assert result.exit_code == 0, result.output
    assert _requests_to(api, "POST", "/consent-requests/41/approve")
    assert f"Deploy of {NAME} succeeded." in result.output


def test_deploy_denies_consent_interactively(
    api: requests_mock_module.Mocker,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Declining a request denies it with the reason given and ends the deploy."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    api.post(f"{API}/deployments", status_code=202, json=_pending_consent())
    api.post(f"{API}/consent-requests/41/deny", json={})

    result = runner.invoke(
        app, ["deploy", str(package), "--instance", "acme-staging"], input="n\nnot yet\n"
    )

    assert result.exit_code == 1
    assert _requests_to(api, "POST", "/consent-requests/41/deny")[0].json() == {"reason": "not yet"}
    assert "cancelled because a consent request was denied" in result.output


# -- git credential helper ---------------------------------------------------


def test_git_credential_mints_a_token_for_the_repository_in_the_request(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """`get` derives the plugin from the repository path and prints git's credential fields."""
    requests_mock.post(
        f"{API}/plugins/{NAME}/git-credentials",
        json={"username": "dana", "password": "cnvs_git_1", "expires_at": "2026-10-01T13:00:00Z"},
    )

    result = runner.invoke(
        app,
        ["git-credential", "--platform", PLATFORM, "get"],
        input=f"protocol=https\nhost=git.platform.example\npath=acme/{NAME}.git\n\n",
    )

    assert result.exit_code == 0, result.output
    assert result.output.splitlines() == [
        "username=dana",
        "password=cnvs_git_1",
        "password_expiry_utc=1790859600",
    ]


def test_git_credential_without_a_path_names_the_setting(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A request without the repository path names `credential.useHttpPath` and mints nothing."""
    result = runner.invoke(
        app, ["git-credential", "get"], input="protocol=https\nhost=git.platform.example\n\n"
    )

    assert result.exit_code == 1
    assert "credential.useHttpPath" in result.output
    assert not requests_mock.called


def test_git_credential_store_and_erase_do_nothing(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """Tokens are short-lived, so `store` and `erase` have nothing to do."""
    for operation in ("store", "erase"):
        result = runner.invoke(app, ["git-credential", operation], input="path=a/b.git\n\n")
        assert result.exit_code == 0
        assert result.output == ""
    assert not requests_mock.called


def test_git_credential_refusal_goes_to_stderr_and_fails(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A refused mint prints platform's sentence for git to show and emits no credential."""
    requests_mock.post(
        f"{API}/plugins/{NAME}/git-credentials", status_code=404, json={"error": "No such plugin."}
    )

    result = runner.invoke(app, ["git-credential", "get"], input=f"path=acme/{NAME}.git\n\n")

    assert result.exit_code == 1
    assert "canvas: No such plugin." in result.output
    assert "password=" not in result.output


def test_plugin_from_repo_path() -> None:
    """The plugin is the last path segment without `.git`, with or without a leading slash."""
    assert commands.plugin_from_repo_path(f"acme/{NAME}.git") == NAME
    assert commands.plugin_from_repo_path(f"/git/acme/{NAME}.git") == NAME


# -- config and uninstall ----------------------------------------------------


@pytest.fixture
def managed_plugin(requests_mock: requests_mock_module.Mocker, signed_in: None) -> Iterator[None]:
    """A plugin platform manages, installed on acme-staging, and a configure that succeeds."""
    requests_mock.get(
        f"{API}/plugins/{NAME}",
        json={
            "name": NAME,
            "publisher": "acme",
            "installs": [{"instance": "acme-staging", "sha": "3f2a", "enabled": True}],
        },
    )
    requests_mock.get(
        f"{API}/instances",
        json={
            "instances": [
                _instance("acme-staging", "configure_plugin"),
                _instance("acme-prod", "configure_plugin"),
            ]
        },
    )
    requests_mock.post(
        f"{API}/deployments", status_code=202, json=_deployment("in_progress", action="configure")
    )
    requests_mock.get(f"{API}/deployments/6f1c", json=_deployment("succeeded", action="configure"))
    yield


def test_config_set_on_a_managed_plugin_stores_values_then_configures(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """Values go to platform, sensitivity only where a flag states it, then a configure
    deployment targets the one configurable instance the plugin is installed on.
    """
    variables = f"{API}/instances/acme-staging/plugins/{NAME}/variables"
    requests_mock.put(f"{variables}/API_URL", json={})
    requests_mock.put(f"{variables}/API_KEY", json={})
    requests_mock.put(f"{variables}/DEBUG", json={})

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            NAME,
            "API_URL=https://api.acme.example",
            "--secret",
            "API_KEY=s3cret",
            "--variable",
            "DEBUG=1",
        ],
    )

    assert result.exit_code == 0, result.output
    bodies = {
        r.url.rsplit("/", 1)[-1]: r.json()
        for r in requests_mock.request_history
        if r.method == "PUT"
    }
    assert bodies == {
        "API_URL": {"value": "https://api.acme.example"},
        "API_KEY": {"value": "s3cret", "sensitive": True},
        "DEBUG": {"value": "1", "sensitive": False},
    }
    assert _requests_to(requests_mock, "POST", "/deployments")[0].json() == {
        "action": "configure",
        "plugins": [{"name": NAME}],
        "instances": ["acme-staging"],
    }


def test_config_unset_on_a_managed_plugin_clears_values_then_configures(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """Each key is cleared on each --instance, then a configure deployment runs."""
    for slug in ("acme-staging", "acme-prod"):
        requests_mock.delete(
            f"{API}/instances/{slug}/plugins/{NAME}/variables/API_KEY", status_code=204
        )

    result = runner.invoke(
        app,
        [
            "config",
            "unset",
            NAME,
            "API_KEY",
            "--instance",
            "acme-staging",
            "--instance",
            "acme-prod",
        ],
    )

    assert result.exit_code == 0, result.output
    assert len([r for r in requests_mock.request_history if r.method == "DELETE"]) == 2
    assert _requests_to(requests_mock, "POST", "/deployments")[0].json()["instances"] == [
        "acme-staging",
        "acme-prod",
    ]


def test_config_set_on_a_managed_plugin_refuses_host(managed_plugin: None) -> None:
    """--host names an instance directly, which a platform-managed plugin does not accept."""
    result = runner.invoke(app, ["config", "set", NAME, "A=1", "--host", "acme-staging"])

    assert result.exit_code == 2
    assert "--instance" in result.output


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_set_on_an_unmanaged_plugin_writes_each_instance_directly(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plugin platform does not have is configured on each named instance directly."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    result = runner.invoke(
        app, ["config", "set", NAME, "A=1", "--instance", "one", "--instance", "two"]
    )

    assert result.exit_code == 0, result.output
    assert [c.kwargs["host"] for c in mock_update.call_args_list] == [
        "https://one.canvasmedical.com",
        "https://two.canvasmedical.com",
    ]
    assert mock_update.call_args.kwargs["secrets"] == ["A=1"]


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_on_an_unprefixed_plugin_never_asks_platform(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A name platform could never hold goes straight to the instance."""
    result = runner.invoke(app, ["config", "unset", "intake", "A", "--host", "https://x.example"])

    assert result.exit_code == 0, result.output
    assert not requests_mock.called
    assert mock_update.call_args.kwargs == {
        "name": "intake",
        "package_path": None,
        "is_enabled": None,
        "secrets": ["A="],
        "host": "https://x.example",
    }


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_signed_out_goes_to_the_instance(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker
) -> None:
    """Without a platform session, config writes the instance directly."""
    result = runner.invoke(app, ["config", "set", NAME, "A=1", "--host", "https://x.example"])

    assert result.exit_code == 0, result.output
    assert not requests_mock.called
    mock_update.assert_called_once()


def test_uninstall_of_a_managed_plugin_requires_an_instance(managed_plugin: None) -> None:
    """Without --instance, uninstall names where the plugin is installed and does nothing."""
    result = runner.invoke(app, ["uninstall", NAME])

    assert result.exit_code == 2
    assert "installed on: acme-staging" in result.output


def test_uninstall_of_a_managed_plugin_dispatches_an_uninstall(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """An uninstall deployment targets each --instance."""
    requests_mock.post(
        f"{API}/deployments", status_code=202, json=_deployment("in_progress", action="uninstall")
    )

    result = runner.invoke(app, ["uninstall", NAME, "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _requests_to(requests_mock, "POST", "/deployments")[0].json() == {
        "action": "uninstall",
        "plugins": [{"name": NAME}],
        "instances": ["acme-staging"],
    }


@patch("canvas_cli.apps.platform.commands.instance_plugin.uninstall")
def test_uninstall_of_an_unmanaged_plugin_goes_to_the_instance(
    mock_uninstall: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plugin platform does not have is uninstalled from the instance directly, --force included."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["uninstall", NAME, "--host", "https://x.example", "--force"])

    assert result.exit_code == 0, result.output
    mock_uninstall.assert_called_once_with(name=NAME, force=True, host="https://x.example")


def test_direct_instance_refusal_for_a_platform_managed_plugin_names_canvas_deploy(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """When an instance refuses a CLI change to a plugin platform deploys, the message points
    at `canvas deploy` rather than echoing the instance's wording.
    """
    requests_mock.delete(
        "https://x.example/plugin-io/plugins/intake/",
        status_code=403,
        json={
            "error": "Plugin 'intake' is managed elsewhere.",
            "error_code": "control_room_managed",
        },
    )

    with patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token", return_value="tok"):
        result = runner.invoke(app, ["uninstall", "intake", "--host", "https://x.example"])

    assert result.exit_code == 1
    assert "`canvas deploy`" in result.output
    assert "managed elsewhere" not in result.output


# -- clone -------------------------------------------------------------------


def test_clone_checks_out_the_repository_ready_to_push(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    package: Path,
    tmp_path: Path,
) -> None:
    """Clone fetches the plugin's repository and leaves origin and the credential helper set."""
    _git(package, "push", bare.as_uri(), "HEAD:main")
    requests_mock.get(f"{API}/plugins/{NAME}", json={"name": NAME, "git_url": bare.as_uri()})
    destination = tmp_path / "elsewhere"

    result = runner.invoke(app, ["clone", NAME, str(destination)])

    assert result.exit_code == 0, result.output
    assert (destination / NAME / "CANVAS_MANIFEST.json").exists()
    assert _git(destination, "remote", "get-url", "origin") == bare.as_uri()
    assert _git(destination, "config", "credential.file://.useHttpPath") == "true"
    helpers = _helpers(destination)
    assert helpers[0] == ""
    assert "git-credential --platform" in helpers[1]
    assert f"canvas deploy {destination / NAME}" in result.output


def test_clone_of_an_unknown_plugin(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plugin platform does not show the person is refused by name."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["clone", NAME])

    assert result.exit_code == 2
    assert "no plugin named" in result.output


# -- init --------------------------------------------------------------------


def test_init_signed_out_keeps_the_given_name(
    requests_mock: requests_mock_module.Mocker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Signed out, the package is named from the project name alone and nothing is registered."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="Intake Forms\n")

    assert result.exit_code == 0, result.output
    manifest_path = tmp_path / "intake-forms" / "intake_forms" / "CANVAS_MANIFEST.json"
    assert json.loads(manifest_path.read_text())["name"] == "intake_forms"
    assert not requests_mock.called


def test_init_signed_in_prefixes_registers_and_connects_git(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Signed in, the package is `<prefix>__<package>`, registered, and its repository's
    origin is platform.
    """
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)
    requests_mock.post(
        f"{API}/orgs/acme/plugins",
        status_code=201,
        json={"name": "acme__intake_forms", "git_url": bare.as_uri()},
    )

    result = runner.invoke(app, ["init"], input="Intake Forms\n")

    assert result.exit_code == 0, result.output
    project = tmp_path / "intake-forms"
    package_dir = project / "acme__intake_forms"
    manifest = json.loads((package_dir / "CANVAS_MANIFEST.json").read_text())
    assert manifest["name"] == "acme__intake_forms"
    assert manifest["components"]["handlers"][0]["class"].startswith("acme__intake_forms.handlers.")
    assert _requests_to(requests_mock, "POST", "/orgs/acme/plugins")[0].json() == {
        "name": "acme__intake_forms"
    }
    assert _git(project, "remote", "get-url", "origin") == bare.as_uri()


def test_init_asks_which_organization_when_there_are_several(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With several organizations to publish in, the person picks one by number."""
    monkeypatch.chdir(tmp_path)
    second = {
        **ACME,
        "slug": "big-leap",
        "name": "Big Leap",
        "plugin_prefix": "big_leap",
    }
    requests_mock.get(f"{API}/me", json={**ME, "organizations": [ACME, second]})
    requests_mock.post(
        f"{API}/orgs/big-leap/plugins", status_code=201, json={"git_url": bare.as_uri()}
    )

    result = runner.invoke(app, ["init"], input="2\nIntake\n")

    assert result.exit_code == 0, result.output
    assert (tmp_path / "intake" / "big_leap__intake" / "CANVAS_MANIFEST.json").exists()


def test_init_org_option_must_be_one_the_person_can_publish_in(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--org naming an organization the person cannot publish in is refused before scaffolding."""
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["init", "--org", "beta"])

    assert result.exit_code == 2
    assert "Choose from: acme" in result.output
    assert not [path for path in tmp_path.iterdir() if path.is_dir()]


# -- logout ------------------------------------------------------------------


def test_logout_says_a_service_account_token_still_signs_commands_in(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Logout under CANVAS_PLATFORM_TOKEN succeeds and says the token still applies."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")

    result = runner.invoke(app, ["logout", "--platform", PLATFORM])

    assert result.exit_code == 0
    assert f"You were not signed in to {PLATFORM}." in result.output
    assert "CANVAS_PLATFORM_TOKEN is set, so commands still act as its service account" in (
        result.output
    )
    assert not requests_mock.called


# -- registration ------------------------------------------------------------


def test_platform_commands_are_registered_and_say_platform() -> None:
    """Every platform command is registered, and no help text names an internal service."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("login", "logout", "deploy", "clone", "init", "uninstall"):
        assert f"  {command} " in result.output
    assert "cr-init" not in result.output

    for args in (["deploy", "--help"], ["config", "set", "--help"], ["login", "--help"]):
        text = runner.invoke(app, args).output
        assert "Control Room" not in text
        assert "--repo-name" not in text


def test_config_on_an_instance_without_the_plugin_says_the_values_wait(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """A configure target skipped because the plugin is not installed says when the values apply."""
    requests_mock.put(f"{API}/instances/acme-prod/plugins/{NAME}/variables/A", json={})
    skipped = _deployment(
        "succeeded",
        action="configure",
        targets=[{"plugin": NAME, "instance": "acme-prod", "status": "skipped", "error": ""}],
    )
    requests_mock.get(f"{API}/deployments/6f1c", json=skipped)

    result = runner.invoke(app, ["config", "set", NAME, "A=1", "--instance", "acme-prod"])

    assert result.exit_code == 0, result.output
    assert "acme-prod: skipped (not installed there; the stored values apply" in result.output


def test_git_runs_the_credential_helper_with_the_repository_path(
    tmp_path: Path, package: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real git, configured the way deploy configures a repository, runs `canvas git-credential`
    with the repository path, and the helper answers with a token minted by platform.
    """
    canvas = Path(sys.executable).parent / "canvas"
    if not canvas.exists():
        pytest.skip("the canvas entry point is not installed beside this interpreter")

    minted: list[tuple[str, str]] = []

    class FakePlatform(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            minted.append((self.path, self.headers["Authorization"]))
            body = json.dumps({"username": "dana", "password": "cnvs_git_1"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            """Keep the request log out of the test output."""

    server = HTTPServer(("127.0.0.1", 0), FakePlatform)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    platform = f"http://127.0.0.1:{server.server_address[1]}"
    home = tmp_path / "home"
    (home / ".canvas").mkdir(parents=True)
    tokens = {"access_token": "cnvs_ua_9", "refresh_token": "cnvs_rt_9", "expires_at": 4102444800}
    (home / ".canvas" / "platform-credentials.json").write_text(
        json.dumps({"default": platform, "platforms": {platform: tokens}})
    )
    git_url = f"https://git.platform.example/acme/{NAME}.git"
    monkeypatch.setattr(sys, "argv", [str(canvas)])
    for key, value in git.credential_config(git_url, platform):
        _git(package, "config", key, value)

    try:
        result = subprocess.run(
            ["git", "-C", str(package), "credential", "fill"],
            input=f"protocol=https\nhost=git.platform.example\npath=acme/{NAME}.git\n\n",
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(home), "GIT_CONFIG_GLOBAL": os.devnull},
            timeout=60,
        )
    finally:
        server.shutdown()

    assert result.returncode == 0, result.stderr
    assert "password=cnvs_git_1" in result.stdout.splitlines()
    assert minted == [(f"/api/v1/plugins/{NAME}/git-credentials", "Bearer cnvs_ua_9")]


# -- manifest names ----------------------------------------------------------


def test_manifest_name_requires_a_manifest(tmp_path: Path) -> None:
    """A directory without CANVAS_MANIFEST.json is refused by name."""
    with pytest.raises(typer.BadParameter, match="has no CANVAS_MANIFEST.json"):
        commands.manifest_name(tmp_path)


def test_manifest_name_reports_an_unreadable_manifest(tmp_path: Path) -> None:
    """A manifest that is not JSON names the file."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text("{not json")

    with pytest.raises(typer.BadParameter, match="Could not read"):
        commands.manifest_name(tmp_path)


def test_manifest_name_requires_a_name(tmp_path: Path) -> None:
    """A manifest without a `name` is refused."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text(json.dumps({"description": "x"}))

    with pytest.raises(typer.BadParameter, match='is missing a "name"'):
        commands.manifest_name(tmp_path)


def test_package_dir_is_the_project_when_the_manifest_sits_at_its_root(tmp_path: Path) -> None:
    """A template that puts the manifest at the project root has the project as its package."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))

    assert commands._package_dir(tmp_path) == tmp_path


# -- deploy: more paths ------------------------------------------------------


def test_deploy_refuses_a_path_that_is_not_a_directory(signed_in: None, tmp_path: Path) -> None:
    """A file or missing path is refused before platform is called."""
    result = runner.invoke(app, ["deploy", str(tmp_path / "missing")])

    assert result.exit_code == 2
    assert "needs to be a valid directory" in result.output


def test_deploy_with_no_deployable_instance_says_to_name_one(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """Without --instance and with no managed instance to deploy to, the person is told to name one."""
    api.get(
        f"{API}/instances",
        json={"instances": [_instance("acme-old", "deploy_plugin", managed=False)]},
    )

    result = runner.invoke(app, ["deploy", str(package)])

    assert result.exit_code == 2
    assert (
        "There is no instance Canvas Platform manages that you can deploy plugins to"
        in result.output
    )
    assert not _requests_to(api, "POST", "/deployments")


def test_canvas_employee_deploys_a_plugin_under_its_existing_publisher(
    requests_mock: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """A Canvas employee outside the plugin's organization deploys it as its existing publisher."""
    directory = tmp_path / "other__intake"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "other__intake"}))
    requests_mock.get(f"{API}/me", json={**ME, "canvas_employee": True})
    requests_mock.get(
        f"{API}/plugins/other__intake", json={"name": "other__intake", "publisher": "other"}
    )
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("succeeded"))

    result = runner.invoke(
        app, ["deploy", str(directory), "--no-push", "--instance", "other-staging"]
    )

    assert result.exit_code == 0, result.output
    assert _requests_to(requests_mock, "POST", "/deployments")[0].json()["instances"] == [
        "other-staging"
    ]


def test_deploy_waits_through_consent_another_person_already_answered(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """A deployment pending consent with no request left to answer is waited on, not prompted."""
    api.post(
        f"{API}/deployments",
        status_code=202,
        json={
            **_deployment("pending_consent"),
            "consent_requests": [{"id": 7, "status": "approved"}],
        },
    )

    result = runner.invoke(app, ["deploy", str(package), "--no-push", "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert "needs consent" not in result.output
    assert f"Deploy of {NAME} succeeded." in result.output


def test_deploy_stops_polling_when_platform_refuses_the_status_request(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """A client error while polling ends the command rather than being retried."""
    api.post(f"{API}/deployments", status_code=202, json=_deployment("in_progress"))
    api.get(f"{API}/deployments/6f1c", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["deploy", str(package), "--no-push", "--instance", "acme-staging"])

    assert result.exit_code != 0
    assert len(_requests_to(api, "GET", "/deployments/6f1c")) == 1


# -- login and logout --------------------------------------------------------


def test_login_lists_each_organization_and_its_prefix(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After the browser sign-in, login names the account and each organization's prefix."""

    def fake_login(url: str) -> None:
        auth.save_tokens(
            url,
            {"access_token": "cnvs_ua_1", "refresh_token": "cnvs_rt_1", "expires_in": 3600},
            make_default=True,
        )

    monkeypatch.setattr(auth, "login", fake_login)
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["login", "--platform", PLATFORM])

    assert result.exit_code == 0, result.output
    assert f"Signed in to {PLATFORM} as dana@acme.example." in result.output
    assert "Acme Health (acme): plugin prefix acme__" in result.output


def test_logout_revokes_the_session(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Logout with a session revokes it and says so."""
    requests_mock.post(f"{PLATFORM}/oauth/revoke", status_code=200)

    result = runner.invoke(app, ["logout", "--platform", PLATFORM])

    assert result.exit_code == 0, result.output
    assert f"Signed out of {PLATFORM}." in result.output
    assert "CANVAS_PLATFORM_TOKEN" not in result.output


def test_logout_says_when_revoking_failed(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A revocation platform refuses is reported, and the machine is still signed out."""
    requests_mock.post(f"{PLATFORM}/oauth/revoke", status_code=503)

    result = runner.invoke(app, ["logout", "--platform", PLATFORM])

    assert result.exit_code == 0, result.output
    assert "revoking the session failed: platform answered 503" in result.output
    assert auth.stored_tokens(PLATFORM) is None


# -- clone and init: more paths ----------------------------------------------


def test_clone_refuses_an_existing_destination(
    requests_mock: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """A destination that already exists is refused before git runs."""
    requests_mock.get(
        f"{API}/plugins/{NAME}", json={"name": NAME, "publisher": "acme", "git_url": "file:///x"}
    )

    result = runner.invoke(app, ["clone", NAME, str(tmp_path)])

    assert result.exit_code == 2
    assert "already exists" in result.output


def test_init_org_option_picks_that_organization(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--org names the publisher without a prompt, among several organizations."""
    monkeypatch.chdir(tmp_path)
    second = {**ACME, "slug": "big-leap", "name": "Big Leap", "plugin_prefix": "big_leap"}
    requests_mock.get(f"{API}/me", json={**ME, "organizations": [ACME, second]})
    requests_mock.post(
        f"{API}/orgs/big-leap/plugins", status_code=201, json={"git_url": bare.as_uri()}
    )

    result = runner.invoke(app, ["init", "--org", "big-leap"], input="Intake\n")

    assert result.exit_code == 0, result.output
    assert "Which organization" not in result.output
    assert (tmp_path / "intake" / "big_leap__intake" / "CANVAS_MANIFEST.json").exists()


def test_init_without_a_publishing_organization_scaffolds_unprefixed(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Signed in without the right to push code anywhere, init scaffolds without a prefix and
    registers nothing.
    """
    monkeypatch.chdir(tmp_path)
    viewer = {**ACME, "capabilities": ["view_org_assets"]}
    requests_mock.get(f"{API}/me", json={**ME, "organizations": [viewer]})

    result = runner.invoke(app, ["init"], input="Intake\n")

    assert result.exit_code == 0, result.output
    assert "scaffolded without a publisher prefix" in result.output
    assert (tmp_path / "intake" / "intake" / "CANVAS_MANIFEST.json").exists()
    assert not _requests_to(requests_mock, "POST", "/orgs/acme/plugins")


def test_init_refuses_a_scaffolded_name_platform_would_reject(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A project name that yields an invalid plugin name is refused before registering."""
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["init"], input="1 Intake\n")

    assert result.exit_code == 2
    assert "is not a valid plugin name" in result.output
    assert not _requests_to(requests_mock, "POST", "/orgs/acme/plugins")


def test_init_reports_a_failed_git_init(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A git init that fails names git's own error."""
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)
    requests_mock.post(f"{API}/orgs/acme/plugins", status_code=201, json={"git_url": bare.as_uri()})
    monkeypatch.setattr(
        git,
        "run",
        lambda directory, *args: subprocess.CompletedProcess(args, 1, "", "permission denied\n"),
    )

    result = runner.invoke(app, ["init"], input="Intake\n")

    assert result.exit_code == 1
    assert "git init failed: permission denied" in result.output


# -- config: argument checks -------------------------------------------------


def test_config_refuses_both_instance_and_host(requests_mock: requests_mock_module.Mocker) -> None:
    """Signed out, --instance and --host together are refused."""
    result = runner.invoke(
        app, ["config", "set", NAME, "A=1", "--instance", "one", "--host", "https://x.example"]
    )

    assert result.exit_code == 2
    assert "either --instance or --host" in result.output


def test_config_set_refuses_a_value_without_a_key(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """A value with no `=` is refused before anything is written."""
    result = runner.invoke(app, ["config", "set", NAME, "--secret", "nokey"])

    assert result.exit_code == 2
    assert "Invalid variable format: 'nokey'" in result.output
    assert not requests_mock.called


def test_config_set_requires_a_variable(requests_mock: requests_mock_module.Mocker) -> None:
    """Config set with no variables is refused."""
    result = runner.invoke(app, ["config", "set", NAME])

    assert result.exit_code == 2
    assert "Provide at least one variable" in result.output


def test_init_application_registers_without_creating_a_repository(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The application template puts the manifest at the project root, so the project is the
    package: it is registered, but no repository is created around it.
    """
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)
    requests_mock.post(f"{API}/orgs/acme/plugins", status_code=201, json={"git_url": bare.as_uri()})

    result = runner.invoke(app, ["init", "application"], input="Intake App\n")

    assert result.exit_code == 0, result.output
    package_dir = tmp_path / "acme__intake_app"
    assert json.loads((package_dir / "CANVAS_MANIFEST.json").read_text())["name"] == (
        "acme__intake_app"
    )
    assert _requests_to(requests_mock, "POST", "/orgs/acme/plugins")[0].json() == {
        "name": "acme__intake_app"
    }
    assert "Initialized a git repository" not in result.output
    assert not (package_dir / ".git").exists()
    assert f"canvas deploy {package_dir}" in result.output


# -- init: signed out says so ------------------------------------------------


def test_init_signed_out_says_the_plugin_cannot_be_deployed_yet(
    requests_mock: requests_mock_module.Mocker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Signed out, init names the platform it checked and says how to get a deployable plugin."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="Intake Forms\n")

    assert result.exit_code == 0, result.output
    assert f"not signed in to Canvas Platform at {auth.DEFAULT_PLATFORM_URL}" in result.output
    assert "run `canvas login`, then `canvas init` again" in result.output
    assert not requests_mock.called


# -- deploy: the package folder matches the name -----------------------------


@patch("subprocess.run")
def test_deploy_refuses_a_folder_not_named_after_the_plugin_before_any_git_or_network(
    mock_run: Mock,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A package folder that differs from the manifest name is refused before git or platform,
    since platform refuses the push anyway.
    """
    directory = tmp_path / "project" / "intake"
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))

    result = runner.invoke(app, ["deploy", str(directory), "--push-only"])

    assert result.exit_code == 2
    assert f"The package folder is 'intake', but the manifest name is '{NAME}'" in result.output
    assert f"Rename the folder to '{NAME}'" in result.output
    mock_run.assert_not_called()
    assert not requests_mock.called


def test_deploy_accepts_the_package_folder_given_as_dot(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`canvas deploy .` from inside the package checks the folder's real name."""
    monkeypatch.chdir(package)

    result = runner.invoke(app, ["deploy", ".", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", "main") == _git(package, "rev-parse", "HEAD")


def test_deploy_ref_skips_the_folder_check(
    api: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """Deploying a ref that is already pushed reads only the manifest name, not the folder."""
    directory = tmp_path / "checkout"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))

    result = runner.invoke(
        app, ["deploy", str(directory), "--ref", "v1.0.0", "--instance", "acme-staging"]
    )

    assert result.exit_code == 0, result.output


# -- deploy: a refused push is not a usage mistake ---------------------------


def test_deploy_reports_a_refused_push_without_the_usage_line(
    api: requests_mock_module.Mocker, bare: Path, package: Path, signed_in: None
) -> None:
    """When platform's git server refuses the push, its reason is shown with no usage text."""
    hook = bare / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho 'Refused refs/heads/main: listing is invalid' >&2\nexit 1\n")
    hook.chmod(0o755)

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 1
    assert "git push to Canvas Platform failed" in result.output
    assert "listing is invalid" in result.output
    assert "Usage:" not in result.output


# -- whoami ------------------------------------------------------------------


def test_whoami_signed_out_names_the_platform_and_says_to_log_in(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """Signed out, whoami says which platform it checked, why, and exits non-zero."""
    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 1
    assert f"Platform: {auth.DEFAULT_PLATFORM_URL} (from the default)" in result.output
    assert "Not signed in. Run `canvas login`." in result.output
    assert not requests_mock.called


def test_whoami_shows_the_session_and_what_each_organization_allows(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Signed in, whoami names the account, the credential's source and each organization's
    prefix and capabilities, and never prints the token.
    """
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0, result.output
    assert f"Platform: {PLATFORM} (from your last `canvas login`)" in result.output
    assert "Signed in as dana@acme.example (browser session from `canvas login`)" in result.output
    assert (
        "Acme Health (acme): plugin prefix acme__, can push, deploy, configure, uninstall"
        in result.output
    )
    assert "cnvs_" not in result.output


def test_whoami_names_the_environment_variable_that_chose_the_platform(
    requests_mock: requests_mock_module.Mocker, signed_in: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A platform chosen by CANVAS_PLATFORM_URL says so."""
    monkeypatch.setenv(auth.PLATFORM_URL_ENV, PLATFORM)
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0, result.output
    assert f"Platform: {PLATFORM} (from {auth.PLATFORM_URL_ENV})" in result.output


def test_whoami_says_a_service_account_token_outranks_a_stored_session(
    requests_mock: requests_mock_module.Mocker, signed_in: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With CANVAS_PLATFORM_TOKEN set, whoami calls platform with it, says it wins over the
    stored session, and does not print it.
    """
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_secret")
    requests_mock.get(f"{API}/me", json={**ME, "email": "ci@acme.example", "organizations": [ACME]})

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0, result.output
    me_request = _requests_to(requests_mock, "GET", "/me")[0]
    assert me_request.headers["Authorization"] == "Bearer cnvs_sa_secret"
    assert (
        f"Signed in as ci@acme.example (service account token from {auth.SERVICE_TOKEN_ENV})"
        in result.output
    )
    assert f"{auth.SERVICE_TOKEN_ENV} takes precedence while it is set" in result.output
    assert "cnvs_sa_secret" not in result.output


def test_whoami_reports_a_revoked_service_account_token(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A token platform no longer accepts is reported, not shown as signed in."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_revoked")
    requests_mock.get(f"{API}/me", status_code=401)
    monkeypatch.setenv(auth.PLATFORM_URL_ENV, PLATFORM)

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 1
    assert "did not accept CANVAS_PLATFORM_TOKEN" in result.output
    assert "Signed in as" not in result.output


def test_whoami_platform_option_suggests_logging_in_there(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """With --platform, the login hint names that platform."""
    result = runner.invoke(app, ["whoami", "--platform", PLATFORM])

    assert result.exit_code == 1
    assert f"Platform: {PLATFORM} (from --platform)" in result.output
    assert f"Run `canvas login --platform {PLATFORM}`." in result.output
