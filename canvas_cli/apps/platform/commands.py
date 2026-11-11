"""Commands that publish, deploy and configure plugins through Canvas Platform.

Canvas Platform hosts each plugin's git repository and deploys it to the
instances it manages. These commands talk to platform's ``/api/v1/`` as the
person signed in with ``canvas login``:

  * ``canvas login`` / ``canvas logout``: the browser sign-in and its revocation.
  * ``canvas whoami``: which platform, and who the CLI signs in as there.
  * ``canvas init``: scaffolds a plugin; signed in, it names it ``<prefix>__<package>``
    by convention, records the publisher in its manifest and registers it with platform.
  * ``canvas deploy``: commits and pushes the working tree, or pushes a snapshot of a
    plugin inside a larger repository, to ``main`` or to the branch ``--branch``
    names, then deploys it.
  * ``canvas clone``: checks out a plugin's repository, ready to push.
  * ``canvas enable`` / ``disable``, ``canvas config list`` / ``set`` / ``unset`` and
    ``canvas uninstall``: through platform for a plugin it manages. Signed in, any
    other plugin is refused unless it targets localhost; signed out, these go directly
    against the instance.
  * ``canvas git-credential``: hidden; git runs it to mint a push token.

``managed_instance``, defined in ``routing`` and re-exported here, decides whether an
instance command (``list``, ``logs``, ``namespace *``) goes through platform, which it
does for an instance platform manages, and refuses any other Canvas instance while signed in.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

import click
import typer

from canvas_cli.apps.auth.utils import configured_default_host, get_default_host, instance_slug
from canvas_cli.apps.platform import auth, git
from canvas_cli.apps.platform.client import PlatformClient, PlatformError
from canvas_cli.apps.platform.routing import managed_instance as managed_instance
from canvas_cli.apps.platform.routing import refuse_unmanaged, require_managed
from canvas_cli.apps.plugin import plugin as instance_plugin
from canvas_cli.utils.platform_notice import print_credentials_ini_deprecation

PLUGIN_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
# Canvas Platform's and home-app's limit.
PLUGIN_NAME_MAX_LENGTH = 256

DEPLOYMENT_TERMINAL = frozenset({"succeeded", "partial", "failed", "cancelled"})
POLL_INTERVAL_SECONDS = 2.0
POLL_TIMEOUT_SECONDS = 300.0

# Why a target settles `skipped`, by deployment action.
_SKIPPED_BECAUSE = {
    "configure": "not installed there; the stored values apply when it is next deployed",
    "uninstall": "not installed there",
}

_INSTANCE_HELP = "Instance slug to target (repeatable)"


# -- names and publishers ----------------------------------------------------


def _read_manifest(plugin_dir: Path) -> tuple[Path, str, dict[str, Any]]:
    """The manifest path, its text and its parsed object.

    Args:
        plugin_dir (Path): The plugin package directory.

    Returns:
        tuple[Path, str, dict[str, Any]]: The manifest path, its raw text and its JSON object.

    Raises:
        typer.BadParameter: The manifest is missing, unreadable or not a JSON object.
    """
    manifest: Path = plugin_dir / "CANVAS_MANIFEST.json"
    if not manifest.exists():
        raise typer.BadParameter(f"'{plugin_dir}' has no CANVAS_MANIFEST.json")
    try:
        text: str = manifest.read_text(encoding="utf-8")
        data: Any = json.loads(text)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not read {manifest}: {exc}") from exc
    if not isinstance(data, dict):
        raise typer.BadParameter(f"Could not read {manifest}: it is not a JSON object")
    return manifest, text, data


def manifest_name(plugin_dir: Path) -> str:
    """The manifest ``name`` of the plugin package in ``plugin_dir``."""
    manifest, _, data = _read_manifest(plugin_dir)
    name: Any = data.get("name")
    if not name:
        raise typer.BadParameter(f'{manifest} is missing a "name"')
    return str(name)


def manifest_publisher(plugin_dir: Path) -> str | None:
    """The manifest ``publisher`` of the plugin package in ``plugin_dir``.

    Args:
        plugin_dir (Path): The plugin package directory.

    Returns:
        str | None: The publisher slug, or None when the manifest has no ``publisher``.
            An empty string is returned as is.

    Raises:
        typer.BadParameter: The manifest is missing or unreadable, or ``publisher`` is
            not a string, null included, since Canvas Platform refuses that at push.
    """
    manifest, _, data = _read_manifest(plugin_dir)
    if "publisher" not in data:
        return None
    publisher: Any = data["publisher"]
    if not isinstance(publisher, str):
        raise typer.BadParameter(f'{manifest} has a "publisher" that is not a string')
    return publisher


def write_manifest_publisher(plugin_dir: Path, slug: str) -> None:
    """Record ``slug`` as the manifest's ``publisher``, right after ``name``.

    The deploy commits the manifest, so only the ``publisher`` line changes: an existing
    top-level value is replaced where it stands, or a line is added after the top-level
    ``name`` line. A manifest whose top level does not sit one key per line (a one-line
    manifest, say) is written out again with its indent and its trailing newline. Its
    line endings, LF or CRLF, are kept.

    Args:
        plugin_dir (Path): The plugin package directory.
        slug (str): The slug of the Canvas Platform organization that publishes the plugin.

    Raises:
        typer.BadParameter: The manifest is missing or unreadable.
    """
    manifest, text, data = _read_manifest(plugin_dir)
    # read_text turns CRLF into "\n"; write_text turns "\n" back into this.
    newline: str = "\r\n" if b"\r\n" in manifest.read_bytes() else "\n"
    indent_match: re.Match[str] | None = re.search(r"^( +|\t)\S", text, flags=re.MULTILINE)
    indent: str | int = indent_match.group(1) if indent_match else 4
    expected: dict[str, Any] = {**data, "publisher": slug}
    if indent_match:
        edited: str | None = _edit_publisher_line(text, indent_match.group(1), slug)
        if edited is not None and _loads_without_duplicate_keys(edited) == expected:
            manifest.write_text(edited, encoding="utf-8", newline=newline)
            return
    rebuilt: dict[str, Any] = {}
    if "publisher" in data:
        rebuilt = {**data, "publisher": slug}
    else:
        for key, value in data.items():
            rebuilt[key] = value
            if key == "name":
                rebuilt["publisher"] = slug
        rebuilt.setdefault("publisher", slug)
    output: str = json.dumps(rebuilt, indent=indent, ensure_ascii=False)
    if text.endswith("\n"):
        output += "\n"
    manifest.write_text(output, encoding="utf-8", newline=newline)


def _loads_without_duplicate_keys(text: str) -> Any:
    """``text`` parsed as JSON, or None when an object in it repeats a key.

    ``json.loads`` keeps the last of two equal keys, so an edit that adds a second
    ``publisher`` would otherwise parse to the expected manifest.

    Args:
        text (str): JSON text.

    Returns:
        Any: The parsed value, or None when a key repeats.
    """

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys: list[str] = [key for key, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError("repeated key")
        return dict(pairs)

    try:
        return json.loads(text, object_pairs_hook=unique)
    except ValueError:
        return None


_JSON_STRING = r'"(?:[^"\\]|\\.)*"'


def _edit_publisher_line(text: str, indent: str, slug: str) -> str | None:
    """``text`` with its top-level ``publisher`` set to ``slug``, changing that line alone.

    A top-level key is one whose line starts with exactly one ``indent``. The caller
    checks the result parses to the expected manifest, so a layout this misreads is
    written out again instead.

    Args:
        text (str): The manifest text.
        indent (str): The manifest's indent unit, as found on its first indented line.
        slug (str): The publisher slug to record.

    Returns:
        str | None: The edited text, or None when the top level has no ``name`` line to
            add the publisher after.
    """
    value: str = json.dumps(slug, ensure_ascii=False)
    key: str = rf"^{re.escape(indent)}(?=\S)"
    existing: re.Pattern[str] = re.compile(
        rf'({key}"publisher"\s*:\s*)(?:{_JSON_STRING}|null)', flags=re.MULTILINE
    )
    if existing.search(text):
        return existing.sub(lambda m: m.group(1) + value, text, count=1)
    name_line: re.Pattern[str] = re.compile(
        rf'{key}"name"\s*:\s*{_JSON_STRING}\s*,[ \t]*\n', flags=re.MULTILINE
    )
    found: re.Match[str] | None = name_line.search(text)
    if found is None:
        return None
    return f'{text[: found.end()]}{indent}"publisher": {value},\n{text[found.end() :]}'


def require_valid_name(name: str) -> None:
    """Refuse a manifest name that is not a valid Python package name within the length limit."""
    if PLUGIN_NAME_PATTERN.fullmatch(name) and len(name) <= PLUGIN_NAME_MAX_LENGTH:
        return
    package: str = re.sub(r"[^a-z0-9_]", "_", name.lower()).strip("_") or "package"
    package = package.lstrip("0123456789_")[:PLUGIN_NAME_MAX_LENGTH] or "package"
    raise typer.BadParameter(
        f"The plugin name '{name}' is not valid. A name starts with a lowercase letter, then "
        f"holds lowercase letters, digits and underscores, at most {PLUGIN_NAME_MAX_LENGTH} "
        "characters, because it is a Python package. Rename it in "
        f"the manifest, the package folder and its imports, for example `{package}`."
    )


def require_folder_matches_name(plugin_dir: Path, name: str) -> None:
    """Refuse a package whose folder is not named after the plugin.

    The folder is the Python package an instance imports, so Canvas Platform's git
    server refuses a push where the two differ. Checking here refuses it before
    anything is committed or pushed.
    """
    folder = plugin_dir.resolve().name
    if folder == name:
        return
    raise typer.BadParameter(
        f"The package folder is '{folder}', but the manifest name is '{name}'. They have to "
        "match, because the folder is the Python package an instance imports. Rename the "
        f"folder to '{name}', and update the imports and manifest class paths that name "
        f"'{folder}'."
    )


def require_no_ignored_python(plugin_dir: Path) -> None:
    """Refuse a package holding Python files git ignores.

    Validation reads the package on disk, but the push carries only what git tracks,
    so an ignored module passes validation and is missing on the instance. Paths
    under a dot-folder or ``node_modules`` are left out, since validation and
    ``canvas install`` skip them too.
    """
    ignored = [
        path
        for path in git.ignored_python_files(plugin_dir)
        if not any(part.startswith(".") or part == "node_modules" for part in Path(path).parts)
    ]
    if not ignored:
        return
    raise typer.BadParameter(
        f"Git ignores these Python files in '{plugin_dir}', so the push would leave them out: "
        f"{', '.join(ignored)}. Stop ignoring them in .gitignore, or move them out of the "
        "package, then try again."
    )


def _no_push_role(*organizations: dict[str, Any]) -> typer.BadParameter:
    """The refusal for organizations whose roles do not include pushing plugin code."""
    names: str = ", ".join(str(o.get("name") or o["slug"]) for o in organizations)
    return typer.BadParameter(
        f"Your roles in {names} do not include pushing plugin code. Ask an organization "
        "admin for the Plugin developer role."
    )


def _matching_organization(organizations: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    """The person's organization whose ``plugin_prefix`` ``name`` carries; the longest wins.

    Args:
        organizations (list[dict[str, Any]]): The person's organizations from ``/me``.
        name (str): The plugin name.

    Returns:
        dict[str, Any] | None: The organization, or None when the name carries no prefix of
            the person's organizations.
    """
    matches: list[dict[str, Any]] = [
        organization
        for organization in organizations
        if organization.get("plugin_prefix")
        and name.startswith(f"{organization['plugin_prefix']}__")
    ]
    return max(matches, key=lambda o: len(o["plugin_prefix"]), default=None)


def _legacy_publisher(client: PlatformClient, name: str, declared: str | None) -> str | None:
    """The slug of the organization that publishes the plugin named ``name`` the person sees
    on Canvas Platform, member or not, else None. Platform authorizes the push and the
    deployment itself. A 409 ``ambiguous`` (several publishers) is settled by the manifest
    ``publisher`` when it names one, and otherwise counts as none.
    """
    try:
        plugin: dict[str, Any] | None = client.plugin(name)
    except PlatformError as error:
        if error.code != "ambiguous":
            raise
        if not declared:
            return None
        plugin = client.plugin(name, declared)
    if plugin is None:
        return None
    return str(plugin.get("publisher") or "") or None


def _publisher(
    client: PlatformClient,
    plugin_dir: Path,
    name: str,
    *,
    pushing: bool,
    records: bool,
    held: str | None,
) -> tuple[str, bool]:
    """The slug of the organization that publishes ``name``, and whether the person picked it.

    It is ``held`` when the manifest names no other ``publisher``; else the manifest's
    ``publisher`` when it names an organization the person belongs to, or any
    ``publisher`` for a deploy that pushes nothing, whose deployment Canvas Platform
    authorizes on its own (a Canvas employee deploys in every organization without
    belonging to it); else the person's organization whose ``plugin_prefix`` the name
    carries; else the only organization the person can publish in; else, at a terminal,
    the one the person picks. The choice is returned, not written: a regular push records it in the manifest once the package is accepted (``records``), and any
    other deploy prints the line to add instead. Without a terminal, several
    organizations are refused with the manifest line that chooses one.

    Args:
        client (PlatformClient): The signed-in platform client.
        plugin_dir (Path): The plugin package directory.
        name (str): The plugin name, for messages.
        pushing (bool): Whether the command pushes code, which needs ``push_plugin_code``.
        records (bool): Whether the command is a regular push, which records a picked
            publisher in the manifest.
        held (str | None): The organization that publishes ``name`` on Platform, for a
            legacy name outside the character rule, whether or not the person belongs to it.

    Returns:
        tuple[str, bool]: The publishing organization's slug, and whether the person
            picked it at the prompt and the regular push is to record it.

    Raises:
        typer.BadParameter: No organization can publish the plugin, or the choice is unclear.
    """
    organizations: list[dict[str, Any]] = client.me().get("organizations", [])
    slugs: str = ", ".join(str(o["slug"]) for o in organizations)
    declared: str | None = manifest_publisher(plugin_dir)
    if held is not None and declared in (None, held):
        # Platform refuses a push or deployment the person may not make.
        print(f"Publishing as {held}, which publishes {name} on Canvas Platform.")
        return held, False
    if declared is not None:  # "" is a value too, and is refused below as no organization
        match: dict[str, Any] | None = next(
            (o for o in organizations if o["slug"] == declared), None
        )
        if match is None and declared and not pushing:
            return declared, False
        if match is None:
            yours: str = (
                f"Your organizations: {slugs}."
                if organizations
                else "You do not belong to any organization on Canvas Platform."
            )
            raise typer.BadParameter(
                f"'{name}' names publisher '{declared}', which is not an organization you "
                f"belong to on Canvas Platform. {yours}"
            )
        if pushing and "push_plugin_code" not in match.get("capabilities", []):
            raise _no_push_role(match)
        return declared, False

    prefixed: dict[str, Any] | None = _matching_organization(organizations, name)
    if prefixed is not None:
        if pushing and "push_plugin_code" not in prefixed.get("capabilities", []):
            raise _no_push_role(prefixed)
        print(f"Publishing as {prefixed['slug']}, whose prefix the name carries.")
        return str(prefixed["slug"]), False

    eligible: list[dict[str, Any]] = [
        o for o in organizations if not pushing or "push_plugin_code" in o.get("capabilities", [])
    ]
    if not eligible:
        if organizations:
            raise _no_push_role(*organizations)
        raise typer.BadParameter("You do not belong to any organization on Canvas Platform.")
    if len(eligible) == 1:
        only: str = str(eligible[0]["slug"])
        print(f"Publishing as {only}, the only organization you can publish in.")
        return only, False
    if not git.interactive():
        raise typer.BadParameter(
            "You can publish in several organizations: "
            f"{', '.join(str(o['slug']) for o in eligible)}. "
            'Add "publisher": "<slug>" to CANVAS_MANIFEST.json to choose one.'
        )
    chosen: str = str(_choose_organization(eligible, None)["slug"])
    if not records:
        print(_publisher_hint(chosen))
    return chosen, records


def _publisher_hint(slug: str) -> str:
    """The manifest line that skips the publisher question, for a deploy that does not write it."""
    return f'Add "publisher": "{slug}" to CANVAS_MANIFEST.json and commit it to skip this question.'


# -- targets -----------------------------------------------------------------


def _resolve_instances(
    client: PlatformClient,
    requested: list[str],
    capability: str,
    *,
    verb: str,
    among: set[str] | None = None,
) -> list[str]:
    """The instances a command targets.

    Explicit ``--instance`` values are used as given, and platform refuses any the
    person may not act on. Without one, the command targets the only managed
    instance the person holds ``capability`` on (narrowed to ``among`` when
    given), and refuses with the choices when there is more than one.
    """
    if requested:
        return list(dict.fromkeys(requested))
    eligible = [
        instance["slug"]
        for instance in client.instances()
        if instance.get("managed")
        and capability in instance.get("capabilities", [])
        and (among is None or instance["slug"] in among)
    ]
    if len(eligible) == 1:
        print(f"Targeting {eligible[0]}, the only instance you can {verb}.")
        return eligible
    if not eligible:
        raise typer.BadParameter(
            f"There is no instance Canvas Platform manages that you can {verb}. "
            "Name one with --instance."
        )
    raise typer.BadParameter(
        f"There are several instances you can {verb}; choose with --instance: "
        f"{', '.join(sorted(eligible))}."
    )


# -- deployments -------------------------------------------------------------


def _describe_consent(request: dict[str, Any]) -> None:
    instances = ", ".join(request.get("instances", []))
    print(
        f"  • {request.get('plugin')} asks for {request.get('access')} access to the "
        f"custom data namespace '{request.get('namespace')}' on {instances}."
    )


def _walk_consent(client: PlatformClient, deployment: dict[str, Any], *, assume_yes: bool) -> None:
    """Ask the person to approve or deny each consent request a deployment waits on.

    Approving a request grants one plugin another plugin's custom data, so only a
    person answering at a terminal decides it. Under ``--yes`` or without a TTY
    the requests are printed and the command exits non-zero, answering none.
    """
    pending = [r for r in deployment.get("consent_requests", []) if r.get("status") == "pending"]
    if not pending:
        return
    print(f"\nThis deployment needs consent ({len(pending)} request(s)):\n")
    if assume_yes or not git.interactive():
        for request in pending:
            _describe_consent(request)
        why = "--yes does not answer consent" if assume_yes else "there is no terminal to ask at"
        print(
            f"\nDeployment {deployment['id']} is waiting on these requests, and {why}. "
            "Run the command again at a terminal, without --yes, to approve or deny them."
        )
        raise typer.Exit(1)
    for request in pending:
        _describe_consent(request)
        if typer.confirm(f"    Approve request {request['id']}?", default=False):
            client.answer_consent(request["id"], approve=True)
            print("    Approved.")
            continue
        reason = typer.prompt("    Reason for denial", default="")
        client.answer_consent(request["id"], approve=False, reason=reason)
        print("    Denied.")
        print("\nThe deployment was cancelled because a consent request was denied.")
        raise typer.Exit(1)
    print()


def _wait_for(client: PlatformClient, deployment: dict[str, Any]) -> dict[str, Any] | None:
    """Poll a deployment until it settles; None when the wait runs out first.

    Transport failures and server errors are retried until the deadline, so a
    blip does not turn a deployment that succeeds into a reported failure.
    """
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    last_status = None
    while True:
        status = deployment.get("status")
        if status != last_status:
            print(f"  {status}…")
            last_status = status
        if status in DEPLOYMENT_TERMINAL:
            return deployment
        if time.monotonic() >= deadline:
            return None
        time.sleep(POLL_INTERVAL_SECONDS)
        try:
            deployment = client.deployment(deployment["id"])
        except PlatformError as error:
            if error.status is not None and error.status < 500:
                raise


def _report(deployment: dict[str, Any] | None, deployment_id: str, *, what: str) -> None:
    """Print each target's outcome and exit non-zero unless the deployment succeeded."""
    if deployment is None:
        print(
            f"{what} is still running after {int(POLL_TIMEOUT_SECONDS)}s "
            f"(deployment {deployment_id})."
        )
        raise typer.Exit(1)
    skipped_because = _SKIPPED_BECAUSE.get(str(deployment.get("action")), "nothing to do there")
    for target in deployment.get("targets", []):
        line = f"  {target.get('plugin')} on {target.get('instance')}: {target.get('status')}"
        if target.get("error"):
            line += f": {target['error']}"
        elif target.get("status") == "skipped":
            line += f" ({skipped_because})"
        print(line)
        if undeclared := target.get("undeclared_values"):
            print(
                "    Stored values left out because this revision does not declare them: "
                + ", ".join(undeclared)
            )
    status = deployment.get("status")
    if status == "succeeded":
        print(f"{what} succeeded.")
        return
    print(f"{what} {status}.")
    raise typer.Exit(1)


