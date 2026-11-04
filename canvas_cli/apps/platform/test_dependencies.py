"""Tests for deploying a plugin with dependencies: resolution, fetching, pushing and the lock.

HTTP is mocked with requests-mock. git is real: a dependency's source repository is
a local repository that git reaches through ``url.<file>.insteadOf``, standing in
for the https address the manifest names, and platform's git server is a bare
repository per plugin.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import requests_mock as requests_mock_module
import typer
from packaging.version import Version
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context
from typer.testing import CliRunner

from canvas_cli.apps.platform import auth, commands, dependencies, git
from canvas_cli.main import app

runner = CliRunner()
PLATFORM = "https://platform.example"
API = f"{PLATFORM}/api/v1"
ROOT = "acme__suite"
SOURCE = "https://git.example.com/acme/kit.git"

ACME: dict[str, Any] = {
    "slug": "acme",
    "name": "Acme Health",
    "plugin_prefix": "acme",
    "capabilities": ["view_org_assets", "push_plugin_code", "deploy_plugin"],
}
ME: dict[str, Any] = {
    "email": "dana@acme.example",
    "name": "Dana Reyes",
    "canvas_employee": False,
    "organizations": [ACME],
}
BASE_SHA = "b" * 40


def _git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _manifest(name: str, version: str, **extra: Any) -> dict[str, Any]:
    """A manifest ``canvas validate`` accepts, for a plugin with no handlers."""
    return {
        "sdk_version": "0.1.0",
        "plugin_version": version,
        "name": name,
        "description": f"The {name} plugin.",
        "components": {"handlers": []},
        "tags": {},
        "license": "",
        "readme": False,
        **extra,
    }


def _kit(version: str = ">=0.1,<1", **source: str) -> dict[str, Any]:
    return {"name": "kit", "version": version, "source": {"git": SOURCE, **source}}


@pytest.fixture(autouse=True)
def _environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A git identity, fast polling, and the source address rewritten to a local path."""
    for variable in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(variable, "Test")
    for variable in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(variable, "test@example.com")
    monkeypatch.setattr(commands, "POLL_INTERVAL_SECONDS", 0)
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", f"url.{(tmp_path / 'remotes').as_uri()}/.insteadOf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "https://git.example.com/acme/")
    auth.save_tokens(
        PLATFORM,
        {"access_token": "cnvs_ua_1", "refresh_token": "cnvs_rt_1", "expires_in": 3600},
        make_default=True,
    )


@pytest.fixture
def source(tmp_path: Path) -> Path:
    """The dependency's source repository, which the manifest names as ``SOURCE``."""
    repo = tmp_path / "remotes" / "kit.git"
    repo.mkdir(parents=True)
    _git(repo, "init", "--initial-branch=main")
    return repo


