"""Headless publish/pull via Control Room (KOALA-5923).

The `canvas` CLI never talks to Control Room directly — it goes through the
developer's own Canvas instance (home-app), which proxies to Control Room and
signs short-lived JWTs on the developer's behalf. Git is an implementation
detail: `canvas publish` discovers the Control Room git server + org from the
instance, configures a `cr` remote and a credential helper transparently, and
pushes. The plugin author never types a git URL, an org, or a git command.

Commands (registered behind CONTROL_ROOM_BETA in canvas_cli.main):

  * ``canvas git-credential`` — hidden git credential helper; git invokes it to
    mint a push credential via the instance's ``mint-git-jwt`` endpoint.
  * ``canvas publish`` — push the plugin's current HEAD to Control Room.
  * ``canvas pull`` — integrate Control Room changes (e.g. a Canvas Support fix).
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import typer

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token

_TIMEOUT_SECONDS = 30


# -- Control Room endpoint helpers -------------------------------------------


def _cr_url(host: str, *paths: str) -> str:
    """Build a ``/plugin-io/control-room/...`` URL (mirrors plugin_url)."""
    join = "/".join(["plugin-io/control-room", *paths])
    if not join.endswith("/"):
        join += "/"
    return urljoin(host, join)


def _control_room_info(host: str, token: str) -> tuple[str, str]:
    """Discover the CR git server URL + this instance's org slug.

    Returns ``(git_url, org_slug)``. Raises ``typer.BadParameter`` on any
    failure (unreachable, unconfigured instance, unassigned org).
    """
    try:
        resp = requests.get(
            _cr_url(host, "info"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise typer.BadParameter(f"Could not reach {host}: {exc}") from exc

    if resp.status_code != requests.codes.ok:
        detail = _error_detail(resp)
        raise typer.BadParameter(
            f"Control Room is not available on {host} ({resp.status_code}): {detail}"
        )

    data = resp.json()
    return data["git_url"], data["org_slug"]


def _error_detail(resp: requests.Response) -> str:
    """Best-effort human-readable error from a JSON ``{error}`` body."""
    try:
        return str(resp.json().get("error", resp.text))
    except ValueError:
        return resp.text


def _consent_url(host: str, request_id: int, action: str) -> str:
    """Build a ``/plugin-io/consent/<id>/<action>/`` URL."""
    return urljoin(host, f"plugin-io/consent/{request_id}/{action}/")


def _post(host: str, token: str, url: str, body: dict[str, object] | None = None) -> dict:
    """POST to a Control Room proxy endpoint and return the parsed JSON body.

    Raises ``typer.BadParameter`` on transport failure or a non-200 (the proxy
    surfaces CR *business* failures as HTTP 200 with ``ok: false``, which the
    caller inspects).
    """
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json=body,
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise typer.BadParameter(f"Could not reach {host}: {exc}") from exc
    if resp.status_code != requests.codes.ok:
        raise typer.BadParameter(f"Control Room error ({resp.status_code}): {_error_detail(resp)}")
    return resp.json()


# -- git plumbing (all transparent to the author) ----------------------------


def _git(
    plugin_dir: Path,
    *args: str,
    isolate_config: bool = False,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a git command scoped to the plugin repo.

    ``isolate_config`` points ``GIT_CONFIG_GLOBAL``/``GIT_CONFIG_SYSTEM`` at
    ``/dev/null`` so git reads only the repo-local ``.git/config``. Use it for
    the network operations (``push``/``fetch``): it structurally prevents
    anything above the repo — a stale ``cr-login`` ``http.<host>.extraHeader``
    (in any slash form) or the macOS ``osxkeychain`` credential helper — from
    shadowing the credential helper we register and 401ing the push. Requires
    git >= 2.32; older git ignores the vars and falls back to global config.

    Do **not** isolate operations that need the user's identity or transport
    config: ``merge`` reads ``user.name``/``user.email`` from global config, and
    a push behind a corporate proxy / custom CA would lose ``http.proxy`` /
    ``http.sslCAInfo``. Only the auth-during-network path needs isolation.
    """
    env = {**os.environ}
    if isolate_config:
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["git", "-C", str(plugin_dir), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _require_git_installed() -> None:
    """Fail with an actionable message when git isn't on PATH.

    The headless flow keeps git invisible to plugin authors, so a missing git
    would otherwise surface as a raw ``FileNotFoundError`` from ``subprocess``
    (``check=False`` doesn't suppress it — it's raised at spawn time) with no
    hint that the fix is to install git. ``publish``/``pull`` shell out to git;
    ``deploy`` is HTTP-only and never reaches here.
    """
    if shutil.which("git") is None:
        raise typer.BadParameter(
            "git was not found on your PATH. `canvas publish` and `canvas pull` "
            "use git to sync your plugin with Control Room. Install it from "
            "https://git-scm.com/downloads and try again."
        )


def _require_git_repo(plugin_dir: Path) -> None:
    _require_git_installed()
    result = _git(plugin_dir, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise typer.BadParameter(
            f"'{plugin_dir}' is not a git repository. `canvas publish` pushes your "
            "plugin's git history to Control Room, so the plugin must live in a git repo."
        )


# Per-file size ceiling for a publish. Mirrors Control Room's default
# GIT_MAX_PUSH_BYTES (25 MB) so the CLI never rejects a file CR would accept —
# a single file this large can't fit under CR's per-push cap anyway. This is an
# early, friendly client-side check; CR enforces the real limit server-side.
_MAX_PUBLISH_FILE_BYTES = 25 * 1024 * 1024


def _reject_oversized_staged_files(plugin_dir: Path) -> None:
    """Refuse to snapshot a file too large to publish, before committing/pushing.

    Ergonomics for the honest author who accidentally staged a build artifact,
    dataset, model weights, or a committed virtualenv: fail fast locally with the
    offending paths instead of eating a round-trip to Control Room's 413. Not a
    security boundary — a determined client bypasses the CLI — which is why CR
    also caps the push server-side.
    """
    root = _git(plugin_dir, "rev-parse", "--show-toplevel").stdout.strip() or str(plugin_dir)
    names = _git(
        plugin_dir, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"
    ).stdout
    offending: list[tuple[str, int]] = []
    for rel in names.split("\0"):
        if not rel:
            continue
        try:
            size = (Path(root) / rel).stat().st_size
        except OSError:
            continue  # deletions / unreadable — not a size concern
        if size > _MAX_PUBLISH_FILE_BYTES:
            offending.append((rel, size))

    if offending:
        limit_mb = _MAX_PUBLISH_FILE_BYTES // (1024 * 1024)
        listing = "\n".join(f"  {path} ({size / 1024 / 1024:.1f} MB)" for path, size in offending)
        raise typer.BadParameter(
            f"These files are too large to publish ({limit_mb} MB max per file):\n"
            f"{listing}\n"
            "Remove them (build artifacts, datasets, binaries) or add them to "
            ".gitignore, then publish again. Control Room enforces this server-side too."
        )


def _capture_working_tree(plugin_dir: Path, *, message: str | None) -> bool:
    """Stage and commit the working tree so ``publish`` ships what's on disk.

    Git stays invisible to plugin authors (KOALA-5923): they edit files and
    ``canvas publish`` — no ``git add`` / ``git commit`` in their vocabulary — so
    we snapshot the tree for them. ``git add -A`` picks up modifications, new
    files, and deletions. Returns ``True`` if a commit was made, ``False`` if the
    tree was already clean (nothing staged after the add).

    Identity: the author's configured ``user.name``/``user.email`` are used when
    set (so history is attributable); we fall back to a Canvas identity only for
    the field(s) they haven't configured, so an author who never set up git can
    still publish instead of hitting "committer identity unknown". The commit is
    deliberately NOT config-isolated, unlike the push, so that configured
    identity is visible.
    """
    _git(plugin_dir, "add", "-A")
    # `diff --cached --quiet` exits 0 when nothing is staged, 1 when there is a
    # diff to commit (covers a fresh repo with no HEAD too — staged vs the empty
    # tree is a diff).
    if _git(plugin_dir, "diff", "--cached", "--quiet").returncode == 0:
        return False

    _reject_oversized_staged_files(plugin_dir)

    identity: dict[str, str] = {}
    if not _git(plugin_dir, "config", "user.name").stdout.strip():
        identity["GIT_AUTHOR_NAME"] = identity["GIT_COMMITTER_NAME"] = "Canvas CLI"
    if not _git(plugin_dir, "config", "user.email").stdout.strip():
        identity["GIT_AUTHOR_EMAIL"] = identity["GIT_COMMITTER_EMAIL"] = (
            "canvas-cli@canvasmedical.com"
        )

    commit_message = message or (
        f"Publish via canvas CLI ({time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})"
    )
    committed = _git(plugin_dir, "commit", "-m", commit_message, extra_env=identity or None)
    if committed.returncode != 0:
        print(committed.stderr or committed.stdout or "git commit failed", file=sys.stderr)
        raise typer.Exit(1)
    return True


def _url_origin(url: str) -> str:
    """``scheme://host`` for credential-helper scoping."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _ensure_cr_remote(plugin_dir: Path, host: str) -> tuple[str, str]:
    """Discover CR + configure the ``cr`` remote and credential helper.

    Idempotent — safe to call on every publish/pull. Returns ``(org_slug,
    plugin_name)``. The plugin author never sees any of this.
    """
    token = get_or_request_api_token(host)
    git_url, org_slug = _control_room_info(host, token)
    name = _manifest_name(plugin_dir)

    remote_url = f"{git_url.rstrip('/')}/{org_slug}/{name}.git"
    if _git(plugin_dir, "remote", "get-url", "cr").returncode == 0:
        _git(plugin_dir, "remote", "set-url", "cr", remote_url)
    else:
        _git(plugin_dir, "remote", "add", "cr", remote_url)

    # Register our credential helper as the sole helper for the CR git host, so
    # `canvas git-credential` mints the push JWT. `--replace-all` keeps it a
    # single entry across repeat publishes. We no longer reset inherited helpers
    # or stale `http.<host>.extraHeader`s here: the network operations run with
    # global/system git config ignored (see `_git(..., isolate_config=True)`),
    # which prevents that shadowing structurally rather than key by key. Use the
    # absolute path to *this* canvas executable — git invokes the helper via a
    # bare shell, so a plain "canvas" only works if it's on PATH (it isn't when
    # run from a venv or `uv run`).
    canvas_bin = shutil.which(sys.argv[0]) or sys.argv[0]
    origin = _url_origin(remote_url)
    _git(
        plugin_dir,
        "config",
        "--replace-all",
        f"credential.{origin}.helper",
        f"!{canvas_bin} git-credential --host {host}",
    )
    _git(plugin_dir, "config", f"credential.{origin}.username", "git")

    return org_slug, name


def _manifest_name(plugin_dir: Path) -> str:
    """The plugin's manifest ``name`` — the Control Room repo name."""
    manifest = plugin_dir / "CANVAS_MANIFEST.json"
    if not manifest.exists():
        raise typer.BadParameter(f"'{plugin_dir}' has no CANVAS_MANIFEST.json")
    try:
        name = json.loads(manifest.read_text()).get("name")
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not read {manifest}: {exc}") from exc
    if not name:
        raise typer.BadParameter(f'{manifest} is missing a "name"')
    return str(name)


# -- commands ----------------------------------------------------------------


def git_credential(
    operation: str = typer.Argument(..., help="git credential operation (get/store/erase)"),
    host: str | None = typer.Option(
        None, "--host", help="Canvas instance to mint the push JWT from"
    ),
) -> None:
    """Git credential helper — mints a short-lived Control Room push JWT.

    Not called directly; git invokes it (configured by `canvas publish`) as
    ``canvas git-credential --host <instance> <get|store|erase>``, feeding the
    request on stdin. Only ``get`` does anything: it returns ``username=git``
    and a fresh JWT as the password. Tokens are ephemeral, so store/erase are
    no-ops.
    """
    # Consume git's request on stdin (protocol/host/path); we mint regardless.
    with contextlib.suppress(Exception):
        sys.stdin.read()

    if operation != "get":
        return

    resolved = get_default_host(host)
    try:
        token = get_or_request_api_token(resolved)
        resp = requests.post(
            _cr_url(resolved, "mint-git-jwt"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        body = resp.json()
    except (requests.RequestException, ValueError) as exc:
        # Fail loudly on stderr; a helper that emits no credentials makes git
        # prompt interactively, which is worse for a CLI push.
        print(f"canvas: could not mint a Control Room git credential: {exc}", file=sys.stderr)
        raise typer.Exit(1) from exc

    print("username=git")
    print(f"password={body['jwt']}")
    if expires_in := body.get("expires_in"):
        print(f"password_expiry_utc={int(time.time()) + int(expires_in)}")


def publish(
    plugin_name: Path = typer.Argument(..., help="Path to the plugin to publish"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
    message: str | None = typer.Option(
        None, "--message", "-m", help="Commit message for the snapshot (default: auto)"
    ),
    no_commit: bool = typer.Option(
        False,
        "--no-commit",
        help="Publish the last commit as-is; don't snapshot the working tree.",
    ),
) -> None:
    """Publish a plugin's current code to Control Room.

    By default this snapshots your working tree — staging and committing any
    changes for you — and pushes it, so what's on disk is what gets published;
    you never have to touch git. Pass ``--no-commit`` if you manage your own
    commits and want to publish exactly the current ``HEAD``.
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")
    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")
    _require_git_repo(plugin_name)

    if no_commit:
        if _git(plugin_name, "status", "--porcelain").stdout.strip():
            print(
                "Note: --no-commit set and the working tree has uncommitted changes; "
                "publishing the last commit only — your uncommitted edits won't ship."
            )
    else:
        _capture_working_tree(plugin_name, message=message)

    org_slug, name = _ensure_cr_remote(plugin_name, host)

    print(f"Publishing {org_slug}/{name} to Control Room…")
    # Push the current HEAD onto Control Room's canonical `main` ref. CR enforces
    # fast-forward-only, so a stale local HEAD is rejected (see below).
    result = _git(plugin_name, "push", "cr", "HEAD:main", isolate_config=True)
    if result.returncode != 0:
        stderr = result.stderr or ""
        if any(marker in stderr for marker in ("non-fast-forward", "fetch first", "[rejected]")):
            print(
                "Control Room has newer commits than your local copy — most likely a "
                "Canvas Support fix.\nRun `canvas pull` to integrate them, then publish again."
            )
            raise typer.Exit(1)
        print(stderr or "git push failed")
        raise typer.Exit(1)

    # `git push` prints "Everything up-to-date" (and pushes nothing) when HEAD is
    # already on CR — surface that honestly rather than a misleading "Published".
    if "up-to-date" in (result.stdout + result.stderr).lower():
        print(f"Nothing new to publish — Control Room already has {org_slug}/{name}@main.")
    else:
        print(f"Published {org_slug}/{name}. Deploy it with `canvas deploy`.")


def pull(
    plugin_name: Path = typer.Argument(..., help="Path to the plugin to update"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
) -> None:
    """Integrate Control Room changes (e.g. a Canvas Support fix) into a plugin."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")
    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")
    _require_git_repo(plugin_name)

    org_slug, name = _ensure_cr_remote(plugin_name, host)

    print(f"Fetching {org_slug}/{name} from Control Room…")
    fetched = _git(plugin_name, "fetch", "cr", isolate_config=True)
    if fetched.returncode != 0:
        print(fetched.stderr or "git fetch failed")
        raise typer.Exit(1)

    merged = _git(plugin_name, "merge", "--no-edit", "cr/main")
    if merged.returncode != 0:
        print(
            "Control Room changes need manual resolution — resolve the conflicts, "
            "commit, then `canvas publish` again:\n" + (merged.stderr or merged.stdout)
        )
        raise typer.Exit(1)

    print(merged.stdout.strip() or "Already up to date with Control Room.")


def deploy(
    plugin_name: Path = typer.Argument(..., help="Path to the plugin to deploy"),
    ref: str = typer.Option("main", "--ref", help="Published git ref to deploy"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
    assume_yes: bool = typer.Option(
        False, "--yes", "-y", help="Approve all consent prompts non-interactively"
    ),
) -> None:
    """Deploy an already-published plugin ref to this instance via Control Room.

    Names a ref previously sent up with `canvas publish`; Control Room builds
    the artifact and installs it. If the deploy is gated on operator consent
    (e.g. cross-plugin custom-data access), the requests are shown and approved
    or denied inline.
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")
    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")

    name = _manifest_name(plugin_name)
    token = get_or_request_api_token(host)
    _, org_slug = _control_room_info(host, token)

    print(f"Deploying {org_slug}/{name}@{ref}…")
    result = _post(
        host,
        token,
        _cr_url(host, "deploy"),
        {"plugins": [{"orgSlug": org_slug, "name": name, "gitRef": ref}]},
    )

    if not result.get("ok"):
        print(f"Deploy failed: {result.get('error') or 'unknown error'}")
        raise typer.Exit(1)

    if result.get("status") == "pending_consent":
        _handle_consent(host, token, result, assume_yes=assume_yes)
        return

    print(f"Deploy dispatched for {org_slug}/{name}@{ref}.")


def set_variables(
    plugin_name: str = typer.Argument(..., help="Plugin name to configure"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
    variables: list[str] = typer.Argument(..., help="Variables to set, e.g. Key=value"),
) -> None:
    """Set a plugin's variables through Control Room.

    The headless replacement for the direct-to-instance ``config set``: Control
    Room stores the values and pushes them to this instance, so it keeps working
    once ``canvas install``'s write path is locked out for CR-managed plugins.
    Values are write-only and treated as sensitive, matching the direct path.
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    parsed: list[dict[str, object]] = []
    for item in variables:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise typer.BadParameter(f"Invalid variable format: '{item}'. Use key=value.")
        parsed.append({"key": key, "value": value, "sensitive": True})

    token = get_or_request_api_token(host)
    _, org_slug = _control_room_info(host, token)

    print(f"Setting {len(parsed)} variable(s) on {org_slug}/{plugin_name} via Control Room…")
    result = _post(
        host,
        token,
        _cr_url(host, "set-variables"),
        {"plugins": [{"orgSlug": org_slug, "name": plugin_name, "variables": parsed}]},
    )
    if not result.get("ok"):
        print(f"Failed to set variables: {result.get('error') or 'unknown error'}")
        raise typer.Exit(1)

    print(f"Set {len(parsed)} variable(s) on {org_slug}/{plugin_name}.")


def uninstall(
    plugin_name: str = typer.Argument(..., help="Plugin name to uninstall"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
) -> None:
    """Uninstall a plugin from this instance through Control Room.

    The headless teardown: home-app refuses a direct CLI uninstall of a
    ``control_room_managed`` plugin (KOALA-5877), so removal must go through
    Control Room. Dispatches an uninstall on the calling instance.
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)
    _, org_slug = _control_room_info(host, token)

    print(f"Uninstalling {org_slug}/{plugin_name} via Control Room…")
    result = _post(
        host,
        token,
        _cr_url(host, "uninstall"),
        {"plugins": [{"orgSlug": org_slug, "name": plugin_name}]},
    )
    if not result.get("ok"):
        print(f"Uninstall failed: {result.get('error') or 'unknown error'}")
        raise typer.Exit(1)

    print(f"Uninstall dispatched for {org_slug}/{plugin_name}.")


def _handle_consent(host: str, token: str, deploy_result: dict, *, assume_yes: bool) -> None:
    """Walk the operator through the consent requests a gated deploy produced."""
    requests_list = deploy_result.get("consent_requests") or []
    count = deploy_result.get("consent_request_count", len(requests_list))
    print(f"\nThis deploy needs operator consent ({count} request(s)):\n")

    if not requests_list:
        # The proxy inlines requests on the deploy response; if they're missing
        # something is off — don't silently proceed.
        print("Consent is required but no request details were returned; check Control Room.")
        raise typer.Exit(1)

    denied = False
    dispatched = False
    for req in requests_list:
        request_id = req["id"]
        heading = req.get("title") or req.get("subject") or f"Consent request {request_id}"
        print(f"  • {heading}")
        if implication := req.get("implication"):
            print(f"    {implication}")

        approve = assume_yes or typer.confirm(f"    Approve request {request_id}?", default=False)
        if approve:
            outcome = _post(host, token, _consent_url(host, request_id, "approve"))
            if not outcome.get("ok"):
                print(f"    Approval failed: {outcome.get('error') or 'unknown error'}")
                raise typer.Exit(1)
            dispatched = dispatched or bool(outcome.get("dispatched"))
            print("    Approved.")
        else:
            reason = "" if assume_yes else typer.prompt("    Reason for denial", default="")
            outcome = _post(host, token, _consent_url(host, request_id, "deny"), {"reason": reason})
            if not outcome.get("ok"):
                # Surface a server-side rejection (e.g. permission) instead of
                # reporting a denial that didn't take — the request stays live.
                print(f"    Denial failed: {outcome.get('error') or 'unknown error'}")
                raise typer.Exit(1)
            denied = True
            print("    Denied.")

    print()
    if denied:
        print("Deploy was not dispatched — one or more consent requests were denied.")
        raise typer.Exit(1)
    if dispatched:
        print("All consent granted — deploy dispatched.")
    else:
        print("Consent recorded; the deploy will dispatch once all approvals are in.")