def _dispatch(
    client: PlatformClient,
    action: str,
    plugins: list[dict[str, str]],
    instances: list[str],
    *,
    what: str,
    assume_yes: bool = False,
) -> None:
    """Create a deployment, walk its consent requests, and wait for it to settle."""
    deployment = client.create_deployment(action, plugins, instances)
    print(f"Deployment {deployment['id']} created.")
    if deployment.get("status") == "pending_consent":
        _walk_consent(client, deployment, assume_yes=assume_yes)
    _report(_wait_for(client, deployment), deployment["id"], what=what)


# -- login / logout ----------------------------------------------------------


def login(
    platform: str | None = typer.Option(
        None,
        "--platform",
        help=(
            f"Canvas Platform URL [default: ${auth.PLATFORM_URL_ENV}, the last platform "
            f"signed in to, or {auth.DEFAULT_PLATFORM_URL}]"
        ),
    ),
) -> None:
    """Sign in to Canvas Platform through your browser."""
    url = auth.resolve_platform_url(platform)
    auth.login(url)
    me = PlatformClient(url).me()
    print(f"Signed in to {url} as {me.get('email')}.")
    for organization in me.get("organizations", []):
        print(
            f"  {organization.get('name')} ({organization['slug']}): plugin prefix "
            f"{organization.get('plugin_prefix')}__"
        )