def _release(
    repo: Path,
    version: str,
    tag: str,
    *,
    folder: str = "plugins/kit",
    **manifest: Any,
) -> str:
    """Commit ``kit`` at ``version`` in ``folder`` and tag it; returns the commit."""
    directory = repo / folder
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "CANVAS_MANIFEST.json").write_text(
        json.dumps(_manifest("kit", version) | manifest)
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", f"Release {version}")
    _git(repo, "tag", "-a", tag, "-m", tag)
    return _git(repo, "rev-parse", "HEAD")


def _server(tmp_path: Path, name: str) -> Path:
    return tmp_path / "server" / f"{name}.git"


@pytest.fixture
def api(requests_mock: requests_mock_module.Mocker, tmp_path: Path) -> requests_mock_module.Mocker:
    """Platform, with a bare repository per registered plugin and no versions of ``kit``."""

    def register(request: _RequestObjectProxy, context: _Context) -> dict[str, Any]:
        name = request.json()["name"]
        server = _server(tmp_path, name)
        if not server.exists():
            server.mkdir(parents=True)
            _git(server, "init", "--bare", "--initial-branch=main")
        context.status_code = 201
        return {"name": name, "publisher": "acme", "git_url": server.as_uri()}

    requests_mock.get(f"{API}/me", json=ME)
    requests_mock.get(
        f"{API}/instances",
        json={
            "instances": [
                {"slug": "acme-staging", "managed": True, "capabilities": ["deploy_plugin"]}
            ]
        },
    )
    requests_mock.post(f"{API}/orgs/acme/plugins", json=register)
    requests_mock.get(
        f"{API}/plugins/kit/versions",
        status_code=404,
        json={"error": "Not found.", "code": "not_found"},
    )
    deployment = {
        "id": "6f1c",
        "action": "deploy",
        "status": "succeeded",
        "targets": [
            {"plugin": "kit", "instance": "acme-staging", "status": "succeeded", "wave": 0},
            {"plugin": ROOT, "instance": "acme-staging", "status": "succeeded", "wave": 1},
        ],
        "consent_requests": [],
    }
    requests_mock.post(f"{API}/deployments", status_code=202, json=deployment)
    return requests_mock


def _root(tmp_path: Path, *requirements: dict[str, Any]) -> Path:
    """A committed bundle ``acme__suite`` at ``<repo>/acme__suite`` requiring ``requirements``."""
    repo = tmp_path / "work"
    directory = repo / ROOT
    directory.mkdir(parents=True)
    (directory / "CANVAS_MANIFEST.json").write_text(
        json.dumps(
            {"name": ROOT, "plugin_version": "1.0.0", "bundle": True, "dependencies": requirements}
        )
    )
    _git(repo, "init", "--initial-branch=main")
    _git(repo, "add", ROOT)
    _git(repo, "commit", "-m", "first")
    return directory


def _require(directory: Path, *requirements: dict[str, Any]) -> None:
    manifest = json.loads((directory / "CANVAS_MANIFEST.json").read_text())
    manifest["dependencies"] = list(requirements)
    (directory / "CANVAS_MANIFEST.json").write_text(json.dumps(manifest))


def _commit_lock(directory: Path) -> None:
    """Commit the lock a deploy wrote, as its message asks."""
    _git(directory, "add", "CANVAS_LOCK.json")
    _git(directory, "commit", "-q", "-m", "Lock dependencies")


def _lock(directory: Path) -> dict[str, Any]:
    return json.loads((directory / "CANVAS_LOCK.json").read_text())


def _deployments(mock: requests_mock_module.Mocker) -> list[dict[str, Any]]:
    return [
        r.json()
        for r in mock.request_history
        if r.method == "POST" and r.path.endswith("/deployments")
    ]


def _versions(mock: requests_mock_module.Mocker, name: str, *versions: tuple[str, str]) -> None:
    """Platform holds ``versions`` of ``name``, as (version, sha), newest first."""
    mock.get(
        f"{API}/plugins/{name}/versions",
        json={
            "plugin": name,
            "publisher": "acme",
            "versions": [
                {"version": v, "sha": sha, "released": True, "pushed_at": "2026-11-01T00:00:00Z"}
                for v, sha in versions
            ],
        },
    )


def _no_git_remote(*args: Any) -> Any:
    raise AssertionError("the source repository was contacted")


# -- version rules -------------------------------------------------------------


@pytest.mark.parametrize(
    ("version", "specifier", "expected"),
    [
        ("1.16.0", "1.16.0", True),
        ("1.16", "1.16.0", True),
        ("1.16.1", "1.16.0", False),
        ("0.1.3", ">=0.1.1,<0.2", True),
        ("0.2.0", ">=0.1.1,<0.2", False),
        ("0.1.5rc1", ">=0.1.1,<0.2", False),
        ("0.1.5rc1", "0.1.5rc1", True),
        ("not a version", ">=0", False),
    ],
)
def test_satisfies(version: str, specifier: str, expected: bool) -> None:
    """An exact version matches itself; a range never matches a prerelease."""
    assert dependencies.satisfies(version, specifier) is expected


TAGS = {
    "v0.1.0": "1" * 40,
    "kit-v0.2.0": "2" * 40,
    "v0.2.0": "3" * 40,
    "v0.3.0rc1": "4" * 40,
    "other-v9.0.0": "5" * 40,
    "v-not-a-version": "6" * 40,
}


def test_best_tag_takes_the_newest_release_and_prefers_the_named_tag() -> None:
    """The newest satisfying release wins, a prerelease is skipped by a range, and of two tags
    naming one version `<name>-v<version>` wins.
    """
    assert dependencies.best_tag("kit", ">=0.1", {"git": SOURCE}, TAGS) == (
        Version("0.2.0"),
        "kit-v0.2.0",
        "2" * 40,
    )


def test_best_tag_takes_a_prerelease_pinned_exactly() -> None:
    """A prerelease is taken when the requirement names it exactly."""
    found = dependencies.best_tag("kit", "0.3.0rc1", {"git": SOURCE}, TAGS)
    assert found is not None
    assert found[1] == "v0.3.0rc1"


def test_best_tag_follows_the_source_tag_pattern() -> None:
    """A source `tag` pattern replaces the default tag names."""
    tags = {"release-1.2.0": "7" * 40, "v9.0.0": "8" * 40}
    found = dependencies.best_tag("kit", ">=1", {"git": SOURCE, "tag": "release-{version}"}, tags)
    assert found is not None
    assert found[1:] == ("release-1.2.0", "7" * 40)


def test_read_lock_refuses_an_unknown_lock_version(tmp_path: Path) -> None:
    """A lock written in a format this CLI does not read is refused, naming --update."""
    (tmp_path / "CANVAS_LOCK.json").write_text(json.dumps({"lock_version": 9, "plugins": {}}))
    with pytest.raises(typer.BadParameter, match="--update"):
        dependencies.read_lock(tmp_path)


def test_ls_remote_tags_reports_the_commit_an_annotated_tag_points_at(source: Path) -> None:
    """Annotated and lightweight tags both map to their commit."""
    annotated = _release(source, "0.1.0", "v0.1.0")
    _git(source, "tag", "light", annotated)

    assert git.ls_remote_tags(SOURCE) == {"v0.1.0": annotated, "light": annotated}


# -- deploy --------------------------------------------------------------------


def test_deploy_fetches_a_missing_dependency_pushes_it_and_locks_it(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A dependency platform does not hold is cloned at its newest release tag, validated,
    pushed to platform as a snapshot, locked, and deployed with the plugin in one deployment.
    """
    _release(source, "0.1.0", "kit-v0.1.0")
    commit = _release(source, "0.2.0", "kit-v0.2.0")
    _release(source, "0.3.0rc1", "kit-v0.3.0rc1")
    root = _root(tmp_path, _kit(path="plugins/kit"))

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert "Dependencies of acme__suite:" in result.output
    assert (
        f"  kit 0.2.0 (acme): fetch kit-v0.2.0 from {SOURCE} and push it, required by acme__suite"
        in result.output
    )
    kit_server = _server(tmp_path, "kit")
    revision = _git(kit_server, "rev-parse", "main")
    assert _git(kit_server, "ls-tree", "-r", "--name-only", "main") == "kit/CANVAS_MANIFEST.json"
    assert _lock(root) == {
        "lock_version": 1,
        "plugins": {
            "kit": {
                "version": "0.2.0",
                "publisher": "acme",
                "source": {
                    "git": SOURCE,
                    "path": "plugins/kit",
                    "tag": "kit-v0.2.0",
                    "commit": commit,
                },
                "revision": revision,
                "required_by": [ROOT],
            }
        },
    }
    (deployment,) = _deployments(api)
    assert deployment == {
        "action": "deploy",
        "plugins": [
            {"name": ROOT, "ref": _git(root, "rev-parse", "HEAD")},
            {"name": "kit", "ref": revision, "publisher": "acme"},
        ],
        "instances": ["acme-staging"],
    }
    assert "kit on acme-staging (wave 0): succeeded" in result.output
    assert f"{ROOT} on acme-staging (wave 1): succeeded" in result.output


def test_deploy_resolves_the_dependencies_of_a_fetched_dependency(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A fetched plugin's own dependencies are resolved too, here one platform already holds,
    which is locked and deployed at platform's revision without being fetched.
    """
    _release(
        source,
        "0.1.0",
        "v0.1.0",
        folder="kit",
        dependencies=[{"name": "base", "version": "1.0.0"}],
    )
    _versions(api, "base", ("1.0.0", BASE_SHA))
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert f"  base 1.0.0 (acme): on Canvas Platform at {BASE_SHA[:12]}, required by kit" in (
        result.output
    )
    lock = _lock(root)["plugins"]
    assert list(lock) == ["kit", "base"]
    assert lock["base"] == {
        "version": "1.0.0",
        "publisher": "acme",
        "revision": BASE_SHA,
        "required_by": ["kit"],
    }
    assert lock["kit"]["source"]["tag"] == "v0.1.0"
    plugins = _deployments(api)[0]["plugins"]
    assert [p["name"] for p in plugins] == [ROOT, "kit", "base"]
    assert plugins[2]["ref"] == BASE_SHA


def test_deploy_takes_a_version_platform_holds_without_fetching(
    api: requests_mock_module.Mocker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exact version platform holds is deployed at its newest revision, and its source is
    not contacted.
    """
    monkeypatch.setattr(git, "ls_remote_tags", _no_git_remote)
    _versions(api, "kit", ("0.2.0", "c" * 40), ("0.2.0", "d" * 40), ("0.1.0", "e" * 40))
    root = _root(tmp_path, _kit("0.2.0"))

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _deployments(api)[0]["plugins"][1] == {
        "name": "kit",
        "ref": "c" * 40,
        "publisher": "acme",
    }
    assert _lock(root)["plugins"]["kit"]["source"] == {"git": SOURCE}


def test_deploy_installs_what_the_lock_names(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With a lock, a later deploy uses the locked revision even when a newer release exists,
    and does not contact the source while platform holds the revision.
    """
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())
    assert runner.invoke(app, ["deploy", str(root), "--push-only"]).exit_code == 0
    _commit_lock(root)
    locked = _lock(root)["plugins"]["kit"]["revision"]
    _release(source, "0.2.0", "v0.2.0", folder="kit")
    _versions(api, "kit", ("0.1.0", locked))
    monkeypatch.setattr(git, "ls_remote_tags", _no_git_remote)

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert "kit 0.1.0 (acme): on Canvas Platform at" in result.output
    assert ", as locked" in result.output
    assert _deployments(api)[0]["plugins"][1]["ref"] == locked


def test_deploy_update_resolves_again_and_rewrites_the_lock(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """--update ignores the lock, fetches the newer release and locks it."""
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())
    assert runner.invoke(app, ["deploy", str(root), "--push-only"]).exit_code == 0
    _commit_lock(root)
    first = _lock(root)["plugins"]["kit"]["revision"]
    newer = _release(source, "0.2.0", "v0.2.0", folder="kit")
    _versions(api, "kit", ("0.1.0", first))

    result = runner.invoke(app, ["deploy", str(root), "--update", "--push-only"])

    assert result.exit_code == 0, result.output
    entry = _lock(root)["plugins"]["kit"]
    assert (entry["version"], entry["source"]["commit"]) == ("0.2.0", newer)
    assert entry["revision"] == _git(_server(tmp_path, "kit"), "rev-parse", "main") != first
    assert not _deployments(api)


def test_deploy_resolves_again_a_lock_entry_the_manifest_no_longer_accepts(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A locked version outside the manifest's requirement is resolved again."""
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())
    assert runner.invoke(app, ["deploy", str(root), "--push-only"]).exit_code == 0
    _commit_lock(root)
    _release(source, "0.2.0", "v0.2.0", folder="kit")
    _require(root, _kit(">=0.2,<1"))

    result = runner.invoke(app, ["deploy", str(root), "--push-only", "--yes"])

    assert result.exit_code == 0, result.output
    assert _lock(root)["plugins"]["kit"]["version"] == "0.2.0"


def test_deploy_refuses_a_locked_tag_that_moved(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A locked version platform lacks is fetched again only from the commit the lock names; a
    tag moved since is refused before anything is cloned or pushed.
    """
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())
    assert runner.invoke(app, ["deploy", str(root), "--push-only"]).exit_code == 0
    _commit_lock(root)
    locked = _lock(root)["plugins"]["kit"]["source"]["commit"]
    moved = _release(source, "0.1.0", "v0.1.0-new", folder="kit", description="Moved.")
    _git(source, "tag", "-f", "-a", "v0.1.0", "-m", "moved", moved)

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "now points at" in result.output
    assert locked[:12] in result.output
    assert not _deployments(api)


def test_deploy_fetches_a_locked_version_platform_lacks_from_its_locked_commit(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A locked version platform does not hold, such as on another platform, is fetched from
    the locked tag and pushed, and the lock records the new revision.
    """
    commit = _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())
    (root / "CANVAS_LOCK.json").write_text(
        json.dumps(
            {
                "lock_version": 1,
                "plugins": {
                    "kit": {
                        "version": "0.1.0",
                        "publisher": "acme",
                        "source": {"git": SOURCE, "tag": "v0.1.0", "commit": commit},
                        "revision": "f" * 40,
                        "required_by": [ROOT],
                    }
                },
            }
        )
    )

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging", "--yes"])

    assert result.exit_code == 0, result.output
    revision = _git(_server(tmp_path, "kit"), "rev-parse", "main")
    assert _lock(root)["plugins"]["kit"]["revision"] == revision
    assert _deployments(api)[0]["plugins"][1]["ref"] == revision


def test_deploy_refuses_a_dependency_cycle(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A fetched plugin that requires the plugin being deployed is a cycle, refused before
    anything is pushed.
    """
    _release(
        source, "0.1.0", "v0.1.0", folder="kit", dependencies=[{"name": ROOT, "version": ">=1"}]
    )
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert f"cycle: {ROOT} -> kit -> {ROOT}" in result.output
    assert not _server(tmp_path, "kit").exists()


def test_deploy_never_fetches_for_another_publisher(
    api: requests_mock_module.Mocker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A dependency another organization publishes must already be on platform; its source is
    not contacted and nothing is pushed.
    """
    monkeypatch.setattr(git, "ls_remote_tags", _no_git_remote)
    api.get(
        f"{API}/plugins/kit/versions?publisher=beta",
        status_code=404,
        json={"error": "Not found.", "code": "not_found"},
    )
    root = _root(tmp_path, {**_kit(), "publisher": "beta"})

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "its publisher, beta, is not an organization you can push" in result.output
    assert not _deployments(api)


def test_deploy_refuses_a_tag_holding_another_version(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A release tag whose manifest names another version is refused."""
    _release(source, "0.1.1", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "holds kit 0.1.1, not kit 0.1.0" in result.output
    assert not _deployments(api)


def _other_repository(tmp_path: Path) -> str:
    """A second repository, ``other.git``, releasing plugin ``other`` 1.0.0; its address."""
    repo = tmp_path / "remotes" / "other.git"
    repo.mkdir(parents=True)
    _git(repo, "init", "--initial-branch=main")
    (repo / "CANVAS_MANIFEST.json").write_text(json.dumps(_manifest("other", "1.0.0")))
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Release 1.0.0")
    _git(repo, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
    return "https://git.example.com/acme/other.git"


def test_deploy_never_fetches_from_a_repository_only_a_fetched_plugin_names(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A fetched plugin's manifest cannot have deploy clone another repository and push it
    into the person's organization; the refusal says how to allow it.
    """
    other = _other_repository(tmp_path)
    _release(
        source,
        "0.1.0",
        "v0.1.0",
        folder="kit",
        dependencies=[{"name": "other", "version": ">=1", "source": {"git": other}}],
    )
    api.get(f"{API}/plugins/other/versions", status_code=404, json={"code": "not_found"})
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "only kit names a source for it" in result.output
    assert not _server(tmp_path, "other").exists()
    assert not _server(tmp_path, "kit").exists()
    assert _deployments(api) == []


def test_deploy_fetches_a_nested_dependency_from_a_repository_the_manifest_names(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """Naming the repository in the deploying manifest is what allows fetching from it."""
    other = _other_repository(tmp_path)
    _release(
        source,
        "0.1.0",
        "v0.1.0",
        folder="kit",
        dependencies=[{"name": "other", "version": ">=1", "source": {"git": other}}],
    )
    api.get(f"{API}/plugins/other/versions", status_code=404, json={"code": "not_found"})
    root = _root(tmp_path, _kit(), {"name": "other", "version": ">=1", "source": {"git": other}})

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _server(tmp_path, "other").exists()
    assert set(_lock(root)["plugins"]) == {"kit", "other"}


def test_deploy_fetches_from_the_source_the_manifest_declares_not_a_nested_one(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """A fetched plugin naming another address for a dependency the deploying manifest
    declares is ignored: the clone comes from the declared source, exactly as written.
    """
    other = _other_repository(tmp_path)
    _release(
        source,
        "0.1.0",
        "v0.1.0",
        folder="kit",
        dependencies=[
            {"name": "other", "version": ">=1", "source": {"git": other.replace("other", "OTHER")}}
        ],
    )
    api.get(f"{API}/plugins/other/versions", status_code=404, json={"code": "not_found"})
    root = _root(tmp_path, _kit(), {"name": "other", "version": ">=1", "source": {"git": other}})

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 0, result.output
    assert _lock(root)["plugins"]["other"]["source"]["git"] == other


def test_deploy_refuses_a_dependency_with_no_version_anywhere(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """With no matching version on platform or tag in the source, deploy names the requirement."""
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit(">=2"))

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"])

    assert result.exit_code == 2
    assert "no release tag in" in result.output
    assert "'>=2'" in result.output


def test_deploy_push_only_pushes_and_locks_dependencies_and_deploys_nothing(
    api: requests_mock_module.Mocker, source: Path, tmp_path: Path
) -> None:
    """--push-only pushes the dependencies and the plugin and writes the lock, deploying none."""
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--push-only"])

    assert result.exit_code == 0, result.output
    assert _git(_server(tmp_path, "kit"), "rev-parse", "main")
    assert _git(_server(tmp_path, ROOT), "rev-parse", "main") == _git(root, "rev-parse", "HEAD")
    assert "kit" in _lock(root)["plugins"]
    assert not _deployments(api)
    assert not [r for r in api.request_history if r.path.endswith("/instances")]


def test_deploy_stops_when_the_plan_is_declined_at_a_terminal(
    api: requests_mock_module.Mocker,
    source: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """At a terminal, declining the printed plan pushes nothing and writes no lock."""
    monkeypatch.setattr(git, "interactive", lambda: True)
    _release(source, "0.1.0", "v0.1.0", folder="kit")
    root = _root(tmp_path, _kit())

    result = runner.invoke(app, ["deploy", str(root), "--instance", "acme-staging"], input="n\n")

    assert result.exit_code == 1
    assert "Continue?" in result.output
    assert not _server(tmp_path, "kit").exists()
    assert not _server(tmp_path, ROOT).exists()
    assert not (root / "CANVAS_LOCK.json").exists()
