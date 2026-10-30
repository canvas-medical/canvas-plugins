"""git plumbing for publishing a plugin to Canvas Platform's git server.

A plugin's repository is rooted one level above its package, the ``canvas init``
layout ``<repo>/<package>/CANVAS_MANIFEST.json``, and platform's git server is
the repository's ``origin``. Pushes authenticate through ``canvas git-credential``,
which git runs as the credential helper registered for the git server's host.

A plugin inside a larger repository, such as a monorepo, is published as a
snapshot instead: its committed package folder becomes the next commit on the
plugin's ``main``, or on the branch ``--branch`` names, built in a scratch repository so the larger repository's
remotes, config and index are never touched.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
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
    extra_env: dict[str, str] | None = None,
    input: str | None = None,
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
    env = {**os.environ, **(extra_env or {})}
    if isolate_config:
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        input=input,
    )


def _output(directory: Path, *args: str, what: str, **kwargs: Any) -> str:
    """The stdout of a git command that has to succeed; ``what`` names it in the error."""
    result = run(directory, *args, **kwargs)
    if result.returncode != 0:
        raise GitError(f"{what} failed: {result.stderr.strip() or 'unknown error'}")
    return result.stdout


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


# -- snapshots ---------------------------------------------------------------

SOURCE_TRAILER = "Monorepo-Commit"
# A commit tagged under this prefix, as Canvas Studio tags the commit it starts main from,
# counts as the last snapshot.
BASELINE_TAG_PREFIX = "snapshot-baseline/"
PATH_TRAILER = "Monorepo-Path"
SUBMODULE_MODE = "160000"
SYMLINK_MODE = "120000"


@dataclass(frozen=True)
class Snapshot:
    """A plugin package's committed contents in the repository that holds it."""

    toplevel: Path
    path: str  # the package folder, relative to ``toplevel``
    commit: str
    tree: str  # the package folder's tree at ``commit``


def snapshot_source(plugin_dir: Path) -> Snapshot:
    """The committed package to snapshot, refusing what a snapshot cannot carry.

    A snapshot is built from commits, so uncommitted changes under the package are
    refused rather than committed: committing in a shared repository is not this
    command's call. Submodules, symbolic links and files stored through a filter
    (Git LFS, git-crypt) are refused by path, because each would reach an instance
    as something other than its content: a commit Canvas Platform does not have, a
    file holding the link's target, or the filter's stored form.
    """
    require_installed()
    package = plugin_dir.resolve()
    if not in_repo(package):
        raise typer.BadParameter(
            "--snapshot deploys the committed contents of a plugin in a git repository, "
            f"and '{plugin_dir}' is not in one."
        )
    status = _output(
        package, "status", "--porcelain", "--untracked-files=all", "--", ".", what="git status"
    )
    if status.strip():
        raise typer.BadParameter(
            "--snapshot deploys only committed work, and the plugin has uncommitted "
            f"changes:\n{status.rstrip()}\nCommit them and run deploy again."
        )
    tree = run(package, "rev-parse", "--verify", "-q", "HEAD:./").stdout.strip()
    if not tree:
        raise typer.BadParameter(
            f"'{plugin_dir}' has no committed files. Commit the plugin and run deploy again."
        )

    problems: list[str] = []
    files: list[str] = []
    # --full-tree, because below the top level ls-tree keeps only paths under the cwd.
    listing = _output(package, "ls-tree", "--full-tree", "-r", "-z", tree, what="git ls-tree")
    for entry in listing.split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode = meta.split(" ", 1)[0]
        if mode == SUBMODULE_MODE:
            problems.append(f"{path} is a submodule, whose files are not in this repository")
        elif mode == SYMLINK_MODE:
            problems.append(
                f"{path} is a symbolic link, which an instance installs as a file holding "
                "the link's target"
            )
        else:
            files.append(path)
    # `check-attr -z` answers in triples: path, attribute, value.
    answers = _output(
        package,
        "check-attr",
        "-z",
        "--stdin",
        "filter",
        input="".join(f"{path}\0" for path in files),
        what="git check-attr",
    ).split("\0")
    # A filter attribute that names a driver means git stores the driver's output,
    # such as an LFS pointer or git-crypt ciphertext; set, unset or unspecified
    # names none and changes nothing.
    problems += [
        f"{path} is stored through the '{value}' filter, so what git stores for it, such as an "
        "LFS pointer or ciphertext, would be deployed instead of the file"
        for path, value in zip(answers[0::3], answers[2::3], strict=False)
        if value not in ("set", "unset", "unspecified")
    ]
    if problems:
        raise typer.BadParameter(
            "--snapshot cannot deploy this plugin as committed:\n"
            + "\n".join(f"  {problem}" for problem in problems)
        )

    return Snapshot(
        toplevel=Path(
            _output(package, "rev-parse", "--show-toplevel", what="git rev-parse").strip()
        ),
        path=_output(package, "rev-parse", "--show-prefix", what="git rev-parse")
        .strip()
        .rstrip("/"),
        commit=_output(package, "rev-parse", "HEAD", what="git rev-parse").strip(),
        tree=tree,
    )