def logout(
    platform: str | None = typer.Option(None, "--platform", help="Canvas Platform URL"),
) -> None:
    """Sign out of Canvas Platform and revoke this machine's session."""
    url = auth.resolve_platform_url(platform)
    problem = auth.logout(url)
    if problem is None:
        print(f"You were not signed in to {url}.")
    elif problem:
        print(f"Signed out of {url} on this machine, but revoking the session failed: {problem}.")
    else:
        print(f"Signed out of {url}.")
    if auth.service_token():
        print(
            f"{auth.SERVICE_TOKEN_ENV} is set, so commands still act as its service account. "
            "Unset it, or revoke it on the Credentials page in Canvas Platform."
        )


# The capabilities `canvas whoami` reports, as the commands they unlock.
_PLUGIN_CAPABILITIES = {
    "push_plugin_code": "push",
    "deploy_plugin": "deploy",
    "configure_plugin": "configure",
    "uninstall_plugin": "uninstall",
}


def whoami(
    platform: str | None = typer.Option(None, "--platform", help="Canvas Platform URL"),
) -> None:
    """Show which Canvas Platform the CLI uses, and who it signs in as there.

    It asks platform, so a revoked or expired credential is reported rather than
    assumed valid. No token is printed.
    """
    url, source = auth.platform_url_source(platform)
    print(f"Platform: {url} (from {source})")
    service = auth.service_token() is not None
    session = auth.stored_session(url)
    if not service and session is None:
        login_command = f"canvas login --platform {url}" if platform else "canvas login"
        print(f"Not signed in. Run `{login_command}`.")
        raise typer.Exit(1)

    me = PlatformClient(url).me()
    credential = (
        f"service account token from {auth.SERVICE_TOKEN_ENV}"
        if service
        else "browser session from `canvas login`"
    )
    employee = ", Canvas employee" if me.get("canvas_employee") else ""
    print(f"Signed in as {me.get('email')} ({credential}{employee})")
    if service and session is not None:
        print(
            f"  A `canvas login` session is also stored for this platform; "
            f"{auth.SERVICE_TOKEN_ENV} takes precedence while it is set."
        )
    organizations = me.get("organizations", [])
    if not organizations:
        print("  No organization memberships.")
    for organization in organizations:
        held = organization.get("capabilities", [])
        can = [word for capability, word in _PLUGIN_CAPABILITIES.items() if capability in held]
        print(
            f"  {organization.get('name')} ({organization['slug']}): plugin prefix "
            f"{organization.get('plugin_prefix')}__, can {', '.join(can) or 'view only'}"
        )


