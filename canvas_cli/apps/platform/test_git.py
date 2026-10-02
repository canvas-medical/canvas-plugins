"""Tests for the git plumbing behind publishing a plugin to Canvas Platform."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import typer

from canvas_cli.apps.platform import git

GIT = "canvas_cli.apps.platform.git"


def _completed(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _runs(*results: subprocess.CompletedProcess[str]) -> Any:
    """A stand-in for ``git.run`` that returns ``results`` in order."""
    remaining = iter(results)
    return patch(f"{GIT}.run", side_effect=lambda *a, **k: next(remaining))


@pytest.fixture
def plugin_dir(tmp_path: Path) -> Path:
    """A plugin package outside any git repository."""
    package = tmp_path / "repo" / "acme__hello"
    package.mkdir(parents=True)
    (package / "CANVAS_MANIFEST.json").write_text("{}")
    return package


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """An empty git repository with an identity for commits."""
    root = tmp_path / "work"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
    return root


def test_require_installed_names_where_to_get_git() -> None:
    """A missing git binary is an actionable error."""
    with (
        patch(f"{GIT}.shutil.which", return_value=None),
        pytest.raises(typer.BadParameter, match="git was not found"),
    ):
        git.require_installed()


def test_ensure_repo_refuses_to_init_without_a_terminal(plugin_dir: Path) -> None:
    """Without a TTY it refuses instead of initializing a possibly shared parent."""
    with (
        patch(f"{GIT}.in_repo", return_value=False),
        patch(f"{GIT}.interactive", return_value=False),
        pytest.raises(typer.BadParameter, match="is not in a git repository"),
    ):
        git.ensure_repo(plugin_dir)
    assert not (plugin_dir.parent / ".git").exists()


def test_ensure_repo_aborts_when_the_person_declines(plugin_dir: Path) -> None:
    """Declining the offer leaves the directory alone."""
    with (
        patch(f"{GIT}.in_repo", return_value=False),
        patch(f"{GIT}.interactive", return_value=True),
        patch(f"{GIT}.typer.confirm", return_value=False),
        pytest.raises(typer.Abort),
    ):
        git.ensure_repo(plugin_dir)
    assert not (plugin_dir.parent / ".git").exists()


def test_ensure_repo_initializes_the_repository_root_after_confirmation(plugin_dir: Path) -> None:
    """Accepting the offer runs git init in the package's parent."""
    with (
        patch(f"{GIT}.in_repo", return_value=False),
        patch(f"{GIT}.interactive", return_value=True),
        patch(f"{GIT}.typer.confirm", return_value=True),
    ):
        git.ensure_repo(plugin_dir)
    assert (plugin_dir.parent / ".git").is_dir()


def test_ensure_repo_surfaces_a_failed_git_init(plugin_dir: Path) -> None:
    """A failing git init reports git's stderr."""
    with (
        patch(f"{GIT}.in_repo", return_value=False),
        patch(f"{GIT}.interactive", return_value=True),
        patch(f"{GIT}.typer.confirm", return_value=True),
        patch(f"{GIT}.run", return_value=_completed(1, stderr="boom")),
        pytest.raises(typer.BadParameter, match="git init failed: boom"),
    ):
        git.ensure_repo(plugin_dir)


def test_connect_remote_replaces_an_existing_origin(repo: Path) -> None:
    """An existing origin is repointed rather than added twice."""
    git.run(repo, "remote", "add", "origin", "https://old.example.com/x.git")
    git.connect_remote(
        repo, "https://git.example.com/acme__hello.git", "https://platform.example.com"
    )
    assert git.run(repo, "remote", "get-url", "origin").stdout.strip() == (
        "https://git.example.com/acme__hello.git"
    )


def test_connect_remote_surfaces_a_remote_failure(repo: Path) -> None:
    """A failure to add the remote reports git's stderr."""
    with (
        patch(f"{GIT}.run", return_value=_completed(2, stderr="nope")),
        pytest.raises(typer.BadParameter, match="Could not set the 'origin' remote: nope"),
    ):
        git.connect_remote(repo, "https://git.example.com/x.git", "https://p.example.com")


def test_connect_remote_surfaces_a_failure_to_clear_config(repo: Path) -> None:
    """An --unset-all failure other than exit 5 is an error."""
    with (
        _runs(_completed(0), _completed(0), _completed(3, stderr="locked")),
        pytest.raises(typer.BadParameter, match="Could not clear credential.*locked"),
    ):
        git.connect_remote(repo, "https://git.example.com/x.git", "https://p.example.com")


def test_connect_remote_surfaces_a_failure_to_set_config(repo: Path) -> None:
    """A failing --add reports which key could not be set."""
    # get-url, set-url, two --unset-all (helper, useHttpPath), then the first --add fails.
    with (
        _runs(*[_completed(0)] * 4, _completed(1, stderr="readonly")),
        pytest.raises(typer.BadParameter, match="Could not set credential.*readonly"),
    ):
        git.connect_remote(repo, "https://git.example.com/x.git", "https://p.example.com")


def test_commit_working_tree_surfaces_a_failed_status(tmp_path: Path) -> None:
    """A failing git status (here, no such directory) is an error."""
    with pytest.raises(typer.BadParameter, match="git status failed"):
        git.commit_working_tree(tmp_path / "missing", assume_yes=True)


def test_commit_working_tree_aborts_when_the_person_declines(repo: Path) -> None:
    """Declining the commit confirmation commits nothing."""
    (repo / "a.txt").write_text("a")
    with (
        patch(f"{GIT}.interactive", return_value=True),
        patch(f"{GIT}.typer.confirm", return_value=False),
        pytest.raises(typer.Abort),
    ):
        git.commit_working_tree(repo, assume_yes=False)
    assert git.run(repo, "rev-parse", "HEAD").returncode != 0


def test_commit_working_tree_surfaces_a_failed_add(repo: Path) -> None:
    """A failing git add reports git's stderr."""
    with (
        _runs(_completed(0, stdout="?? a.txt\n"), _completed(1, stderr="index locked")),
        pytest.raises(typer.BadParameter, match="git add failed: index locked"),
    ):
        git.commit_working_tree(repo, assume_yes=True)


def test_commit_working_tree_surfaces_a_failed_commit(repo: Path) -> None:
    """A failing git commit reports git's stderr."""
    with (
        _runs(
            _completed(0, stdout="?? a.txt\n"),
            _completed(0),
            _completed(1, stderr="no identity"),
        ),
        pytest.raises(typer.BadParameter, match="git commit failed: no identity"),
    ):
        git.commit_working_tree(repo, assume_yes=True)


def test_head_sha_of_a_repository_without_commits(repo: Path) -> None:
    """An unborn HEAD asks the person to commit first."""
    with pytest.raises(typer.BadParameter, match="no commits yet"):
        git.head_sha(repo)


def test_push_head_surfaces_the_push_error(repo: Path) -> None:
    """A rejected push reports the failure."""
    (repo / "a.txt").write_text("a")
    git.commit_working_tree(repo, assume_yes=True)
    git.run(repo, "remote", "add", "origin", str(repo.parent / "does-not-exist.git"))
    with pytest.raises(typer.BadParameter, match="git push to Canvas Platform failed"):
        git.push_head(repo, "main")


def test_clone_surfaces_the_clone_error(tmp_path: Path) -> None:
    """A failed clone reports the failure."""
    with pytest.raises(typer.BadParameter, match="git clone failed"):
        git.clone(str(tmp_path / "does-not-exist.git"), tmp_path / "dest", "https://p.example.com")
