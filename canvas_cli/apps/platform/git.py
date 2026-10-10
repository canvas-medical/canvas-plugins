"""git plumbing for publishing a plugin to Canvas Platform's git server.

A plugin's repository is rooted one level above its package, the ``canvas init``
layout ``<repo>/<package>/CANVAS_MANIFEST.json``, and platform's git server is
the repository's ``origin``. Pushes authenticate through ``canvas git-credential``,
which git runs as the credential helper registered for the git server's host.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import click
import typer

REMOTE = "origin"


class GitError(click.ClickException):
    """A git command that failed or could not run.

    It is a failure of the operation, not of what the person typed, so it is
    reported without the command's usage line.
    """


def run(
    directory: Path,
    *args: str,
    isolate_config: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a git command in ``directory``.

    ``isolate_config`` points ``GIT_CONFIG_GLOBAL``/``GIT_CONFIG_SYSTEM`` at
    ``/dev/null`` so git reads only the repository's own ``.git/config``. The
    network operations use it, so that nothing above the repository (the macOS
    ``osxkeychain`` helper, a stale ``http.<host>.extraHeader``) can shadow the
    credential helper registered for the git server and fail the push with a
    401. It requires git 2.32 or newer; older git ignores the variables.

    Operations that need the person's identity or transport settings stay
    unisolated: ``commit`` reads ``user.name``/``user.email`` from global config.
    """
    env = {**os.environ}
    if isolate_config:
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def interactive() -> bool:
    """Whether a person is at the terminal to answer a prompt."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def require_installed() -> None:
    """Fail with an actionable message when git is not on PATH."""
    if shutil.which("git") is None:
        raise GitError(
            "git was not found on your PATH. Publishing a plugin to Canvas Platform uses "
            "git. Install it from https://git-scm.com/downloads and try again."
        )


def repo_root(plugin_dir: Path) -> Path:
    """The repository root for a plugin package: its parent directory."""
    return plugin_dir.resolve().parent


def in_repo(directory: Path) -> bool:
    """Whether ``directory`` is inside a git work tree."""
    return run(directory, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"


def ensure_repo(plugin_dir: Path) -> None:
    """Ensure the plugin is in a git repository, offering to create one at a TTY.

    The offer names the exact directory, the package's parent, so the person can
    catch a parent that is a shared folder of many plugins they do not want swept
    into one repository. Without a TTY it refuses rather than initializing a
    possibly shared parent unattended.
    """
    require_installed()
    if in_repo(plugin_dir):
        return
    root = repo_root(plugin_dir)
    if not interactive():
        raise typer.BadParameter(
            f"'{plugin_dir}' is not in a git repository. Canvas Platform hosts your "
            f"plugin's git repository, so it must live in one. Run `git init` in the "
            f"repository root ({root}), the directory containing the plugin package, "
            "then try again."
        )

    print(f"'{plugin_dir}' is not in a git repository.")
    if not typer.confirm(
        f"Initialize a git repository at {root} (the plugin's repository root) and continue?",
        default=False,
    ):
        raise typer.Abort()
    result = run(root, "init")
    if result.returncode != 0:
        raise GitError(f"git init failed: {result.stderr.strip()}")
    print(f"Initialized a git repository at {root}.")


def url_origin(url: str) -> str:
    """``scheme://host`` of a URL, the scope a credential helper is registered for."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def credential_helper_command(platform: str) -> str:
    """The helper git runs, by absolute path to this ``canvas``.

    git runs it through a shell, so a bare ``canvas`` works only when it is on
    PATH, which it is not under a virtualenv or ``uv run``.
    """
    canvas_bin = shutil.which(sys.argv[0]) or sys.argv[0]
    return f"!{shlex.quote(canvas_bin)} git-credential --platform {shlex.quote(platform)}"


def credential_config(git_url: str, platform: str) -> list[tuple[str, str]]:
    """The git config that sends a git server's credential requests to ``canvas``, in order.

    The empty helper comes first because git runs every helper configured for a
    URL, system ones included: on macOS that is ``osxkeychain``, which would
    otherwise answer with a stale password and store each short-lived token in the
    keychain. An empty value resets the list, so only ``canvas`` answers. Every
    entry is added rather than replaced, since the helper key holds both.

    ``useHttpPath`` makes git include the repository path in the request, which
    is how the helper knows which plugin to mint a token for.
    """
    host = url_origin(git_url)
    return [
        (f"credential.{host}.helper", ""),
        (f"credential.{host}.helper", credential_helper_command(platform)),
        (f"credential.{host}.useHttpPath", "true"),
    ]