# -- git credential helper ---------------------------------------------------


def _read_credential_request(stream: TextIO) -> dict[str, str]:
    """Git's ``key=value`` credential request, which ends at a blank line or EOF."""
    request: dict[str, str] = {}
    for raw in stream:
        line = raw.rstrip("\n")
        if not line:
            break
        key, _, value = line.partition("=")
        request[key] = value
    return request


def repo_plugin(path: str) -> tuple[str | None, str]:
    """The publisher and plugin name in a repository path.

    Platform's paths are ``/git/<publisher>/<name>.git``. The leading ``git`` segment is
    the server's mount point, so the publisher is the segment before the name only when
    one remains.

    Args:
        path (str): The repository path git sends to the credential helper.

    Returns:
        tuple[str | None, str]: The publisher (None for a bare ``<name>.git``) and the name.
    """
    segments: list[str] = path.strip("/").split("/")
    if segments[0] == "git":
        segments = segments[1:]
    name: str = segments[-1].removesuffix(".git")
    publisher: str | None = segments[-2] if len(segments) >= 2 else None
    return publisher, name


def git_credential(
    operation: str = typer.Argument(..., help="git credential operation (get/store/erase)"),
    platform: str | None = typer.Option(None, "--platform", help="Canvas Platform URL"),
) -> None:
    """Git credential helper: mints a one-hour Canvas Platform git token.

    git runs it as ``canvas git-credential --platform <url> get`` with the request
    on stdin. Only ``get`` does anything; tokens are short-lived, so ``store`` and
    ``erase`` have nothing to keep or forget.
    """
    request = _read_credential_request(sys.stdin)
    if operation != "get":
        return
    path = request.get("path")
    if not path:
        print(
            "canvas: git did not send the repository path. Set "
            "`git config credential.useHttpPath true` in this repository.",
            file=sys.stderr,
        )
        raise typer.Exit(1)
    try:
        client = PlatformClient(auth.resolve_platform_url(platform))
        publisher, name = repo_plugin(path)
        credential = client.git_credentials(name, publisher)
    except click.ClickException as error:
        print(f"canvas: {error.message}", file=sys.stderr)
        raise typer.Exit(1) from error

    print(f"username={credential.get('username') or 'git'}")
    print(f"password={credential['password']}")
    if expires_at := credential.get("expires_at"):
        expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        print(f"password_expiry_utc={int(expiry.timestamp())}")


# -- deploy ------------------------------------------------------------------


def _require_package_at_repo_root(plugin_dir: Path) -> None:
    """Refuse a package that is not directly below its repository's root.

    A plugin's repository holds ``<package>/CANVAS_MANIFEST.json`` at its root,
    so a package nested deeper in a larger repository would push that whole
    repository as the plugin.
    """
    toplevel = git.run(plugin_dir, "rev-parse", "--show-toplevel").stdout.strip()
    expected = git.repo_root(plugin_dir)
    if toplevel and Path(toplevel).resolve() != expected:
        raise typer.BadParameter(
            f"'{plugin_dir}' is inside the git repository at {toplevel}, but a plugin's "
            f"repository must be rooted at the directory containing the package ({expected}). "
            "To deploy it from this repository, pass --snapshot."
        )


