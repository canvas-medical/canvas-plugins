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


def _git(plugin_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command scoped to the plugin repo."""
    return subprocess.run(
        ["git", "-C", str(plugin_dir), *args],
        capture_output=True,
        text=True,
        check=False,
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

    # Scope the credential helper to the CR git host and bake in this instance
    # so `canvas git-credential` knows where to mint the push JWT. Host-level
    # scoping is enough: only git ever invokes a credential helper. Use the
    # absolute path to *this* canvas executable — git invokes the helper via a
    # bare shell, so a plain "canvas" only works if it's on PATH (it isn't when
    # run from a venv or `uv run`).
    canvas_bin = shutil.which(sys.argv[0]) or sys.argv[0]
    origin = _url_origin(remote_url)
    # Reset the helper list for this host first (empty value) so an inherited,
    # broader-scope helper — notably macOS's system-wide osxkeychain — can't
    # shadow ours with a stale cached credential, then register ours as the sole
    # helper for the CR git host.
    _git(plugin_dir, "config", f"credential.{origin}.helper", "")
    _git(
        plugin_dir,
        "config",
        "--add",
        f"credential.{origin}.helper",
        f"!{canvas_bin} git-credential --host {host}",
    )
    _git(plugin_dir, "config", f"credential.{origin}.username", "git")

    # Drop any inherited Authorization extraHeader for the CR host. A prior
    # `canvas login` / cr-login writes a URL-scoped `http.<host>.extraHeader`
    # with an OAuth2 token; git would attach it to our push and shadow the
    # credential helper, sending a stale token that 401s. An empty value resets
    # the (multi-valued) list for this repo, leaving the helper as the sole auth.
    # Reset both the bare origin and the trailing-slash form: `http.<url>`
    # matching is by URL prefix, and cr-login writes the key WITH a trailing
    # slash (`http.<host>/.extraHeader`) in *global* config, so clearing only the
    # bare origin leaves that global entry live for this repo.
    for key in (f"http.{origin}.extraHeader", f"http.{origin}/.extraHeader"):
        _git(plugin_dir, "config", key, "")

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
) -> None:
    """Publish a plugin's current git HEAD to Control Room."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")
    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")
    _require_git_repo(plugin_name)

    org_slug, name = _ensure_cr_remote(plugin_name, host)

    print(f"Publishing {org_slug}/{name} to Control Room…")
    # Push the current HEAD onto Control Room's canonical `main` ref. CR enforces
    # fast-forward-only, so a stale local HEAD is rejected (see below).
    result = _git(plugin_name, "push", "cr", "HEAD:main")
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
    fetched = _git(plugin_name, "fetch", "cr")
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
            _post(host, token, _consent_url(host, request_id, "deny"), {"reason": reason})
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