def connect_remote(repo: Path, git_url: str, platform: str) -> None:
    """Point ``origin`` at the plugin's repository and register the credential helper.

    Idempotent: each key is cleared before its entries are added, so repeat runs
    leave the same configuration.
    """
    if run(repo, "remote", "get-url", REMOTE).returncode == 0:
        result = run(repo, "remote", "set-url", REMOTE, git_url)
    else:
        result = run(repo, "remote", "add", REMOTE, git_url)
    if result.returncode != 0:
        raise GitError(f"Could not set the '{REMOTE}' remote: {result.stderr.strip()}")
    entries = credential_config(git_url, platform)
    for key in dict.fromkeys(key for key, _ in entries):
        # Exit status 5 is "nothing to unset", which a first run always is.
        result = run(repo, "config", "--unset-all", key)
        if result.returncode not in (0, 5):
            raise GitError(f"Could not clear {key}: {result.stderr.strip()}")
    for key, value in entries:
        result = run(repo, "config", "--add", key, value)
        if result.returncode != 0:
            raise GitError(f"Could not set {key}: {result.stderr.strip()}")


DEFAULT_COMMIT_MESSAGE = "Deploy via canvas"


def commit_working_tree(plugin_dir: Path, *, assume_yes: bool) -> None:
    """Stage and commit uncommitted changes, after the person confirms.

    ``git push`` sends only commits, so deploying the working tree means
    committing it first. ``assume_yes`` answers the confirmation and takes the
    default commit message. Without it and without a TTY a dirty tree is an
    error, because committing someone's working tree unasked is surprising and
    hard to undo.
    """
    status = run(plugin_dir, "status", "--porcelain")
    if status.returncode != 0:
        raise GitError(f"git status failed: {status.stderr.strip()}")
    if not status.stdout.strip():
        return

    if not assume_yes and not interactive():
        raise typer.BadParameter(
            "You have uncommitted changes, and deploy only pushes committed work. "
            "Commit them and run deploy again, pass --yes to commit them, or pass "
            "--ref / --no-push to deploy a ref that is already pushed."
        )

    print("Uncommitted changes to be committed and deployed:")
    print(status.stdout.rstrip())
    if assume_yes:
        message = DEFAULT_COMMIT_MESSAGE
    else:
        if not typer.confirm("Commit these and deploy?", default=True):
            raise typer.Abort()
        message = typer.prompt("Commit message", default=DEFAULT_COMMIT_MESSAGE)

    add = run(plugin_dir, "add", "-A")
    if add.returncode != 0:
        raise GitError(f"git add failed: {add.stderr.strip()}")
    commit = run(plugin_dir, "commit", "-m", message)
    if commit.returncode != 0:
        raise GitError(f"git commit failed: {commit.stderr.strip()}")


def head_sha(plugin_dir: Path) -> str:
    """The commit HEAD points at."""
    result = run(plugin_dir, "rev-parse", "HEAD")
    if result.returncode != 0:
        raise GitError(
            "This repository has no commits yet. Commit the plugin and run deploy again."
        )
    return result.stdout.strip()


def push_head(plugin_dir: Path, branch: str) -> None:
    """Push HEAD to ``branch`` on ``origin``, with global and system config ignored."""
    result = run(plugin_dir, "push", REMOTE, f"HEAD:refs/heads/{branch}", isolate_config=True)
    if result.returncode != 0:
        raise GitError(
            "git push to Canvas Platform failed:\n" + (result.stderr.strip() or "unknown error")
        )


def clone(git_url: str, destination: Path, platform: str) -> None:
    """Clone a plugin's repository with the remote and credential helper preconfigured.

    ``git clone -c`` writes each setting into the new repository before the first
    fetch, so the clone itself authenticates through the helper.
    """
    settings = [
        arg
        for key, value in credential_config(git_url, platform)
        for arg in ("-c", f"{key}={value}")
    ]
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    result = subprocess.run(
        ["git", "clone", *settings, git_url, str(destination)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise GitError(f"git clone failed:\n{result.stderr.strip() or 'unknown error'}")