def _require_branch_name(plugin_dir: Path, branch: str) -> None:
    """Refuse a ``--branch`` that is ``main`` or that git does not accept as a branch name.

    ``check-ref-format --branch`` also expands ``@{-1}`` to the name of the branch
    checked out before the current one, so a name that comes back changed is
    refused rather than pushed under a name the person did not type.
    """
    if branch == "main":
        raise typer.BadParameter(
            "--branch names a branch other than 'main', which Canvas Platform deploys to "
            "every instance. Leave --branch out to push to the plugin's default branch."
        )
    git.require_installed()
    result = git.run(plugin_dir, "check-ref-format", "--branch", branch)
    if result.returncode != 0 or result.stdout.strip() != branch:
        raise typer.BadParameter(f"'{branch}' is not a valid branch name.")


def _target_and_default_branch(registered: dict[str, Any], branch: str | None) -> tuple[str, str]:
    """The branch to push to and the plugin's default branch, in that order.

    The target is ``branch``, or the default branch when none is given. A ``--branch``
    equal to the default branch is refused, because a plain deploy already pushes
    there and Platform deploys that branch to any instance.
    """
    default: str = registered.get("default_branch") or "main"
    if branch == default:
        raise typer.BadParameter(
            f"'{branch}' is the plugin's default branch on Canvas Platform. "
            "To deploy to it, leave --branch out."
        )
    return branch or default, default


def _push_snapshot(
    client: PlatformClient,
    plugin_dir: Path,
    publisher: str,
    name: str,
    platform: str,
    branch: str | None,
) -> str:
    """Register the plugin and push the package's committed contents as one new commit.

    Returns the commit on ``branch``, or on the default branch when ``branch`` is None.
    """
    snapshot = git.snapshot_source(plugin_dir)
    require_no_ignored_python(plugin_dir)
    if not git.on_a_remote(plugin_dir):
        print(
            f"Warning: {snapshot.commit[:12]} is not on any remote branch of the repository "
            "it is in, so it has not been pushed for review there.",
            file=sys.stderr,
            flush=True,
        )
    registered = client.register_plugin(publisher, name)
    target, default = _target_and_default_branch(registered, branch)
    me = client.me()
    return git.push_snapshot(
        snapshot,
        name,
        registered["git_url"],
        target,
        platform,
        author=(me.get("name") or me["email"], me["email"]),
        default_branch=default,
    )


def _push(
    client: PlatformClient,
    plugin_dir: Path,
    publisher: str,
    name: str,
    platform: str,
    *,
    assume_yes: bool,
    snapshot: bool,
    branch: str | None,
    record_publisher: bool,
) -> str:
    """Register the plugin, connect its repository and push HEAD to ``branch``.

    ``branch`` defaults to the plugin's default branch. With ``record_publisher``, the
    manifest names ``publisher`` before the commit, so the push carries it.

    Returns the pushed commit.
    """
    if snapshot:
        return _push_snapshot(client, plugin_dir, publisher, name, platform, branch)
    git.ensure_repo(plugin_dir)
    require_no_ignored_python(plugin_dir)
    _require_package_at_repo_root(plugin_dir)
    if record_publisher:
        write_manifest_publisher(plugin_dir, publisher)
        print(f"CANVAS_MANIFEST.json now names {publisher} as the publisher.")
    registered = client.register_plugin(publisher, name)
    target, _ = _target_and_default_branch(registered, branch)
    git.connect_remote(plugin_dir, registered["git_url"], platform)
    git.commit_working_tree(plugin_dir, assume_yes=assume_yes)
    git.push_head(plugin_dir, target)
    sha = git.head_sha(plugin_dir)
    print(f"Pushed {name} {sha[:12]} to {target} on Canvas Platform.")
    return sha


def deploy(
    plugin_dir: Path = typer.Argument(..., help="Path to the plugin package to deploy"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    ref: str | None = typer.Option(
        None,
        "--ref",
        help="Deploy a pushed branch, tag or commit as-is, without pushing.",
    ),
    no_push: bool = typer.Option(
        False, "--no-push", help="Deploy the pushed 'main' as-is, without pushing HEAD first."
    ),
    push_only: bool = typer.Option(
        False,
        "--push-only",
        help="Push HEAD to 'main', or to the --branch branch, without deploying it to any instance.",
    ),
    branch: str | None = typer.Option(
        None,
        "--branch",
        help=(
            "Push HEAD to this branch on Canvas Platform instead of 'main', and deploy it. "
            "Platform deploys a commit not on 'main' only to your organization's test instances."
        ),
    ),
    snapshot: bool = typer.Option(
        False,
        "--snapshot",
        help=(
            "Push the committed contents of a plugin inside a larger repository, such as a "
            "monorepo, as one new commit on 'main' or on the --branch branch, leaving that "
            "repository's remotes alone."
        ),
    ),
    assume_yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help=(
            "Commit uncommitted changes without prompting, with the default message. "
            "Does not approve consent requests: a deployment that needs consent exits "
            "non-zero and lists them."
        ),
    ),
) -> None:
    """Publish the plugin's code to Canvas Platform and deploy it.

    The manifest `name` is a plain package name: lowercase, at most 256 characters,
    with an org prefix recommended. A name outside that rule deploys when Canvas Platform
    holds a plugin of exactly that name you can see, under its publisher, and Platform
    decides whether you may push and deploy it. Otherwise the publisher is the manifest
    `publisher`, else your organization whose prefix the name carries, else the only
    organization you can publish in, else, at a terminal, the organization you pick. A regular push records the pick in the manifest once the package is
    accepted, so the push commits it; --ref, --no-push and --snapshot print the
    manifest line to add instead.

    Without --ref or --no-push, deploy first runs the same checks as `canvas
    validate` and stops on a failure. It then registers the plugin, points the
    repository's `origin` at Canvas Platform with a credential helper, commits any
    uncommitted changes after you confirm, pushes HEAD to `main` and deploys that
    commit. A plugin that is not in a git repository yet is offered one.

    With no --instance, deploy targets the only instance you can deploy to and
    otherwise lists the choices. Consent requests for cross-plugin custom data
    access are shown and answered inline at a terminal. Under --yes, or without a
    terminal, they are listed and deploy exits non-zero without answering them.

    With --push-only, deploy registers and pushes the same way and stops there, so
    it needs no instance: the plugin's code, and its catalog listing, are updated
    on Canvas Platform without being deployed anywhere.

    With --snapshot, the plugin can sit anywhere inside a larger repository. Deploy
    refuses uncommitted changes in the package rather than committing them, builds
    a commit whose package folder is the package as committed at HEAD, and pushes
    it to `main` from a scratch repository, so the larger repository's `origin`
    and config are untouched. A commit on `main` tagged `snapshot-baseline/...`
    counts as the last snapshot. It refuses when `main` has changes to the package,
    such as a catalog listing edited in Canvas Platform, that the snapshot would
    replace, and asks at a terminal instead.

    With --branch, deploy pushes HEAD, or the snapshot commit, to that branch on
    Canvas Platform rather than `main`, and deploys that commit. Platform deploys a
    commit not on `main` only to your organization's test instances, and refuses
    other instances with a message naming them. It combines with --push-only and
    --snapshot, and is refused with --ref or --no-push and for `main` or the
    plugin's default branch. A snapshot on a branch builds on that branch's tip when
    it exists, and the checks against edits made in Canvas Platform and against
    rolling back read that branch. Otherwise it builds on `main` and the checks read
    `main`.
    """
    if push_only and (instance or ref is not None or no_push):
        raise typer.BadParameter(
            "--push-only pushes without deploying, so it takes no --instance, --ref or --no-push."
        )
    if snapshot and (ref is not None or no_push):
        raise typer.BadParameter(
            "--snapshot pushes a new commit, so it takes no --ref or --no-push."
        )
    if branch is not None and (ref is not None or no_push):
        raise typer.BadParameter(
            "--branch pushes HEAD to a branch, so it takes no --ref or --no-push."
        )
    if not plugin_dir.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_dir}' needs to be a valid directory")
    if branch is not None:
        _require_branch_name(plugin_dir, branch)
    name = manifest_name(plugin_dir)
    platform = auth.resolve_platform_url()
    client = PlatformClient(platform)
    # A legacy name Platform holds a plugin of for the person deploys as is: on an
    # instance a rename is a new plugin.
    held: str | None = (
        None
        if len(name) > PLUGIN_NAME_MAX_LENGTH or PLUGIN_NAME_PATTERN.fullmatch(name)
        else _legacy_publisher(client, name, manifest_publisher(plugin_dir))
    )
    if held is None:
        require_valid_name(name)
    pushing = ref is None and not no_push
    if pushing:
        require_folder_matches_name(plugin_dir, name)
        instance_plugin.validate(plugin_dir)

    publisher, picked = _publisher(
        client,
        plugin_dir,
        name,
        pushing=pushing,
        records=pushing and not snapshot,
        held=held,
    )
    if push_only:
        sha = _push(
            client,
            plugin_dir,
            publisher,
            name,
            platform,
            assume_yes=assume_yes,
            snapshot=snapshot,
            branch=branch,
            record_publisher=picked,
        )
        print(f"To install this commit on an instance: canvas deploy {plugin_dir} --ref {sha[:12]}")
        return

    # Resolved before pushing, so a deploy with no clear target moves nothing.
    targets = _resolve_instances(client, instance, "deploy_plugin", verb="deploy plugins to")
    if pushing:
        deploy_ref = _push(
            client,
            plugin_dir,
            publisher,
            name,
            platform,
            assume_yes=assume_yes,
            snapshot=snapshot,
            branch=branch,
            record_publisher=picked,
        )
    else:
        deploy_ref = ref or "main"

    print(f"Deploying {name}@{deploy_ref[:12]} to {', '.join(targets)}…")
    _dispatch(
        client,
        "deploy",
        [{"name": name, "ref": deploy_ref, "publisher": publisher}],
        targets,
        what=f"Deploy of {name}",
        assume_yes=assume_yes,
    )