def on_a_remote(directory: Path) -> bool:
    """Whether a remote-tracking branch contains HEAD, that is, HEAD has been pushed."""
    return bool(run(directory, "branch", "-r", "--contains", "HEAD").stdout.strip())


def push_snapshot(
    snapshot: Snapshot,
    name: str,
    git_url: str,
    branch: str,
    platform: str,
    *,
    author: tuple[str, str],
    default_branch: str | None = None,
) -> str:
    """Commit the snapshot onto ``branch`` of the plugin's repository, push it, and return it.

    The work happens in a scratch repository that borrows the source repository's
    objects through ``objects/info/alternates`` rather than copying them, and that
    holds the credential helper itself. The snapshot replaces the ``name`` folder on
    ``branch`` and keeps everything else at its root. When the contents are
    unchanged nothing is pushed, and the commit already on ``branch`` is returned.

    ``default_branch`` is the plugin's default branch, which ``branch`` defaults to.
    A ``branch`` that Canvas Platform does not have yet continues from the default
    branch's tip, and the checks against edits made on Canvas Platform and against
    rolling back always read the default branch. Unchanged contents on a new
    ``branch`` push the default branch's commit to it without a new commit.

    ``author`` is the name and email the commit carries, set through the
    environment because a CI runner has no git identity of its own.
    """
    default_branch = default_branch or branch
    with tempfile.TemporaryDirectory(prefix="canvas-snapshot-") as scratch:
        work = Path(scratch)
        _output(work, "init", "--bare", "-q", what="git init")
        objects = (
            snapshot.toplevel
            / _output(
                snapshot.toplevel, "rev-parse", "--git-path", "objects", what="git rev-parse"
            ).strip()
        )
        (work / "objects" / "info" / "alternates").write_text(f"{objects.resolve()}\n")
        for key, value in credential_config(git_url, platform):
            _output(work, "config", "--add", key, value, what=f"Setting {key}")

        # Every branch and baseline tag, so a repository with none yet fetches nothing
        # rather than failing. --no-tags keeps other tags out.
        fetch = run(
            work,
            "fetch",
            "-q",
            "--no-tags",
            git_url,
            "+refs/heads/*:refs/platform/*",
            f"+refs/tags/{BASELINE_TAG_PREFIX}*:refs/tags/{BASELINE_TAG_PREFIX}*",
            isolate_config=True,
        )
        if fetch.returncode != 0:
            raise GitError(
                "git fetch from Canvas Platform failed:\n"
                + (fetch.stderr.strip() or "unknown error")
            )
        target_tip = run(
            work, "rev-parse", "--verify", "-q", f"refs/platform/{branch}"
        ).stdout.strip()
        default_tip = run(
            work, "rev-parse", "--verify", "-q", f"refs/platform/{default_branch}"
        ).stdout.strip()
        tip = target_tip or default_tip

        kept = _output(work, "ls-tree", "-z", tip, what="git ls-tree").split("\0") if tip else []
        entries = [entry for entry in kept if entry and entry.split("\t", 1)[1] != name]
        entries.append(f"040000 tree {snapshot.tree}\t{name}")
        root = _output(
            work,
            "mktree",
            "-z",
            input="".join(f"{entry}\0" for entry in entries),
            what="git mktree",
        ).strip()

        if tip:
            if root == _output(work, "rev-parse", f"{tip}^{{tree}}", what="git rev-parse").strip():
                if tip == target_tip:
                    print(f"{branch} on Canvas Platform already holds this snapshot.")
                    return tip
                _push_ref(work, git_url, tip, branch)
                print(f"Pushed {tip[:12]} to {branch}, which already holds this snapshot.")
                return tip
            if default_tip:
                _guard_platform_history(work, snapshot, default_tip, name, root, default_branch)
            print(_output(work, "diff", "--stat", tip, root, what="git diff").rstrip())

        message = (
            f"Snapshot of {snapshot.path or '.'} at {snapshot.commit[:12]}\n\n"
            f"{SOURCE_TRAILER}: {snapshot.commit}\n"
            f"{PATH_TRAILER}: {snapshot.path or '.'}\n"
        )
        author_name, author_email = author
        identity = {
            "GIT_AUTHOR_NAME": author_name,
            "GIT_AUTHOR_EMAIL": author_email,
            "GIT_COMMITTER_NAME": author_name,
            "GIT_COMMITTER_EMAIL": author_email,
        }
        commit = _output(
            work,
            "commit-tree",
            root,
            *(["-p", tip] if tip else []),
            "-F",
            "-",
            input=message,
            extra_env=identity,
            isolate_config=True,
            what="git commit-tree",
        ).strip()

        _push_ref(work, git_url, commit, branch)
        print(f"Pushed {commit[:12]} to {branch}, a snapshot of {snapshot.commit[:12]}.")
        return commit


