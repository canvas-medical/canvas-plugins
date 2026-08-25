"""Control Room deploy commands for the `canvas` CLI (KOALA-5923).

Control Room is the authoritative git home for a plugin. The `canvas` CLI never
talks to Control Room directly — it goes through the developer's own Canvas
instance (home-app), which proxies to Control Room and signs short-lived JWTs on
the developer's behalf. ``canvas cr-init`` discovers the CR git server + org
from the instance and wires up a ``cr`` remote + credential helper; from there
the (git-savvy) developer publishes with **plain git** (``git push cr
HEAD:main``) — the CLI no longer wraps add/commit/push.

Commands (registered behind CONTROL_ROOM_BETA in canvas_cli.main):

  * ``canvas git-credential`` — hidden git credential helper; git invokes it to
    mint a push credential via the instance's ``mint-git-jwt`` endpoint.
  * ``canvas cr-init`` — connect a plugin repo to Control Room (sets up the
    ``cr`` remote + credential helper). One-time, idempotent.
  * ``canvas deploy`` / ``canvas config set`` / ``canvas uninstall`` — dispatch
    deploy / variable / uninstall operations through the instance's CR proxies.
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
            "git was not found on your PATH. `canvas cr-init` and publishing to "
            "Control Room use git. Install it from "
            "https://git-scm.com/downloads and try again."
        )


def _require_git_repo(plugin_dir: Path) -> None:
    _require_git_installed()
    result = _git(plugin_dir, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise typer.BadParameter(
            f"'{plugin_dir}' is not a git repository. Control Room is your plugin's "
            "git remote, so the plugin must live in a git repo (run `git init` first)."
        )


def _url_origin(url: str) -> str:
    """``scheme://host`` for credential-helper scoping."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _ensure_cr_remote(plugin_dir: Path, host: str) -> tuple[str, str]:
    """Discover CR + configure the ``cr`` remote and credential helper.

    Idempotent — safe to call on every ``cr-init``. Returns ``(org_slug,
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

    Not called directly; git invokes it (configured by `canvas cr-init`) as
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


def cr_init(
    plugin_name: Path = typer.Argument(..., help="Path to the plugin to connect to Control Room"),
    host: str | None = typer.Option(
        callback=get_default_host, default=None, help="Canvas instance to connect to"
    ),
) -> None:
    """Connect a plugin's git repo to Control Room (its authoritative remote).

    One-time, idempotent setup: adds a ``cr`` remote pointing at Control Room's
    git backend and registers the credential helper that mints push tokens. After
    this you publish with **plain git** — Control Room is a normal remote:

        git add -A && git commit -m "…"
        git push cr HEAD:main

    then deploy with ``canvas deploy``. (Control Room is the source of truth for
    plugin history; there is no separate ``publish`` step.)
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")
    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")
    _require_git_repo(plugin_name)  # also asserts git is installed

    org_slug, name = _ensure_cr_remote(plugin_name, host)

    print(f"Connected {org_slug}/{name} to Control Room (remote 'cr').")
    print("Publish with plain git, then deploy:")
    print("  git add -A && git commit -m 'your message'")
    print("  git push cr HEAD:main")
    print(f"  canvas deploy {plugin_name} --host {host}")


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

    Names a ref previously pushed to the `cr` remote (`git push cr HEAD:main`);
    Control Room builds the artifact and installs it. If the deploy is gated on
    operator consent
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