# -- clone -------------------------------------------------------------------


def clone(
    name: str = typer.Argument(..., help="Name of the plugin to clone, e.g. intake"),
    directory: Path | None = typer.Argument(
        None, help="Where to clone it [default: a directory named after the plugin]"
    ),
    publisher: str | None = typer.Option(
        None,
        "--publisher",
        help="Organization slug that publishes the plugin, when two publishers share the name",
    ),
) -> None:
    """Clone a plugin's repository from Canvas Platform, ready to deploy."""
    platform = auth.resolve_platform_url()
    client = PlatformClient(platform)
    plugin = client.plugin(name, publisher)
    if plugin is None:
        by: str = f" published by '{publisher}'" if publisher else ""
        raise typer.BadParameter(
            f"Canvas Platform has no plugin named '{name}'{by} that you can see."
        )
    destination = directory or Path(name)
    if destination.exists():
        raise typer.BadParameter(f"'{destination}' already exists.")
    git.require_installed()
    git.clone(plugin["git_url"], destination, platform)
    print(f"Cloned {name} into {destination}.")
    print(f"Deploy it with: canvas deploy {destination / name}")


# -- init --------------------------------------------------------------------


def _choose_organization(
    organizations: list[dict[str, Any]], requested: str | None
) -> dict[str, Any]:
    if requested:
        for organization in organizations:
            if organization["slug"] == requested:
                return organization
        raise typer.BadParameter(
            f"You cannot publish plugins in '{requested}'. Choose from: "
            + ", ".join(o["slug"] for o in organizations)
        )
    if len(organizations) == 1:
        return organizations[0]
    print("Which organization publishes this plugin?")
    for number, organization in enumerate(organizations, start=1):
        prefix: str = (
            f" (prefix {organization['plugin_prefix']}__)"
            if organization.get("plugin_prefix")
            else ""
        )
        print(f"  {number}. {organization.get('name') or organization['slug']}{prefix}")
    choice: int = typer.prompt("Organization", type=click.IntRange(1, len(organizations)))
    return organizations[choice - 1]


def _package_dir(project_dir: Path) -> Path:
    """The directory holding the scaffolded manifest."""
    if (project_dir / "CANVAS_MANIFEST.json").exists():
        return project_dir
    return next(path.parent for path in project_dir.glob("*/CANVAS_MANIFEST.json"))


def init(
    plugin_type: str = typer.Argument(
        "handler",
        help="The type of plugin to create. Options are 'application' or 'handler'.",
    ),
    organization: str | None = typer.Option(
        None,
        "--org",
        help="Organization that publishes the plugin, when you can publish in several",
    ),
) -> None:
    """Create a new plugin.

    Signed in to Canvas Platform, the plugin is named `<your org prefix>__<package>` as a
    recommended convention, its manifest records the publisher, and it is registered
    with platform and given a git repository whose `origin` is platform. Signed out,
    it is scaffolded with the name you give.
    """
    platform = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is None:
        print(
            f"You are not signed in to Canvas Platform at {platform}, so this plugin is "
            "scaffolded without registration or a git repository. Running `canvas login` "
            "then `canvas init` gives a registered plugin."
        )
        instance_plugin.scaffold(plugin_type)
        return

    client = PlatformClient(platform)
    publishers = [
        o
        for o in client.me().get("organizations", [])
        if "push_plugin_code" in o.get("capabilities", []) and o.get("plugin_prefix")
    ]
    if not publishers:
        print(
            "None of your organizations on Canvas Platform lets you push plugin code, so "
            "this plugin is scaffolded without registration or a git repository. Once an "
            "organization admin gives you the Plugin developer role, `canvas login` then "
            "`canvas init` gives a registered plugin."
        )
        instance_plugin.scaffold(plugin_type)
        return

    chosen = _choose_organization(publishers, organization)
    git.require_installed()
    project_dir = instance_plugin.scaffold(plugin_type, prefix=chosen["plugin_prefix"])
    package_dir = _package_dir(project_dir)
    name = manifest_name(package_dir)
    try:
        require_valid_name(name)
    except typer.BadParameter as exc:
        raise typer.BadParameter(
            f"The scaffolded name '{name}' is not a valid plugin name. {exc.message} "
            "Then run `canvas deploy`."
        ) from exc
    write_manifest_publisher(package_dir, chosen["slug"])

    registered = client.register_plugin(chosen["slug"], name)
    print(f"Registered {name} with Canvas Platform.")
    if git.repo_root(package_dir) == project_dir.resolve():
        result = git.run(project_dir, "init")
        if result.returncode != 0:
            raise git.GitError(f"git init failed: {result.stderr.strip()}")
        git.connect_remote(project_dir, registered["git_url"], platform)
        print(f"Initialized a git repository at {project_dir} with origin {registered['git_url']}.")
    print(f"Deploy it with: canvas deploy {package_dir}")


