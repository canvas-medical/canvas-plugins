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
# For asserting what goes to stderr, where diagnostics belong so a piped log keeps their order.
split_runner = CliRunner(mix_stderr=False)
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


BIG_LEAP: dict[str, Any] = {
    **ACME,
    "slug": "big-leap",
    "name": "Big Leap",
    "plugin_prefix": "big_leap",
}


def _plain_package(tmp_path: Path, manifest: str | None = None, name: str = "intake") -> Path:
    """A committed package named ``name`` with no org prefix, at ``<repo>/<name>``."""
    repo = tmp_path / "plain"
    directory = repo / name
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(
        manifest if manifest is not None else json.dumps({"name": name})
    )
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "add", name)
    _git(repo, "commit", "-m", "first")
    return directory


def test_deploy_accepts_a_plain_name(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """A package name needs no org prefix; the publisher is the one organization."""
    package = _plain_package(tmp_path)

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    head = _git(package, "rev-parse", "HEAD")
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": "intake", "ref": head, "publisher": "acme"}
    ]
    assert "Publishing as acme, the only organization you can publish in." in result.output


@pytest.mark.parametrize("name", ["Intake", "1abc", "a" * 64])
@patch("subprocess.run")
def test_deploy_refuses_an_invalid_name_before_any_git_or_network(
    mock_run: Mock,
    name: str,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A name that is not a Python package and a Postgres identifier is refused up front."""
    directory = tmp_path / name
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": name}))

    result = runner.invoke(app, ["deploy", str(directory), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "at most 63 characters" in result.output
    assert "starts with a lowercase letter" in result.output
    mock_run.assert_not_called()
    assert not requests_mock.called


def test_deploy_uses_the_manifest_publisher(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None, bare: Path
) -> None:
    """A manifest publisher picks the org without a prompt, among several."""
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, BIG_LEAP]})
    api.post(
        f"{API}/orgs/big-leap/plugins",
        status_code=201,
        json={
            "name": "intake",
            "publisher": "big-leap",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "big-leap"}))

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 0, result.output
    assert "Which organization" not in result.output
    assert _requests_to(api, "POST", "/orgs/big-leap/plugins")
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


def test_deploy_entry_carries_the_manifest_publisher(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None, bare: Path
) -> None:
    """The deployment entry names the publisher the manifest chose."""
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, BIG_LEAP]})
    api.post(
        f"{API}/orgs/big-leap/plugins",
        status_code=201,
        json={
            "name": "intake",
            "publisher": "big-leap",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "big-leap"}))

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    plugins = _requests_to(api, "POST", "/deployments")[0].json()["plugins"]
    assert plugins[0]["publisher"] == "big-leap"


def test_deploy_refuses_a_manifest_publisher_you_do_not_belong_to(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """A forged publisher is refused before any push, because the CLI trusts only me()."""
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "globex"}))

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "names publisher 'globex', which is not an organization you belong to" in result.output
    assert "Your organizations: acme." in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")
    assert not any("/orgs/" in r.url for r in api.request_history if r.method == "POST")


def test_deploy_names_no_organization_when_the_person_has_none(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """With no membership there is no publisher to choose, and the refusal says so."""
    api.get(f"{API}/me", json={**ME, "organizations": []})
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "globex"}))

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "You do not belong to any organization on Canvas Platform." in result.output


def test_deploy_refuses_a_manifest_publisher_without_push_role(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """Pushing needs the Plugin developer role in the org the manifest names."""
    reader = {**ACME, "capabilities": ["view_org_assets", "deploy_plugin"]}
    api.get(f"{API}/me", json={**ME, "organizations": [reader]})
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "acme"}))

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "Plugin developer" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


def test_deploy_without_push_role_anywhere_names_the_missing_role(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """With no publisher in the manifest and no org that can push, the refusal names the role."""
    reader = {**ACME, "capabilities": ["view_org_assets", "deploy_plugin"]}
    api.get(f"{API}/me", json={**ME, "organizations": [reader]})
    package = _plain_package(tmp_path)

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "Plugin developer" in result.output


def test_deploy_without_push_role_names_every_organization(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """Each organization the person belongs to lacks the role, so the refusal names them all."""
    reader = {**ACME, "capabilities": ["view_org_assets", "deploy_plugin"]}
    api.get(
        f"{API}/me",
        json={
            **ME,
            "organizations": [reader, {**BIG_LEAP, "capabilities": reader["capabilities"]}],
        },
    )
    package = _plain_package(tmp_path)

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "Acme" in result.output
    assert "Big Leap" in result.output
    assert "Plugin developer" in result.output


def test_deploy_without_any_organization_says_so(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """With no organization there is no publisher to deploy as, so nothing is registered."""
    api.get(f"{API}/me", json={**ME, "organizations": []})
    package = _plain_package(tmp_path)

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "You do not belong to any organization on Canvas Platform." in result.output
    assert not _requests_to(api, "POST", "/plugins")


def test_deploy_with_one_org_leaves_the_manifest_alone(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """The only organization is used without rewriting the person's manifest."""
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before


def test_deploy_with_several_orgs_prompts_and_records_the_choice(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At a terminal the choice is asked once and recorded in the manifest that gets pushed."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, BIG_LEAP]})
    api.post(
        f"{API}/orgs/big-leap/plugins",
        status_code=201,
        json={
            "name": "intake",
            "publisher": "big-leap",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    package = _plain_package(tmp_path)

    result = runner.invoke(
        app,
        ["deploy", str(package), "--instance", "acme-staging"],
        input="2\ny\nRecord publisher\n",
    )

    assert result.exit_code == 0, result.output
    manifest: dict[str, Any] = json.loads((package / "CANVAS_MANIFEST.json").read_text())
    assert list(manifest) == ["name", "publisher"]
    assert manifest["publisher"] == "big-leap"
    assert "CANVAS_MANIFEST.json now names big-leap as the publisher." in result.output
    pushed = json.loads(_git(bare, "show", "main:intake/CANVAS_MANIFEST.json"))
    assert pushed["publisher"] == "big-leap"


def test_deploy_with_several_orgs_without_a_terminal_lists_them(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """With no terminal to ask at, the refusal lists the orgs and names the manifest key."""
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, BIG_LEAP]})
    package = _plain_package(tmp_path)

    result = runner.invoke(app, ["deploy", str(package), "--push-only"])

    assert result.exit_code == 2
    assert "You can publish in several organizations: acme, big-leap." in result.output
    assert '"publisher"' in result.output
    assert not any("/orgs/" in r.url for r in api.request_history if r.method == "POST")


def test_snapshot_deploy_with_several_orgs_does_not_write_the_manifest(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A snapshot publishes committed content, so the choice is printed as a hint, not written."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, BIG_LEAP]})
    api.post(
        f"{API}/orgs/big-leap/plugins",
        status_code=201,
        json={
            "name": "intake",
            "publisher": "big-leap",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()

    result = runner.invoke(app, ["deploy", str(package), "--snapshot", "--push-only"], input="2\n")

    assert result.exit_code == 0, result.output
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before
    assert 'Add "publisher": "big-leap" to CANVAS_MANIFEST.json and commit it' in result.output


def test_a_forged_manifest_publisher_is_refused_for_every_deploy_mode(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """The membership check runs for --no-push too, since the deployment entry names the org."""
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": "globex"}))

    result = runner.invoke(app, ["deploy", str(package), "--no-push", "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert not _requests_to(api, "POST", "/deployments")


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
        "plugins": [{"name": NAME, "ref": head, "publisher": "acme"}],
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
        {"name": NAME, "ref": "main", "publisher": "acme"}
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
        {"name": NAME, "ref": "v1.2.0", "publisher": "acme"}
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
    assert f"Pushed {NAME} {head[:12]} to main on Canvas Platform." in result.output
    assert (
        f"To install this commit on an instance: canvas deploy {package} --ref {head[:12]}"
        in result.output
    )
    assert "Not deployed" not in result.output


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
    assert "pass --snapshot" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


# -- deploy --snapshot -------------------------------------------------------


@pytest.fixture
def monorepo(tmp_path: Path) -> Path:
    """A committed package at ``<monorepo>/plugins/acme__intake``, beside another plugin and
    other code, in a repository whose ``origin`` is the customer's own git host.
    """
    root = tmp_path / "monorepo"
    directory = root / "plugins" / NAME
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))
    (root / "plugins" / "acme__other").mkdir()
    (root / "plugins" / "acme__other" / "CANVAS_MANIFEST.json").write_text("{}")
    (root / "services").mkdir()
    (root / "services" / "api.py").write_text("x = 1\n")
    _git(root, "init", "--initial-branch=main")
    _git(root, "remote", "add", "origin", "https://git.example.com/acme/monorepo.git")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "first")
    return directory


# The manifest as platform's catalog listing editor leaves it.
EDITED_MANIFEST = json.dumps({"name": NAME, "catalog": {"tagline": "Intake forms"}})


def _commit_in(directory: Path, path: str, content: str) -> None:
    (directory / path).write_text(content)
    _git(directory, "add", path)
    _git(directory, "commit", "-m", f"Change {path}")


def _commit_on_platform(bare: Path, tmp_path: Path, path: str, content: str) -> None:
    """A commit made on platform's side, the way its catalog listing editor commits to main."""
    checkout = tmp_path / "platform-side"
    _git(tmp_path, "clone", "-q", bare.as_uri(), str(checkout))
    (checkout / path).parent.mkdir(parents=True, exist_ok=True)
    _commit_in(checkout, path, content)
    _git(checkout, "push", "-q", "origin", "HEAD:main")


def test_deploy_snapshot_pushes_only_the_package_and_leaves_the_monorepo_alone(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """--snapshot pushes the committed package folder as one commit traced to its source,
    authored as the signed-in identity, and deploys it, without touching the monorepo.
    """
    root = monorepo.parent.parent
    config = (root / ".git" / "config").read_text()

    result = split_runner.invoke(
        app, ["deploy", str(monorepo), "--snapshot", "--instance", "acme-staging"]
    )

    assert result.exit_code == 0, result.output
    head = _git(root, "rev-parse", "HEAD")
    pushed = _git(bare, "rev-parse", "main")
    assert _git(bare, "ls-tree", "-r", "--name-only", "main") == f"{NAME}/CANVAS_MANIFEST.json"
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(
        root, "rev-parse", f"HEAD:plugins/{NAME}"
    )
    assert _git(bare, "log", "-1", "--format=%an <%ae>", "main") == "Dana Reyes <dana@acme.example>"
    trailers = _git(bare, "log", "-1", "--format=%(trailers:only)", "main")
    assert trailers == f"Monorepo-Commit: {head}\nMonorepo-Path: plugins/{NAME}"
    _git(bare, "fsck", "--strict")
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": NAME, "ref": pushed, "publisher": "acme"}
    ]
    assert (root / ".git" / "config").read_text() == config
    assert _git(root, "status", "--porcelain") == ""
    assert "is not on any remote branch" in result.stderr


def test_deploy_snapshot_keeps_platform_files_beside_the_package_and_skips_an_unchanged_push(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A snapshot replaces only the package folder on main, and an unchanged package pushes
    nothing and deploys the commit main already has.
    """
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, "README.md", "# Intake\n")
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "ls-tree", "-r", "--name-only", "main").splitlines() == [
        "README.md",
        f"{NAME}/CANVAS_MANIFEST.json",
        f"{NAME}/handler.py",
    ]
    pushed = _git(bare, "rev-parse", "main")

    again = runner.invoke(
        app, ["deploy", str(monorepo), "--snapshot", "--instance", "acme-staging"]
    )

    assert again.exit_code == 0, again.output
    assert "main on Canvas Platform already holds this snapshot." in again.output
    assert "Pushed" not in again.output
    assert _git(bare, "rev-parse", "main") == pushed
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": NAME, "ref": pushed, "publisher": "acme"}
    ]


def test_deploy_snapshot_refuses_to_replace_a_change_made_on_platform(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A file in the package changed on main since the last snapshot, such as by the catalog
    listing editor, is not replaced without a person confirming it.
    """
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    edited = _git(bare, "rev-parse", "main")
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    # The paths are part of the error, so a CI log that interleaves stdout and stderr
    # shows them together.
    assert result.output.index("Error:") < result.output.index(f"  {NAME}/CANVAS_MANIFEST.json")
    assert f"`canvas clone {NAME}`" in result.output
    assert _git(bare, "rev-parse", "main") == edited


def test_deploy_snapshot_replaces_a_platform_change_once_confirmed_at_a_terminal(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At a terminal the person may confirm replacing the change made on platform."""
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")
    monkeypatch.setattr(git, "interactive", lambda: True)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"], input="y\n")

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(monorepo, "rev-parse", "HEAD:./")


def test_deploy_snapshot_accepts_a_platform_change_the_monorepo_carries(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """Once the monorepo holds platform's version of a file, a snapshot goes through."""
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output


def test_deploy_snapshot_refuses_to_roll_back_a_later_snapshot(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """A checkout whose HEAD lacks the commit main was last deployed from is refused."""
    _commit_in(monorepo, "handler.py", "x = 1\n")
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    deployed = _git(bare, "rev-parse", "main")
    _git(monorepo, "checkout", "-q", "HEAD~1")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "would roll the plugin back" in result.output
    assert f"  plugins/{NAME}/handler.py" in result.output
    assert _git(bare, "rev-parse", "main") == deployed


def test_deploy_snapshot_refuses_a_branch_missing_changes_main_was_deployed_with(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """A branch that forked before the last deploy and lacks its changes is refused, though
    HEAD is beside the deployed commit rather than behind it.
    """
    root = monorepo.parent.parent
    _commit_in(monorepo, "handler.py", "x = 1\n")
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    deployed = _git(bare, "rev-parse", "main")
    _git(root, "checkout", "-q", "-b", "stale", "HEAD~1")
    _commit_in(monorepo, "other.py", "y = 2\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert f"  plugins/{NAME}/handler.py" in result.output
    assert _git(bare, "rev-parse", "main") == deployed


def test_deploy_snapshot_after_a_deployed_branch_is_squash_merged(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """A branch deployed before it was squash-merged leaves its commit out of main's history,
    but main carries its changes, so a deploy from main goes through.
    """
    root = monorepo.parent.parent
    _git(root, "checkout", "-q", "-b", "feature")
    _commit_in(monorepo, "handler.py", "x = 1\n")
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _git(root, "checkout", "-q", "main")
    _git(root, "merge", "-q", "--squash", "feature")
    _git(root, "commit", "-q", "-m", "Feature, squashed")
    _commit_in(monorepo, "other.py", "y = 2\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(monorepo, "rev-parse", "HEAD:./")


def test_deploy_snapshot_refuses_uncommitted_changes_even_with_yes(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """--snapshot never commits in the larger repository, so uncommitted work is refused."""
    (monorepo / "handler.py").write_text("x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only", "--yes"])

    assert result.exit_code == 2
    assert f"plugins/{NAME}/handler.py" in result.output
    assert _git(monorepo, "rev-list", "--count", "HEAD") == "1"
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


def test_deploy_snapshot_refuses_what_would_not_reach_an_instance_intact(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """Submodules, symbolic links and files stored through a filter, such as Git LFS or
    git-crypt, are refused by path before anything is registered or pushed. A `filter`
    attribute naming no driver changes nothing and is allowed.
    """
    root = monorepo.parent.parent
    (root / ".gitattributes").write_text(
        "*.png filter=lfs\nsecrets.json filter=git-crypt\nnotes.txt filter\n"
    )
    (monorepo / "logo.png").write_text("version https://git-lfs.github.com/spec/v1\n")
    (monorepo / "secrets.json").write_text("{}\n")
    (monorepo / "notes.txt").write_text("notes\n")
    (monorepo / "shared").symlink_to("../../services")
    (monorepo / "vendor").mkdir()  # where an uninitialized submodule sits
    _git(root, "add", ".")
    head = _git(root, "rev-parse", "HEAD")
    _git(root, "update-index", "--add", "--cacheinfo", f"160000,{head},plugins/{NAME}/vendor")
    _git(root, "commit", "-m", "assets")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 2
    assert "logo.png is stored through the 'lfs' filter" in result.output
    assert "secrets.json is stored through the 'git-crypt' filter" in result.output
    assert "notes.txt" not in result.output
    assert "shared is a symbolic link" in result.output
    assert "vendor is a submodule" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


@pytest.mark.parametrize("extra", [["--ref", "v1.2.0"], ["--no-push"]])
def test_deploy_snapshot_refuses_the_options_that_do_not_push(
    extra: list[str], api: requests_mock_module.Mocker, monorepo: Path, signed_in: None
) -> None:
    """--snapshot with an option that deploys without pushing is refused before anything runs."""
    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", *extra])

    assert result.exit_code == 2
    assert "--snapshot pushes a new commit" in result.output
    assert not api.called


def test_deploy_snapshot_needs_a_repository(
    api: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """A package in no git repository has no commits to snapshot."""
    directory = tmp_path / NAME
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": NAME}))

    result = runner.invoke(app, ["deploy", str(directory), "--snapshot", "--push-only"])

    assert result.exit_code == 2
    assert "is not in one" in result.output
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")


def test_deploy_snapshot_needs_the_package_committed(
    api: requests_mock_module.Mocker, monorepo: Path, signed_in: None
) -> None:
    """A package the repository ignores has nothing committed to snapshot."""
    root = monorepo.parent.parent
    _git(root, "rm", "-q", "-r", "--cached", f"plugins/{NAME}")
    (root / ".gitignore").write_text(f"plugins/{NAME}/\n")
    _git(root, "add", ".gitignore")
    _git(root, "commit", "-m", "ignore it")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 2
    assert "has no committed files" in result.output


def test_deploy_snapshot_over_history_that_was_not_snapshotted(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """The first snapshot onto a main built by ordinary pushes treats every file in the
    package on main as platform's, so one the snapshot would change is refused.
    """
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    pushed = _git(bare, "rev-parse", "main")
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "by pushes that were not snapshots" in result.output
    assert f"  {NAME}/CANVAS_MANIFEST.json" in result.output
    assert f"  {NAME}/handler.py" not in result.output  # new in the snapshot, not replaced
    assert _git(bare, "rev-parse", "main") == pushed


def _tag_platform_base(bare: Path, annotated: bool) -> str:
    """Tag platform's main as Canvas Studio tags the commit it starts main from."""
    sha = _git(bare, "rev-parse", "main")
    tag = f"snapshot-baseline/{sha}"
    _git(bare, "tag", *(["-a", "-m", "baseline"] if annotated else []), tag, sha)
    return sha


@pytest.mark.parametrize("annotated", [False, True], ids=["lightweight", "annotated"])
def test_deploy_snapshot_onto_a_tagged_base(
    annotated: bool,
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """A main commit tagged snapshot-baseline/* counts as the last snapshot, so the first
    snapshot onto it replaces the package without the "pushes that were not snapshots" refusal.
    """
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    base = _tag_platform_base(bare, annotated)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(
        monorepo.parent.parent, "rev-parse", f"HEAD:plugins/{NAME}"
    )
    assert _git(bare, "rev-parse", "main~1") == base


def test_deploy_snapshot_refuses_a_platform_change_since_the_tagged_base(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """Only files changed on platform since the tagged base are listed as replaced, and the
    refusal names the tag.
    """
    _commit_in(package, "handler.py", "x = 0\n")
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    base = _tag_platform_base(bare, annotated=False)
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    edited = _git(bare, "rev-parse", "main")
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert f"since snapshot-baseline/{base}" in result.output
    assert f"  {NAME}/CANVAS_MANIFEST.json" in result.output
    assert f"  {NAME}/handler.py" not in result.output
    assert _git(bare, "rev-parse", "main") == edited


def test_deploy_snapshot_prefers_a_later_snapshot_over_the_tagged_base(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """The newest snapshot or tagged commit on main is the starting point, so a snapshot
    pushed after the tagged base still gets the rollback check.
    """
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    _tag_platform_base(bare, annotated=False)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")
    first = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    assert first.exit_code == 0, first.output
    _git(monorepo.parent.parent, "checkout", "-q", "HEAD~1")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "would roll the plugin back" in result.output
    assert f"  plugins/{NAME}/handler.py" in result.output


def test_deploy_snapshot_ignores_a_baseline_tag_off_main(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """Only a tag on main's first-parent chain counts as the last snapshot."""
    # Passes without tag support too: it pins that a tag elsewhere changes nothing.
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    base = _git(bare, "rev-parse", "main")
    side = _git(bare, "commit-tree", f"{base}^{{tree}}", "-p", base, "-m", "side")
    _git(bare, "tag", f"snapshot-baseline/{side}", side)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "by pushes that were not snapshots" in result.output
    assert _git(bare, "rev-parse", "main") == base


def test_deploy_snapshot_onto_a_baseline_tagged_after_an_earlier_snapshot(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A tag-only baseline commit on top of an earlier snapshot is the last snapshot: nothing
    is checked for rolling back the earlier snapshot, and the baseline's own changes are not
    counted as changed on platform.
    """
    root = monorepo.parent.parent
    _commit_in(monorepo, "handler.py", "x = 1\n")
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    baseline = _tag_platform_base(bare, annotated=False)
    _git(root, "checkout", "-q", "HEAD~1")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(
        root, "rev-parse", f"HEAD:plugins/{NAME}"
    )
    assert _git(bare, "rev-parse", "main~1") == baseline


def test_deploy_snapshot_keeps_the_rollback_check_on_a_tagged_snapshot(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """A commit carrying both the Monorepo-Commit trailer and a baseline tag, the shape of
    Canvas Studio's baseline commit for an existing gated project, keeps the rollback check.
    """
    # Passes without tag support too: it pins that the trailer wins over the tag.
    _commit_in(monorepo, "handler.py", "x = 1\n")
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    deployed = _tag_platform_base(bare, annotated=True)
    _git(monorepo, "checkout", "-q", "HEAD~1")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "would roll the plugin back" in result.output
    assert f"  plugins/{NAME}/handler.py" in result.output
    assert _git(bare, "rev-parse", "main") == deployed


def test_deploy_snapshot_starts_from_the_nearest_of_several_baseline_tags(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """With the base tagged at creation and a later commit tagged again, the later tag is the
    starting point, so a change between the two tags is not counted as changed on platform.
    """
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    _tag_platform_base(bare, annotated=False)
    _commit_on_platform(bare, tmp_path, f"{NAME}/handler.py", "x = 0\n")
    _tag_platform_base(bare, annotated=True)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "show", f"main:{NAME}/handler.py") == "x = 1"


def test_deploy_snapshot_from_a_shallow_checkout_onto_a_tagged_base(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A tagged base names no monorepo commit, so a shallow CI checkout deploys onto it
    without being told to fetch more history.
    """
    root = monorepo.parent.parent
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    _tag_platform_base(bare, annotated=False)
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)
    _commit_in(monorepo, "handler.py", "x = 1\n")
    shallow = tmp_path / "ci"
    _git(tmp_path, "clone", "-q", "--depth", "1", root.as_uri(), str(shallow))

    result = split_runner.invoke(
        app, ["deploy", str(shallow / "plugins" / NAME), "--snapshot", "--push-only"]
    )

    assert result.exit_code == 0, result.output + result.stderr
    assert "rolls the plugin back" not in result.stderr
    assert "git fetch --unshallow" not in result.stderr
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(
        root, "rev-parse", f"HEAD:plugins/{NAME}"
    )


def test_deploy_snapshot_onto_a_base_tagged_through_another_tag(
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """A baseline tag that points at another annotated tag counts once peeled to its commit,
    though the inner tag is outside snapshot-baseline/.
    """
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    base = _git(bare, "rev-parse", "main")
    _git(bare, "tag", "-a", "-m", "release", "v1.0.0", base)
    _git(bare, "tag", "-a", "-m", "baseline", f"snapshot-baseline/{base}", "v1.0.0")
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(bare, "rev-parse", "main~1") == base


@pytest.mark.parametrize(
    ("tag", "peel"),
    [
        # A tag that names a tree marks no commit on main.
        ("snapshot-baseline/{base}", "^{tree}"),
        # Only tags under snapshot-baseline/ count, not a name that merely starts the same.
        ("snapshot-baselines/{base}", ""),
    ],
    ids=["tree", "near-miss-name"],
)
def test_deploy_snapshot_ignores_what_is_not_a_baseline_tag_on_main(
    tag: str,
    peel: str,
    api: requests_mock_module.Mocker,
    bare: Path,
    package: Path,
    monorepo: Path,
    signed_in: None,
) -> None:
    """A tag that marks no starting point leaves the refusal for history that was never
    snapshotted, rather than failing the deploy or accepting the history.
    """
    # Passes without tag support too: it pins that such a tag changes nothing.
    runner.invoke(app, ["deploy", str(package), "--push-only"])
    base = _git(bare, "rev-parse", "main")
    _git(bare, "tag", tag.format(base=base), f"{base}{peel}")
    _commit_in(monorepo, "CANVAS_MANIFEST.json", EDITED_MANIFEST)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "by pushes that were not snapshots" in result.output
    assert _git(bare, "rev-parse", "main") == base


def test_deploy_snapshot_aborts_when_the_person_declines_to_replace(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Declining at the terminal leaves main as platform left it."""
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_on_platform(bare, tmp_path, f"{NAME}/CANVAS_MANIFEST.json", EDITED_MANIFEST)
    edited = _git(bare, "rev-parse", "main")
    _commit_in(monorepo, "handler.py", "x = 1\n")
    monkeypatch.setattr(git, "interactive", lambda: True)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"], input="n\n")

    assert result.exit_code == 1
    assert _git(bare, "rev-parse", "main") == edited


def test_deploy_snapshot_from_a_shallow_checkout(
    api: requests_mock_module.Mocker,
    bare: Path,
    monorepo: Path,
    signed_in: None,
    tmp_path: Path,
) -> None:
    """A shallow CI checkout lacks the commit main was last deployed from, so the rollback
    check is skipped and said to be, and a pushed HEAD draws no warning.
    """
    root = monorepo.parent.parent
    runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])
    _commit_in(monorepo, "handler.py", "x = 1\n")
    shallow = tmp_path / "ci"
    _git(tmp_path, "clone", "-q", "--depth", "1", root.as_uri(), str(shallow))

    result = split_runner.invoke(
        app, ["deploy", str(shallow / "plugins" / NAME), "--snapshot", "--push-only"]
    )

    assert result.exit_code == 0, result.output
    assert "so it is not checked whether this deploy rolls the plugin back" in result.stderr
    assert "git fetch --unshallow" in result.stderr
    assert "is not on any remote branch" not in result.stderr
    assert _git(bare, "rev-parse", f"main:{NAME}") == _git(
        root, "rev-parse", f"HEAD:plugins/{NAME}"
    )


def test_deploy_snapshot_reports_a_failed_fetch(
    api: requests_mock_module.Mocker, monorepo: Path, signed_in: None, tmp_path: Path
) -> None:
    """A git server that cannot be fetched from is reported without the usage line."""
    api.post(
        f"{API}/orgs/acme/plugins",
        status_code=201,
        json={"name": NAME, "git_url": (tmp_path / "missing.git").as_uri()},
    )

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "git fetch from Canvas Platform failed" in result.output
    assert "Usage:" not in result.output


def test_deploy_snapshot_reports_a_refused_push(
    api: requests_mock_module.Mocker, bare: Path, monorepo: Path, signed_in: None
) -> None:
    """When platform's git server refuses the snapshot, its reason is shown."""
    hook = bare / "hooks" / "pre-receive"
    # An init.templateDir without hooks/ leaves the bare repository without one.
    hook.parent.mkdir(exist_ok=True)
    hook.write_text("#!/bin/sh\necho 'Refused refs/heads/main: listing is invalid' >&2\nexit 1\n")
    hook.chmod(0o755)

    result = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"])

    assert result.exit_code == 1
    assert "git push to Canvas Platform failed" in result.output
    assert "listing is invalid" in result.output


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
    """`get` derives the plugin and publisher from the repository path and prints git's
    credential fields.
    """
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
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.qs == {"publisher": ["acme"]}


def test_git_credential_for_a_bare_repository_path_sends_no_publisher(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A path with only `<name>.git` names no publisher, so Platform resolves the name alone."""
    requests_mock.post(
        f"{API}/plugins/intake/git-credentials",
        json={"username": "dana", "password": "cnvs_git_1"},
    )

    result = runner.invoke(
        app,
        ["git-credential", "--platform", PLATFORM, "get"],
        input="protocol=https\nhost=git.platform.example\npath=intake.git\n\n",
    )

    assert result.exit_code == 0, result.output
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.qs == {}


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


def test_repo_plugin() -> None:
    """The name is the last path segment without `.git`; the segment before it is the publisher."""
    assert commands.repo_plugin(f"acme/{NAME}.git") == ("acme", NAME)
    assert commands.repo_plugin("/git/acme/intake.git") == ("acme", "intake")
    assert commands.repo_plugin("intake.git") == (None, "intake")
    assert commands.repo_plugin("/intake.git") == (None, "intake")
    # `git` is the server's mount point, not a publisher.
    assert commands.repo_plugin("/git/intake.git") == (None, "intake")


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
def test_config_set_on_an_unmanaged_plugin_is_refused_while_signed_in(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Signed in, a plugin platform does not have is refused rather than written with credentials.ini."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    result = runner.invoke(
        app, ["config", "set", NAME, "A=1", "--instance", "one", "--instance", "two"]
    )

    assert result.exit_code == 1
    assert f"Canvas Platform does not manage {NAME}." in result.output
    assert "sign out with `canvas logout`" in result.output
    mock_update.assert_not_called()


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_set_signed_out_writes_each_instance_directly(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker
) -> None:
    """Signed out, a plugin is configured on each named instance directly."""
    result = runner.invoke(
        app, ["config", "set", NAME, "A=1", "--instance", "one", "--instance", "two"]
    )

    assert result.exit_code == 0, result.output
    assert [c.kwargs["host"] for c in mock_update.call_args_list] == [
        "https://one.canvasmedical.com",
        "https://two.canvasmedical.com",
    ]
    assert mock_update.call_args.kwargs["secrets"] == ["A=1"]
    assert not requests_mock.called


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_on_a_plain_name_is_refused_for_an_instance_platform_does_not_manage(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plain name is asked of platform like any other; a 404 refuses a Canvas instance target."""
    requests_mock.get(f"{API}/plugins/intake", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["config", "unset", "intake", "A", "--instance", "legacy"])

    assert result.exit_code == 1
    assert "Canvas Platform does not manage intake." in result.output
    assert _requests_to(requests_mock, "GET", "/plugins/intake")
    mock_update.assert_not_called()


@patch("canvas_cli.apps.platform.commands.get_default_host")
@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_without_a_target_is_refused_when_the_default_host_is_an_instance(
    mock_update: Mock,
    mock_default_host: Mock,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
) -> None:
    """Platform does not have the plugin and credentials.ini's default is a Canvas instance."""
    mock_default_host.return_value = "https://legacy.canvasmedical.com"
    requests_mock.get(f"{API}/plugins/intake", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["config", "unset", "intake", "A"])

    assert result.exit_code == 1
    assert "Canvas Platform does not manage intake." in result.output
    mock_update.assert_not_called()


@patch("canvas_cli.apps.platform.commands.get_default_host")
@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_without_a_target_uses_a_local_default_host(
    mock_update: Mock,
    mock_default_host: Mock,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
) -> None:
    """Platform does not have the plugin and the default is localhost, which Platform never manages."""
    mock_default_host.return_value = "http://localhost:8000"
    requests_mock.get(f"{API}/plugins/intake", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["config", "unset", "intake", "A"])

    assert result.exit_code == 0, result.output
    assert mock_update.call_args.kwargs["host"] == "http://localhost:8000"


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_on_a_host_that_is_not_a_canvas_instance_never_asks_platform(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Platform can never manage a non-Canvas host, so it goes straight to that host."""
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


def test_clone_passes_the_publisher(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """`--publisher` selects the plugin when two publishers share the name, and the refusal
    names it.
    """
    requests_mock.get(f"{API}/plugins/intake", status_code=404, json={"error": "Not found."})

    result = runner.invoke(app, ["clone", "intake", "--publisher", "acme"])

    assert result.exit_code == 2
    assert requests_mock.last_request is not None
    assert requests_mock.last_request.qs == {"publisher": ["acme"]}
    assert "published by 'acme'" in result.output


def test_clone_of_an_ambiguous_name_prints_platforms_sentence(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A 409 from Platform tells the person to pass `--publisher`; the CLI relays that sentence."""
    sentence = "Two publishers have a plugin named 'intake'; pass ?publisher=<slug>."
    requests_mock.get(
        f"{API}/plugins/intake", status_code=409, json={"error": sentence, "code": "ambiguous"}
    )

    result = runner.invoke(app, ["clone", "intake"])

    assert result.exit_code == 1
    assert sentence in result.output


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
    assert manifest["publisher"] == "acme"
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
    manifest_path = tmp_path / "intake" / "big_leap__intake" / "CANVAS_MANIFEST.json"
    assert json.loads(manifest_path.read_text())["publisher"] == "big-leap"


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
    assert minted == [
        (f"/api/v1/plugins/{NAME}/git-credentials?publisher=acme", "Bearer cnvs_ua_9")
    ]


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


def test_manifest_publisher_is_none_without_the_field(tmp_path: Path) -> None:
    """A manifest with no `publisher` has none, which is different from an unreadable one."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "intake"}))

    assert commands.manifest_publisher(tmp_path) is None


def test_manifest_publisher_refuses_a_value_that_is_not_a_string(tmp_path: Path) -> None:
    """A non-string publisher names no organization, so it fails closed rather than counting as none."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "intake", "publisher": 3}))

    with pytest.raises(typer.BadParameter, match='"publisher" that is not a string'):
        commands.manifest_publisher(tmp_path)


def test_manifest_name_refuses_a_manifest_that_is_not_an_object(tmp_path: Path) -> None:
    """A manifest that parses to a list is unreadable as a manifest."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text(json.dumps(["intake"]))

    with pytest.raises(typer.BadParameter, match="it is not a JSON object"):
        commands.manifest_name(tmp_path)


def test_manifest_publisher_reports_an_unreadable_manifest(tmp_path: Path) -> None:
    """An unreadable manifest fails closed rather than counting as no publisher."""
    (tmp_path / "CANVAS_MANIFEST.json").write_text("{not json")

    with pytest.raises(typer.BadParameter, match="Could not read"):
        commands.manifest_publisher(tmp_path)


@pytest.mark.parametrize("indent", [2, 4])
@pytest.mark.parametrize("trailing_newline", [True, False])
def test_write_manifest_publisher_keeps_the_manifests_formatting(
    tmp_path: Path, indent: int, trailing_newline: bool
) -> None:
    """The publisher lands right after `name`, keeping indent, non-ASCII text and the final newline."""
    original = {"name": "intake", "description": "Café intake", "components": {"handlers": []}}
    text = json.dumps(original, indent=indent, ensure_ascii=False)
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text(text + ("\n" if trailing_newline else ""), encoding="utf-8")

    commands.write_manifest_publisher(tmp_path, "acme")

    expected = json.dumps(
        {
            "name": "intake",
            "publisher": "acme",
            **{k: v for k, v in original.items() if k != "name"},
        },
        indent=indent,
        ensure_ascii=False,
    )
    assert manifest.read_text(encoding="utf-8") == expected + ("\n" if trailing_newline else "")


def test_write_manifest_publisher_changes_only_the_publisher_line(tmp_path: Path) -> None:
    """The deploy commits the manifest, so its own layout (inline arrays, spacing) is kept."""
    text = (
        "{\n"
        '    "sdk_version": "0.1.4",\n'
        '    "name": "intake",\n'
        '    "secrets": ["api-key"],\n'
        '    "components": {"handlers": [{"name": "Handler", "class": "intake.h:H"}]}\n'
        "}\n"
    )
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text(text)

    commands.write_manifest_publisher(tmp_path, "big-leap")

    assert manifest.read_text() == text.replace(
        '    "name": "intake",\n', '    "name": "intake",\n    "publisher": "big-leap",\n'
    )


def test_write_manifest_publisher_replaces_only_the_existing_value(tmp_path: Path) -> None:
    """An existing top-level publisher takes the new slug; a nested `publisher` is untouched."""
    text = '{\n  "name": "intake",\n  "publisher":"old",\n  "catalog": {"publisher": "keep"}\n}\n'
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text(text)

    commands.write_manifest_publisher(tmp_path, "acme")

    assert manifest.read_text() == text.replace('"publisher":"old"', '"publisher":"acme"')


def test_write_manifest_publisher_replaces_a_null_publisher_rather_than_adding_a_second(
    tmp_path: Path,
) -> None:
    """A null publisher after `name` is replaced; a second key would leave the manifest null."""
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text('{\n    "name": "intake",\n    "publisher": null\n}\n')

    commands.write_manifest_publisher(tmp_path, "acme")

    text: str = manifest.read_text()
    assert json.loads(text) == {"name": "intake", "publisher": "acme"}
    assert text.count('"publisher"') == 1


def test_write_manifest_publisher_replaces_an_existing_publisher_in_place(tmp_path: Path) -> None:
    """An existing publisher keeps its position and takes the new slug."""
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text(
        json.dumps({"name": "intake", "version": "1", "publisher": "old", "z": 1}, indent=4)
    )

    commands.write_manifest_publisher(tmp_path, "acme")

    assert list(json.loads(manifest.read_text())) == ["name", "version", "publisher", "z"]
    assert json.loads(manifest.read_text())["publisher"] == "acme"


def test_write_manifest_publisher_refuses_an_invalid_manifest(tmp_path: Path) -> None:
    """An unreadable manifest is refused, and the file is left as it was."""
    manifest = tmp_path / "CANVAS_MANIFEST.json"
    manifest.write_text("{not json")

    with pytest.raises(typer.BadParameter, match="Could not read"):
        commands.write_manifest_publisher(tmp_path, "acme")

    assert manifest.read_text() == "{not json"


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


def test_staff_cannot_deploy_under_an_org_they_do_not_belong_to(
    requests_mock: requests_mock_module.Mocker, signed_in: None, tmp_path: Path
) -> None:
    """Staff reach other orgs through Platform, not through a publisher the CLI cannot verify."""
    directory = tmp_path / "intake"
    directory.mkdir()
    (directory / "CANVAS_MANIFEST.json").write_text(
        json.dumps({"name": "intake", "publisher": "globex"})
    )
    requests_mock.get(f"{API}/me", json={**ME, "canvas_employee": True})

    result = runner.invoke(
        app, ["deploy", str(directory), "--no-push", "--instance", "other-staging"]
    )

    assert result.exit_code == 2
    assert "which is not an organization you belong to" in result.output
    assert not _requests_to(requests_mock, "POST", "/deployments")


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
    manifest_path = tmp_path / "intake" / "big_leap__intake" / "CANVAS_MANIFEST.json"
    assert json.loads(manifest_path.read_text())["publisher"] == "big-leap"


def test_init_without_a_publishing_organization_scaffolds_unregistered(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Signed in without the right to push code anywhere, init scaffolds without registering,
    and records no publisher.
    """
    monkeypatch.chdir(tmp_path)
    viewer = {**ACME, "capabilities": ["view_org_assets"]}
    requests_mock.get(f"{API}/me", json={**ME, "organizations": [viewer]})

    result = runner.invoke(app, ["init"], input="Intake\n")

    assert result.exit_code == 0, result.output
    assert "is scaffolded without registration or a git repository" in result.output
    manifest_path = tmp_path / "intake" / "intake" / "CANVAS_MANIFEST.json"
    assert "publisher" not in json.loads(manifest_path.read_text())
    assert not _requests_to(requests_mock, "POST", "/orgs/acme/plugins")


def test_init_refuses_a_scaffolded_name_that_is_too_long(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A project name that yields a name over 63 characters is refused before registering."""
    monkeypatch.chdir(tmp_path)
    requests_mock.get(f"{API}/me", json=ME)

    result = runner.invoke(app, ["init"], input=f"{'a' * 60}\n")

    assert result.exit_code == 2
    assert "is not a valid plugin name" in result.output
    assert "at most 63 characters" in result.output
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
    manifest = json.loads((package_dir / "CANVAS_MANIFEST.json").read_text())
    assert manifest["name"] == "acme__intake_app"
    assert manifest["publisher"] == "acme"
    assert _requests_to(requests_mock, "POST", "/orgs/acme/plugins")[0].json() == {
        "name": "acme__intake_app"
    }
    assert "Initialized a git repository" not in result.output
    assert not (package_dir / ".git").exists()
    assert f"canvas deploy {package_dir}" in result.output


# -- init: signed out says so ------------------------------------------------


def test_init_signed_out_says_how_to_get_a_registered_plugin(
    requests_mock: requests_mock_module.Mocker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Signed out, init names the platform it checked and says how to get a registered plugin."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"], input="Intake Forms\n")

    assert result.exit_code == 0, result.output
    assert f"not signed in to Canvas Platform at {auth.DEFAULT_PLATFORM_URL}" in result.output
    assert "is scaffolded without registration or a git repository" in result.output
    assert "`canvas login` then `canvas init` gives a registered plugin" in result.output
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
    # An init.templateDir without hooks/ leaves the bare repository without one.
    hook.parent.mkdir(exist_ok=True)
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


# -- scenarios across names, publishers and the wire --------------------------


TWO_ORGS: dict[str, Any] = {**ME, "organizations": [ACME, BIG_LEAP]}


def _register_big_leap(api: requests_mock_module.Mocker, bare: Path) -> None:
    """Platform registers ``intake`` under big-leap, answering with ``bare`` as its repository."""
    api.post(
        f"{API}/orgs/big-leap/plugins",
        status_code=201,
        json={
            "name": "intake",
            "publisher": "big-leap",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )


def _has_main(bare: Path) -> bool:
    """Whether anything was pushed to the bare repository's ``main``."""
    probe = subprocess.run(
        ["git", "-C", str(bare), "rev-parse", "--verify", "-q", "main"],
        capture_output=True,
        text=True,
        check=False,
    )
    return probe.returncode == 0


def test_a_second_deploy_reads_the_publisher_the_first_one_recorded(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S1: the person is asked once, at a terminal, and every later deploy publishes as that
    choice without a terminal, in registration and in the deployment entry alike.
    """
    api.get(f"{API}/me", json=TWO_ORGS)
    _register_big_leap(api, bare)
    package = _plain_package(tmp_path)

    monkeypatch.setattr(git, "interactive", lambda: True)
    first = runner.invoke(
        app,
        ["deploy", str(package), "--instance", "acme-staging"],
        input="2\ny\nRecord publisher\n",
    )
    assert first.exit_code == 0, first.output
    first_sha = _git(bare, "rev-parse", "main")

    monkeypatch.setattr(git, "interactive", lambda: False)
    (package / "handlers.py").write_text("x = 1\n")
    _git(package, "add", ".")
    _git(package, "commit", "-m", "second")
    second = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert second.exit_code == 0, second.output
    assert "Which organization" not in second.output
    assert "several organizations" not in second.output
    second_sha = _git(bare, "rev-parse", "main")
    assert second_sha != first_sha
    assert len(_requests_to(api, "POST", "/orgs/big-leap/plugins")) == 2
    assert not _requests_to(api, "POST", "/orgs/acme/plugins")
    assert [r.json()["plugins"] for r in _requests_to(api, "POST", "/deployments")] == [
        [{"name": "intake", "ref": first_sha, "publisher": "big-leap"}],
        [{"name": "intake", "ref": second_sha, "publisher": "big-leap"}],
    ]


def test_a_refused_registration_keeps_the_choice_for_the_rerun(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S2: Platform refusing the registration pushes and deploys nothing, and the rerun, often
    without a terminal, publishes as the org the person already chose instead of asking again.
    """
    api.get(f"{API}/me", json=TWO_ORGS)
    api.post(
        f"{API}/orgs/big-leap/plugins",
        [
            {
                "status_code": 403,
                "json": {
                    "error": "That needs push_plugin_code in Big Leap.",
                    "code": "forbidden",
                },
            },
            {
                "status_code": 201,
                "json": {
                    "name": "intake",
                    "publisher": "big-leap",
                    "git_url": bare.as_uri(),
                    "default_branch": "main",
                },
            },
        ],
    )
    package = _plain_package(tmp_path)

    monkeypatch.setattr(git, "interactive", lambda: True)
    refused = runner.invoke(
        app, ["deploy", str(package), "--instance", "acme-staging"], input="2\n"
    )

    assert refused.exit_code == 1, refused.output
    assert "That needs push_plugin_code in Big Leap." in refused.output
    assert not _has_main(bare)
    assert not _requests_to(api, "POST", "/deployments")
    assert commands.manifest_publisher(package) == "big-leap"

    monkeypatch.setattr(git, "interactive", lambda: False)
    rerun = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging", "--yes"])

    assert rerun.exit_code == 0, rerun.output
    assert "Which organization" not in rerun.output
    assert json.loads(_git(bare, "show", "main:intake/CANVAS_MANIFEST.json"))["publisher"] == (
        "big-leap"
    )
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"][0]["publisher"] == (
        "big-leap"
    )


def test_a_monorepo_deploy_refused_for_missing_snapshot_leaves_the_manifest_for_the_rerun(
    api: requests_mock_module.Mocker,
    monorepo: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S3: a deploy refused because the package needs --snapshot writes nothing, so the
    --snapshot rerun the refusal recommends finds the package committed.
    """
    api.get(f"{API}/me", json=TWO_ORGS)
    monkeypatch.setattr(git, "interactive", lambda: True)
    manifest = monorepo / "CANVAS_MANIFEST.json"
    before: bytes = manifest.read_bytes()

    refused = runner.invoke(
        app, ["deploy", str(monorepo), "--instance", "acme-staging"], input="1\n"
    )

    assert refused.exit_code == 2, refused.output
    assert "pass --snapshot" in refused.output
    assert manifest.read_bytes() == before

    rerun = runner.invoke(app, ["deploy", str(monorepo), "--snapshot", "--push-only"], input="1\n")

    assert rerun.exit_code == 0, rerun.output
    assert _has_main(bare)


def test_an_init_scaffold_deploys_as_its_recorded_publisher_after_joining_a_second_org(
    api: requests_mock_module.Mocker,
    signed_in: None,
    bare: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S4: init records the publisher, so a deploy without a terminal after the person joins a
    second org neither asks nor refuses, and the entry names the org init chose.
    """
    monkeypatch.chdir(tmp_path)
    api.post(
        f"{API}/orgs/acme/plugins",
        status_code=201,
        json={
            "name": "acme__intake_forms",
            "publisher": "acme",
            "git_url": bare.as_uri(),
            "default_branch": "main",
        },
    )
    initialized = runner.invoke(app, ["init"], input="Intake Forms\n")
    assert initialized.exit_code == 0, initialized.output
    package_dir = tmp_path / "intake-forms" / "acme__intake_forms"

    api.get(f"{API}/me", json=TWO_ORGS)
    result = runner.invoke(app, ["deploy", str(package_dir), "--instance", "acme-staging", "--yes"])

    assert result.exit_code == 0, result.output
    assert "Which organization" not in result.output
    assert "several organizations" not in result.output
    pushed = json.loads(_git(bare, "show", "main:acme__intake_forms/CANVAS_MANIFEST.json"))
    assert (pushed["name"], pushed["publisher"]) == ("acme__intake_forms", "acme")
    assert len(_requests_to(api, "POST", "/orgs/acme/plugins")) == 2
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": "acme__intake_forms", "ref": _git(bare, "rev-parse", "main"), "publisher": "acme"}
    ]


def test_a_clone_by_publisher_mints_git_tokens_for_that_publisher(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S5: `clone --publisher` finds big-leap's `intake`, and git asking for credentials on the
    clone's origin gets a token minted for big-leap's repository, taken from the cloned path.
    """
    canvas = Path(sys.executable).parent / "canvas"
    if not canvas.exists():
        pytest.skip("the canvas entry point is not installed beside this interpreter")

    # Platform's git URLs are `<git host>/<publisher>/<name>.git`.
    git_url = "https://git.platform.example/big-leap/intake.git"
    source = _plain_package(tmp_path)
    bare = tmp_path / "server" / "intake.git"
    bare.mkdir(parents=True)
    _git(bare, "init", "--bare", "--initial-branch=main")
    _git(source, "push", bare.as_uri(), "HEAD:main")

    seen: list[tuple[str, str]] = []

    class FakePlatform(BaseHTTPRequestHandler):
        def _answer(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            seen.append(("GET", self.path))
            self._answer({"name": "intake", "publisher": "big-leap", "git_url": git_url})

        def do_POST(self) -> None:
            seen.append(("POST", self.path))
            self._answer({"username": "dana", "password": "cnvs_git_1"})

        def log_message(self, format: str, *args: object) -> None:
            """Keep the request log out of the test output."""

    server = HTTPServer(("127.0.0.1", 0), FakePlatform)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    platform = f"http://127.0.0.1:{server.server_address[1]}"
    home = tmp_path / "home"
    credentials = home / ".canvas" / "platform-credentials.json"
    credentials.parent.mkdir(parents=True)
    tokens = {"access_token": "cnvs_ua_9", "refresh_token": "cnvs_rt_9", "expires_at": 4102444800}
    credentials.write_text(json.dumps({"default": platform, "platforms": {platform: tokens}}))
    monkeypatch.setattr(auth, "CREDENTIALS_PATH", credentials)
    monkeypatch.setattr(sys, "argv", [str(canvas)])
    # The clone fetches big-leap's repository from disk; its origin stays Platform's URL.
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", f"url.{bare.as_uri()}.insteadOf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", git_url)
    destination = tmp_path / "cloned"

    try:
        cloned = runner.invoke(
            app, ["clone", "intake", str(destination), "--publisher", "big-leap"]
        )
        assert cloned.exit_code == 0, cloned.output
        # `remote get-url` applies insteadOf; the configured URL is what git authenticates for.
        origin = _git(destination, "config", "remote.origin.url")
        filled = subprocess.run(
            ["git", "-C", str(destination), "credential", "fill"],
            input=f"url={origin}\n\n",
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(home), "GIT_CONFIG_GLOBAL": os.devnull},
            timeout=60,
        )
    finally:
        server.shutdown()

    assert origin == git_url
    assert filled.returncode == 0, filled.stderr
    assert "password=cnvs_git_1" in filled.stdout.splitlines()
    assert seen == [
        ("GET", "/api/v1/plugins/intake?publisher=big-leap"),
        ("POST", "/api/v1/plugins/intake/git-credentials?publisher=big-leap"),
    ]


def test_a_platform_that_still_requires_a_prefix_stops_the_deploy_before_git(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None, bare: Path
) -> None:
    """S6: until Platform accepts plain names, its registration refusal reaches the person and
    no code reaches its git server, since there is no publisher to push `intake` under.
    """
    sentence = (
        "A plugin name is lowercase letters, digits and underscores in the form "
        "<prefix>__<package>, such as acme__my_plugin."
    )
    api.post(
        f"{API}/orgs/acme/plugins",
        status_code=400,
        json={"error": sentence, "code": "invalid_name"},
    )
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 1, result.output
    assert sentence in result.output
    assert not _has_main(bare)
    assert not _requests_to(api, "POST", "/deployments")
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before


@patch("canvas_cli.apps.platform.commands.instance_plugin.update")
def test_config_on_a_name_two_publishers_share_fails_closed(
    mock_update: Mock, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """S7: an ambiguous name is refused with Platform's sentence rather than written through
    credentials.ini, which would change an instance behind Platform's back.
    """
    sentence = "Two publishers have a plugin named 'intake': acme, big-leap. Pass ?publisher=."
    requests_mock.get(
        f"{API}/plugins/intake", status_code=409, json={"error": sentence, "code": "ambiguous"}
    )

    result = runner.invoke(app, ["config", "set", "intake", "A=1", "--instance", "acme-staging"])

    assert result.exit_code == 1, result.output
    assert sentence in result.output
    assert not [r for r in requests_mock.request_history if r.method == "PUT"]
    mock_update.assert_not_called()


def test_an_abandoned_organization_prompt_records_and_registers_nothing(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    bare: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S8: an unanswered question chose nothing, so nothing is written, registered or committed."""
    api.get(f"{API}/me", json=TWO_ORGS)
    _register_big_leap(api, bare)
    monkeypatch.setattr(git, "interactive", lambda: True)
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()
    head = _git(package, "rev-parse", "HEAD")

    def interrupted(*args: object, **kwargs: object) -> None:
        """Ctrl-C at the prompt, which click turns into Abort."""
        raise typer.Abort()

    # CliRunner answers an exhausted input with an empty line, so a required prompt would
    # repeat forever; the interrupt is raised where the prompt reads instead.
    monkeypatch.setattr(typer, "prompt", interrupted)

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 1, result.output
    assert "Aborted" in result.output
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before
    assert _git(package, "rev-parse", "HEAD") == head
    assert not any("/orgs/" in r.url for r in api.request_history if r.method == "POST")


def test_an_org_without_the_push_role_is_not_offered_for_a_push(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """S9: an org where the person cannot push code is no choice for a push, so the one org that
    can push is used without a prompt or a manifest write.
    """
    reader = {**BIG_LEAP, "capabilities": ["view_org_assets", "deploy_plugin"]}
    api.get(f"{API}/me", json={**ME, "organizations": [ACME, reader]})
    monkeypatch.setattr(git, "interactive", lambda: True)
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert "Which organization" not in result.output
    assert "Publishing as acme, the only organization you can publish in." in result.output
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before


def test_a_prefixed_name_without_a_publisher_does_not_pick_the_org_from_its_prefix(
    api: requests_mock_module.Mocker, package: Path, signed_in: None
) -> None:
    """Q2: the prefix is a naming convention only, so a member of several orgs without a
    terminal is asked to name the publisher even for `acme__intake`.
    """
    api.get(f"{API}/me", json=TWO_ORGS)

    result = runner.invoke(
        app, ["deploy", str(package), "--ref", "main", "--instance", "acme-staging"]
    )

    assert result.exit_code == 2, result.output
    assert "You can publish in several organizations: acme, big-leap." in result.output
    assert not _requests_to(api, "POST", "/deployments")


def test_a_deploy_of_a_pushed_ref_uses_the_choice_without_writing_the_manifest(
    api: requests_mock_module.Mocker,
    tmp_path: Path,
    signed_in: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Q4: `--ref` commits nothing, so a recorded choice would sit uncommitted; the choice is
    used for this deploy and the manifest line is printed instead.
    """
    api.get(f"{API}/me", json=TWO_ORGS)
    monkeypatch.setattr(git, "interactive", lambda: True)
    package = _plain_package(tmp_path)
    before: bytes = (package / "CANVAS_MANIFEST.json").read_bytes()

    result = runner.invoke(
        app, ["deploy", str(package), "--ref", "main", "--instance", "acme-staging"], input="2\n"
    )

    assert result.exit_code == 0, result.output
    assert (package / "CANVAS_MANIFEST.json").read_bytes() == before
    assert 'Add "publisher": "big-leap" to CANVAS_MANIFEST.json' in result.output
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"] == [
        {"name": "intake", "ref": "main", "publisher": "big-leap"}
    ]


def test_an_empty_manifest_publisher_is_refused_as_naming_no_org(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """Q5: an empty string names no organization, so it is refused rather than read as absent."""
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": ""}))

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 2, result.output
    assert "names publisher '', which is not an organization you belong to" in result.output
    assert not _requests_to(api, "POST", "/deployments")


def test_a_null_manifest_publisher_counts_as_absent(
    api: requests_mock_module.Mocker, tmp_path: Path, signed_in: None
) -> None:
    """Q5: `null` is the same as no `publisher`, so the one org publishes."""
    package = _plain_package(tmp_path, json.dumps({"name": "intake", "publisher": None}))

    result = runner.invoke(app, ["deploy", str(package), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _requests_to(api, "POST", "/deployments")[0].json()["plugins"][0]["publisher"] == "acme"