def _push_ref(work: Path, git_url: str, commit: str, branch: str) -> None:
    """Push ``commit`` to ``branch`` of the plugin's repository from the scratch repository."""
    push = run(work, "push", "-q", git_url, f"{commit}:refs/heads/{branch}", isolate_config=True)
    if push.returncode != 0:
        raise GitError(
            "git push to Canvas Platform failed:\n" + (push.stderr.strip() or "unknown error")
        )


def _paths(work: Path, *args: str) -> set[str]:
    return set(filter(None, _output(work, *args, what=f"git {args[0]}").split("\0")))


def _guard_platform_history(
    work: Path, snapshot: Snapshot, tip: str, name: str, root: str, branch: str
) -> None:
    """Refuse a snapshot that would undo work on ``branch`` that it does not hold.

    The last snapshot on ``branch`` is the newest commit on its first-parent chain
    that carries a ``Monorepo-Commit`` trailer or is tagged under
    ``snapshot-baseline/``, as the commit Canvas Studio starts ``main`` from is.
    A commit carrying both is read by its trailer.

    A snapshot names the commit it came from. When this checkout has that commit,
    every package file it changed since its common ancestor with HEAD must be
    changed on HEAD's side too; a file HEAD left alone would go back to its older
    content, rolling the plugin back. A branch deployed and then squash- or
    rebase-merged passes, because HEAD carries its changes under another commit.
    A commit that is only tagged names no source commit, so nothing is checked for
    rolling back.

    Files in the package folder changed on ``branch`` since the last snapshot, such
    as by editing the catalog listing in Canvas Platform, or every file when no
    snapshot was pushed before, are replaced wherever the snapshot differs. At a
    terminal the person may confirm that; otherwise it is refused.
    """
    found = _output(
        work,
        "log",
        "--first-parent",
        "--decorate=short",
        f"--decorate-refs=refs/tags/{BASELINE_TAG_PREFIX}",
        f"--format=%H%x00%D%x00%(trailers:key={SOURCE_TRAILER},valueonly,separator=%x2C)",
        tip,
        what="git log",
    )
    last = source = tag = ""
    for record in found.splitlines():
        commit, _, rest = record.partition("\0")
        refs, _, trailer = rest.partition("\0")
        if refs.strip() or trailer.strip():
            last, source = commit.strip(), trailer.strip()
            if not source:
                tag = refs.split(",")[0].strip().removeprefix("tag: ")
            break
    if source:
        if run(snapshot.toplevel, "cat-file", "-e", f"{source}^{{commit}}").returncode != 0:
            print(
                f"This checkout does not have {source[:12]}, the commit {branch} was last "
                "deployed from, so it is not checked whether this deploy rolls the plugin back. "
                "A checkout with full history, such as after `git fetch --unshallow`, is checked.",
                file=sys.stderr,
                flush=True,
            )
        else:
            top, package = snapshot.toplevel, snapshot.path or "."
            base = _output(top, "merge-base", source, snapshot.commit, what="git merge-base")
            deployed = _paths(top, "diff", "--name-only", "-z", base.strip(), source, "--", package)
            kept = _paths(
                top, "diff", "--name-only", "-z", base.strip(), snapshot.commit, "--", package
            )
            if missing := sorted(deployed - kept):
                raise GitError(
                    f"{branch} on Canvas Platform was last deployed from {source[:12]}, and HEAD "
                    f"({snapshot.commit[:12]}) lacks its changes to these files, so this deploy "
                    "would roll the plugin back:\n"
                    + "\n".join(f"  {path}" for path in missing)
                    + "\nUpdate this checkout to include them, such as with `git pull`, and run "
                    "deploy again."
                )

    if last:
        on_platform = _paths(work, "diff", "--name-only", "-z", last, tip, "--", name)
        since = (
            f"since {tag}, such as by editing its catalog listing"
            if tag
            else "since the last snapshot, such as by editing its catalog listing"
        )
    else:
        on_platform = _paths(work, "ls-tree", "-r", "--name-only", "-z", tip, name)
        since = "by pushes that were not snapshots"
    replaced = sorted(on_platform & _paths(work, "diff", "--name-only", "-z", tip, root))
    if not replaced:
        return
    changes = f"These files on {branch} were changed on Canvas Platform {since}:\n" + "\n".join(
        f"  {path}" for path in replaced
    )
    if interactive():
        print(changes)
        if not typer.confirm("Replace them with this snapshot's versions?", default=False):
            raise typer.Abort()
        return
    raise GitError(
        f"{changes}\nThis snapshot would replace them. Copy Canvas Platform's versions into "
        f"{snapshot.path or 'the plugin'} (`canvas clone {name}` checks them out) and commit "
        "them, or run deploy at a terminal to confirm replacing them."
    )