# -- config and uninstall ----------------------------------------------------


def _managed(
    name: str,
    instances: list[str],
    host: str | None,
    command: str,
) -> tuple[PlatformClient, dict[str, Any]] | None:
    """Platform's record of ``name`` when the command goes through platform, else None.

    When every named target is localhost or another host that is not a Canvas instance,
    which platform can never manage, the answer is None without asking platform, and no
    deprecation notice prints, since `canvas login` cannot serve those hosts. With no
    ``--instance`` or ``--host``, the target is credentials.ini's default host, so a
    default that is not a Canvas instance gets the same answer. Otherwise, signed in, a
    plugin platform manages for the person (see ``_managed_record``) goes through platform, each
    ``--instance`` must be one platform manages for the person, and any other plugin
    aimed at a Canvas instance, or named with no ``--instance``, ``--host`` or
    credentials.ini default, is refused with the way to sign out; with no ``--instance``
    or ``--host`` and no credentials.ini default, or a default that is a Canvas instance,
    platform is asked first. Signed out, the answer is None: the caller uses
    credentials.ini, and the deprecation notice for ``command`` is printed when the
    credentials.ini target is a Canvas instance.

    Args:
        name (str): The plugin name.
        instances (list[str]): The ``--instance`` slugs.
        host (str | None): The ``--host`` option.
        command (str): The command as typed after ``canvas``, for the deprecation notice.

    Returns:
        tuple[PlatformClient, dict[str, Any]] | None: The client and plugin record, or None
            for credentials.ini.

    Raises:
        click.ClickException: Signed in, and platform does not manage the plugin or an
            ``--instance``.
    """
    if (instances or host) and all(
        instance_slug(url) is None for url in _direct_hosts(instances, host)
    ):
        return None
    if not (instances or host):
        default: str | None = configured_default_host()
        if default is not None and instance_slug(default) is None:
            return None
    platform = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is not None:
        # With no --instance or --host and a credentials.ini default that is a Canvas
        # instance (or none at all), platform chooses the targets from the plugin's
        # installs, so it is asked first.
        client = PlatformClient(platform)
        plugin = _managed_record(client, name)
        if plugin is not None:
            for slug in dict.fromkeys(instances):
                require_managed(client, slug)
            return client, plugin
        if not (instances or host) and configured_default_host() is None:
            raise refuse_unmanaged(f"Canvas Platform does not manage {name}.", name)
        if any(instance_slug(url) is not None for url in _direct_hosts(instances, host)):
            raise refuse_unmanaged(f"Canvas Platform does not manage {name}.", name)
    print_credentials_ini_deprecation(command)
    return None


def _managed_record(client: PlatformClient, name: str) -> dict[str, Any] | None:
    """Platform's record of ``name`` when Platform manages it for the person, else None.

    An instance can hold a plugin of that name from a direct ``canvas install`` while
    another organization publishes one of that name on Platform, and Platform does not tie
    a name's prefix to a publisher, so the record counts only when one of the person's
    organizations publishes it, which Platform prefers when several share the name, or when
    the name carries its publisher's prefix (the slug lowercased, ``-`` to ``_``, then
    ``__``). A Canvas employee reaches every organization, so for one the record always
    counts, and Platform's capability check on each request decides what the command may do.
    A 409 ``ambiguous`` (several publishers, none the person's) counts as unmanaged.

    Args:
        client (PlatformClient): The signed-in platform client.
        name (str): The plugin name.

    Returns:
        dict[str, Any] | None: The plugin record, or None when Platform does not manage it
            for the person.
    """
    try:
        plugin: dict[str, Any] | None = client.plugin(name)
    except PlatformError as error:
        if error.code == "ambiguous":
            return None
        raise
    if plugin is None:
        return None
    publisher: str = str(plugin.get("publisher") or "")
    if publisher and name.startswith(f"{publisher.lower().replace('-', '_')}__"):
        return plugin
    me: dict[str, Any] = client.me()
    if me.get("canvas_employee"):
        return plugin
    yours: set[str] = {str(o["slug"]) for o in me.get("organizations", [])}
    return plugin if publisher in yours else None


def _entry(name: str, plugin: dict[str, Any]) -> dict[str, str]:
    """The deployment entry for a managed plugin, naming its publisher when Platform gave one."""
    publisher: Any = plugin.get("publisher")
    return {"name": name} | ({"publisher": str(publisher)} if publisher else {})


def _direct_hosts(instances: list[str], host: str | None) -> list[str]:
    """The instance URLs for the direct-to-instance path."""
    if instances and host:
        raise typer.BadParameter("Pass either --instance or --host, not both.")
    if instances:
        return [get_default_host(slug) for slug in dict.fromkeys(instances)]
    return [get_default_host(host)]


def _refuse_host_for_managed(name: str, host: str | None) -> None:
    if host:
        raise typer.BadParameter(
            f"'{name}' is managed by Canvas Platform; name its instances with --instance "
            "rather than --host."
        )


def _installed_on(plugin: dict[str, Any]) -> set[str]:
    return {install["instance"] for install in plugin.get("installs", [])}


def _parse_pair(item: str) -> tuple[str, str]:
    key, separator, value = item.partition("=")
    if not separator or not key:
        raise typer.BadParameter(f"Invalid variable format: '{item}'. Use key=value.")
    return key, value


def set_variables(
    plugin_name: str = typer.Argument(..., help="Plugin name to configure"),
    variables: list[str] = typer.Argument(
        None, help="Variables to set, e.g. Key=value (keeps each one's declared sensitivity)"
    ),
    secret: list[str] = typer.Option(
        [],
        "--secret",
        help="Set a variable no revision declares as sensitive, e.g. Key=value (repeatable)",
    ),
    variable: list[str] = typer.Option(
        [],
        "--variable",
        help="Set a variable no revision declares as non-sensitive, e.g. Key=value (repeatable)",
    ),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """Set a plugin's variables.

    For a plugin Canvas Platform manages, the values are stored in platform and a
    configure deployment brings them to the running plugin. A variable's
    sensitivity comes from the manifest; --secret and --variable say it for a key
    no revision declares. Without --instance, the only instance the plugin is
    installed on that you can configure is targeted.

    For any other plugin, the values are written to the instance directly.
    """
    parsed: list[tuple[str, str, bool | None]] = [
        *((*_parse_pair(item), None) for item in variables or []),
        *((*_parse_pair(item), True) for item in secret),
        *((*_parse_pair(item), False) for item in variable),
    ]
    if not parsed:
        raise typer.BadParameter(
            "Provide at least one variable: KEY=value, --secret KEY=value, or --variable KEY=value."
        )

    managed = _managed(plugin_name, instance, host, "config set")
    if managed is None:
        pairs = [f"{key}={value}" for key, value, _ in parsed]
        for url in _direct_hosts(instance, host):
            instance_plugin.update(
                name=plugin_name, package_path=None, is_enabled=None, secrets=pairs, host=url
            )
        return

    _refuse_host_for_managed(plugin_name, host)
    client, plugin = managed
    targets = _resolve_instances(
        client,
        instance,
        "configure_plugin",
        verb=f"configure {plugin_name} on",
        among=_installed_on(plugin),
    )
    for slug in targets:
        for key, value, sensitive in parsed:
            client.set_variable(slug, plugin_name, key, value, sensitive)
    print(f"Stored {len(parsed)} value(s) for {plugin_name} on {', '.join(targets)}.")
    _dispatch(
        client,
        "configure",
        [_entry(plugin_name, plugin)],
        targets,
        what=f"Configuring {plugin_name}",
    )


def unset_variables(
    plugin_name: str = typer.Argument(..., help="Plugin name to configure"),
    keys: list[str] = typer.Argument(..., help="Variable keys to clear, e.g. API_KEY"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """Clear a plugin's variable values.

    For a plugin Canvas Platform manages, the values are cleared in platform and a
    configure deployment removes them from the running plugin. For any other
    plugin, each value is set to empty on the instance directly.
    """
    managed = _managed(plugin_name, instance, host, "config unset")
    if managed is None:
        for url in _direct_hosts(instance, host):
            instance_plugin.update(
                name=plugin_name,
                package_path=None,
                is_enabled=None,
                secrets=[f"{key}=" for key in keys],
                host=url,
            )
        return

    _refuse_host_for_managed(plugin_name, host)
    client, plugin = managed
    targets = _resolve_instances(
        client,
        instance,
        "configure_plugin",
        verb=f"configure {plugin_name} on",
        among=_installed_on(plugin),
    )
    for slug in targets:
        for key in keys:
            client.clear_variable(slug, plugin_name, key)
    print(f"Cleared {len(keys)} value(s) for {plugin_name} on {', '.join(targets)}.")
    _dispatch(
        client,
        "configure",
        [_entry(plugin_name, plugin)],
        targets,
        what=f"Configuring {plugin_name}",
    )


def _switch(plugin_name: str, instance: list[str], host: str | None, *, action: str) -> None:
    """Enable or disable ``plugin_name`` through platform, or on the instance directly.

    Args:
        plugin_name (str): The plugin to switch.
        instance (list[str]): The ``--instance`` slugs; empty targets the only instance the
            plugin is installed on that the person can deploy to.
        host (str | None): The ``--host`` for a plugin platform does not manage.
        action (str): ``enable`` or ``disable``.
    """
    managed = _managed(plugin_name, instance, host, action)
    if managed is None:
        direct = instance_plugin.enable if action == "enable" else instance_plugin.disable
        for url in _direct_hosts(instance, host):
            direct(name=plugin_name, host=url)
        return

    _refuse_host_for_managed(plugin_name, host)
    client, plugin = managed
    verb = "Enabling" if action == "enable" else "Disabling"
    targets = _resolve_instances(
        client,
        instance,
        "deploy_plugin",
        verb=f"{action} {plugin_name} on",
        among=_installed_on(plugin),
    )
    _dispatch(
        client,
        action,
        [_entry(plugin_name, plugin)],
        targets,
        what=f"{verb} {plugin_name}",
    )


def enable(
    plugin_name: str = typer.Argument(..., help="Plugin name to enable"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """Enable a plugin.

    For a plugin Canvas Platform manages, an enable deployment switches it on at each
    --instance. Without --instance, the only instance the plugin is installed on that
    you can deploy to is targeted. For any other plugin, it is enabled on the instance
    directly.
    """
    _switch(plugin_name, instance, host, action="enable")


def disable(
    plugin_name: str = typer.Argument(..., help="Plugin name to disable"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """Disable a plugin.

    For a plugin Canvas Platform manages, a disable deployment switches it off at each
    --instance. Without --instance, the only instance the plugin is installed on that
    you can deploy to is targeted. For any other plugin, it is disabled on the instance
    directly.
    """
    _switch(plugin_name, instance, host, action="disable")


def list_variables(
    plugin_name: str = typer.Argument(..., help="Plugin name to list variables for"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """List a plugin's variables and whether each is set.

    For a plugin Canvas Platform manages, the keys come from platform. Without
    --instance, the only instance the plugin is installed on is used. Values are never
    printed. For any other plugin, the variables are read from the instance directly.
    """
    managed = _managed(plugin_name, instance, host, "config list")
    if managed is None:
        for url in _direct_hosts(instance, host):
            instance_plugin.list_secrets(plugin=plugin_name, host=url)
        return

    _refuse_host_for_managed(plugin_name, host)
    client, plugin = managed
    if instance:
        targets = list(dict.fromkeys(instance))
    else:
        installed = sorted(_installed_on(plugin))
        if len(installed) != 1:
            where = f" It is installed on: {', '.join(installed)}." if installed else ""
            raise typer.BadParameter(
                f"Name the instance to list {plugin_name}'s variables on with --instance.{where}"
            )
        targets = installed
    for slug in targets:
        if len(targets) > 1:
            print(f"{slug}:")
        variables = client.variables(slug, plugin_name)
        if not variables:
            print("No variables configured.")
        for variable in variables:
            display = "[set]" if variable.get("set") else "[not set]"
            annotation = "  (sensitive)" if variable.get("sensitive") else ""
            print(f"  {variable['key']} = {display}{annotation}")


def uninstall(
    plugin_name: str = typer.Argument(..., help="Plugin name to uninstall"),
    instance: list[str] = typer.Option([], "--instance", help=_INSTANCE_HELP),
    force: bool = typer.Option(
        False,
        "--force",
        help="Uninstall an enabled plugin from an instance directly",
        show_default=False,
    ),
    host: str | None = typer.Option(None, "--host", help="Canvas instance URL or name"),
) -> None:
    """Uninstall a plugin.

    For a plugin Canvas Platform manages, an uninstall deployment removes it from
    each --instance, which is required. For any other plugin, it is removed from
    the instance directly.
    """
    managed = _managed(plugin_name, instance, host, "uninstall")
    if managed is None:
        for url in _direct_hosts(instance, host):
            instance_plugin.uninstall(name=plugin_name, force=force, host=url)
        return

    _refuse_host_for_managed(plugin_name, host)
    client, plugin = managed
    if not instance:
        installed = sorted(_installed_on(plugin))
        where = f" It is installed on: {', '.join(installed)}." if installed else ""
        raise typer.BadParameter(
            f"Name the instances to remove {plugin_name} from with --instance.{where}"
        )
    targets = list(dict.fromkeys(instance))
    print(f"Uninstalling {plugin_name} from {', '.join(targets)}…")
    _dispatch(
        client,
        "uninstall",
        [_entry(plugin_name, plugin)],
        targets,
        what=f"Uninstall of {plugin_name}",
    )
