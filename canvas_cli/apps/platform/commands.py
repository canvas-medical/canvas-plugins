"""Commands that publish, deploy and configure plugins through Canvas Platform.

Canvas Platform hosts each plugin's git repository and deploys it to the
instances it manages. These commands talk to platform's ``/api/v1/`` as the
person signed in with ``canvas login``:

  * ``canvas login`` / ``canvas logout``: the browser sign-in and its revocation.
  * ``canvas init``: scaffolds a plugin; signed in, it names it
    ``<prefix>__<package>`` and registers it with platform.
  * ``canvas deploy``: commits and pushes the working tree, then deploys it.
  * ``canvas clone``: checks out a plugin's repository, ready to push.
  * ``canvas config set`` / ``unset`` and ``canvas uninstall``: through platform
    for a plugin it manages, and directly against the instance otherwise.
  * ``canvas git-credential``: hidden; git runs it to mint a push token.
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

from canvas_cli.apps.auth.utils import get_default_host
from canvas_cli.apps.platform import auth, git
from canvas_cli.apps.platform.client import PlatformClient, PlatformError
from canvas_cli.apps.plugin import plugin as instance_plugin

PLUGIN_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$")

DEPLOYMENT_TERMINAL = frozenset({"succeeded", "partial", "failed", "cancelled"})
POLL_INTERVAL_SECONDS = 2.0
POLL_TIMEOUT_SECONDS = 300.0

_INSTANCE_HELP = "Instance slug to target (repeatable)"


# -- names and publishers ----------------------------------------------------


def manifest_name(plugin_dir: Path) -> str:
    """The manifest ``name`` of the plugin package in ``plugin_dir``."""
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


def require_prefixed_name(name: str) -> None:
    """Refuse a manifest name that does not carry a publisher prefix."""
    if PLUGIN_NAME_PATTERN.match(name):
        return
    package = re.sub(r"[^a-z0-9_]", "_", name.lower()).strip("_") or "package"
    raise typer.BadParameter(
        f"The plugin name '{name}' is not publisher-prefixed. Canvas Platform needs a "
        f"publisher-prefixed name like `<your org prefix>__{package}`, made of lowercase "
        "letters, digits and underscores, in the manifest, the package folder and its "
        "imports. `canvas login` lists your organizations' prefixes."
    )


def _matching_organization(me: dict[str, Any], name: str) -> dict[str, Any] | None:
    """The organization whose prefix the name carries; the longest prefix wins."""
    matches = [
        organization
        for organization in me.get("organizations", [])
        if organization.get("plugin_prefix")
        and name.startswith(f"{organization['plugin_prefix']}__")
    ]
    return max(matches, key=lambda o: len(o["plugin_prefix"]), default=None)


def _publisher(client: PlatformClient, name: str, *, pushing: bool) -> str:
    """The slug of the organization that publishes ``name``.

    It is the person's organization whose ``plugin_prefix`` the name carries. A
    Canvas employee, who reaches every organization without belonging to it, may
    also deploy a plugin that already exists under another publisher.
    """
    me = client.me()
    organization = _matching_organization(me, name)
    if organization is None:
        if me.get("canvas_employee") and (existing := client.plugin(name)):
            return str(existing["publisher"])
        prefixes = sorted(
            {o["plugin_prefix"] for o in me.get("organizations", []) if o.get("plugin_prefix")}
        )
        package = name.split("__", 1)[-1]
        yours = (
            f" Your organizations' prefixes: {', '.join(prefixes)}."
            if prefixes
            else " You do not belong to any organization on Canvas Platform."
        )
        raise typer.BadParameter(
            f"'{name}' does not start with the prefix of an organization you belong to, so "
            f"there is no publisher to deploy it as. Use a publisher-prefixed name like "
            f"`<your org prefix>__{package}`.{yours}"
        )
    if pushing and "push_plugin_code" not in organization.get("capabilities", []):
        raise typer.BadParameter(
            f"Your roles in {organization.get('name') or organization['slug']} do not include "
            "pushing plugin code. Ask an organization admin for the Plugin developer role."
        )
    return str(organization["slug"])


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


def _walk_consent(client: PlatformClient, deployment: dict[str, Any], *, assume_yes: bool) -> None:
    """Ask the person to approve or deny each consent request a deployment waits on."""
    pending = [r for r in deployment.get("consent_requests", []) if r.get("status") == "pending"]
    if not pending:
        return
    print(f"\nThis deployment needs consent ({len(pending)} request(s)):\n")
    for request in pending:
        instances = ", ".join(request.get("instances", []))
        print(
            f"  • {request.get('plugin')} asks for {request.get('access')} access to the "
            f"custom data namespace '{request.get('namespace')}' on {instances}."
        )
        if assume_yes or typer.confirm(f"    Approve request {request['id']}?", default=False):
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
    for target in deployment.get("targets", []):
        line = f"  {target.get('plugin')} on {target.get('instance')}: {target.get('status')}"
        if target.get("error"):
            line += f": {target['error']}"
        elif target.get("status") == "skipped":
            line += " (nothing to do there)"
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


def plugin_from_repo_path(path: str) -> str:
    """The plugin name in a repository path ``<publisher>/<name>.git``."""
    return path.strip("/").rsplit("/", 1)[-1].removesuffix(".git")


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
        credential = client.git_credentials(plugin_from_repo_path(path))
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
            "Move the package into its own repository, or use `canvas clone` to check it out."
        )


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
    assume_yes: bool = typer.Option(
        False, "--yes", "-y", help="Approve all consent requests non-interactively"
    ),
) -> None:
    """Publish the plugin's code to Canvas Platform and deploy it.

    The manifest `name` must be publisher-prefixed, `<your org prefix>__<package>`,
    and the prefix decides which of your organizations publishes the plugin.

    Without --ref or --no-push, deploy registers the plugin, points the
    repository's `origin` at Canvas Platform with a credential helper, commits any
    uncommitted changes after you confirm, pushes HEAD to `main` and deploys that
    commit. A plugin that is not in a git repository yet is offered one.

    With no --instance, deploy targets the only instance you can deploy to and
    otherwise lists the choices. Consent requests for cross-plugin custom data
    access are shown and answered inline.
    """
    if not plugin_dir.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_dir}' needs to be a valid directory")
    name = manifest_name(plugin_dir)
    require_prefixed_name(name)

    pushing = ref is None and not no_push
    platform = auth.resolve_platform_url()
    client = PlatformClient(platform)
    publisher = _publisher(client, name, pushing=pushing)
    targets = _resolve_instances(client, instance, "deploy_plugin", verb="deploy plugins to")

    if pushing:
        git.ensure_repo(plugin_dir)
        _require_package_at_repo_root(plugin_dir)
        registered = client.register_plugin(publisher, name)
        git.connect_remote(plugin_dir, registered["git_url"], platform)
        git.commit_working_tree_interactively(plugin_dir)
        branch = registered.get("default_branch") or "main"
        git.push_head(plugin_dir, branch)
        deploy_ref = git.head_sha(plugin_dir)
        print(f"Pushed {deploy_ref[:12]} to {branch}.")
    else:
        deploy_ref = ref or "main"

    print(f"Deploying {name}@{deploy_ref[:12]} to {', '.join(targets)}…")
    _dispatch(
        client,
        "deploy",
        [{"name": name, "ref": deploy_ref}],
        targets,
        what=f"Deploy of {name}",
        assume_yes=assume_yes,
    )


# -- clone -------------------------------------------------------------------


def clone(
    name: str = typer.Argument(..., help="Name of the plugin to clone, e.g. acme__intake"),
    directory: Path | None = typer.Argument(
        None, help="Where to clone it [default: a directory named after the plugin]"
    ),
) -> None:
    """Clone a plugin's repository from Canvas Platform, ready to deploy."""
    platform = auth.resolve_platform_url()
    client = PlatformClient(platform)
    plugin = client.plugin(name)
    if plugin is None:
        raise typer.BadParameter(f"Canvas Platform has no plugin named '{name}' that you can see.")
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
        print(f"  {number}. {organization.get('name')} (prefix {organization['plugin_prefix']}__)")
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

    Signed in to Canvas Platform, the plugin is named `<your org prefix>__<package>`,
    registered with platform, and given a git repository whose `origin` is
    platform. Signed out, it is scaffolded with the name you give.
    """
    platform = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is None:
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
            "this plugin is scaffolded without a publisher prefix and is not registered."
        )
        instance_plugin.scaffold(plugin_type)
        return

    chosen = _choose_organization(publishers, organization)
    git.require_installed()
    project_dir = instance_plugin.scaffold(plugin_type, prefix=chosen["plugin_prefix"])
    package_dir = _package_dir(project_dir)
    name = manifest_name(package_dir)
    if not PLUGIN_NAME_PATTERN.match(name):
        raise typer.BadParameter(
            f"The scaffolded name '{name}' is not a valid plugin name: after the prefix it "
            "must start with a letter and hold only lowercase letters, digits and "
            "underscores. Rename the package and its manifest `name`, then run `canvas deploy`."
        )

    registered = client.register_plugin(chosen["slug"], name)
    print(f"Registered {name} with Canvas Platform.")
    if git.repo_root(package_dir) == project_dir.resolve():
        result = git.run(project_dir, "init")
        if result.returncode != 0:
            raise typer.BadParameter(f"git init failed: {result.stderr.strip()}")
        git.connect_remote(project_dir, registered["git_url"], platform)
        print(f"Initialized a git repository at {project_dir} with origin {registered['git_url']}.")
    print(f"Deploy it with: canvas deploy {package_dir}")


# -- config and uninstall ----------------------------------------------------


def _managed(name: str) -> tuple[PlatformClient, dict[str, Any]] | None:
    """Platform's record of ``name`` when platform manages it, else None.

    A plugin platform manages has a publisher-prefixed name and answers
    ``GET /api/v1/plugins/<name>``. Without a platform session there is no way
    to ask, so the plugin is treated as one the instance manages; the instance
    then refuses a write to a platform-managed plugin and says so.
    """
    if not PLUGIN_NAME_PATTERN.match(name):
        return None
    platform = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is None:
        return None
    client = PlatformClient(platform)
    plugin = client.plugin(name)
    return (client, plugin) if plugin is not None else None


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

    managed = _managed(plugin_name)
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
        [{"name": plugin_name}],
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
    managed = _managed(plugin_name)
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
        [{"name": plugin_name}],
        targets,
        what=f"Configuring {plugin_name}",
    )


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
    managed = _managed(plugin_name)
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
        [{"name": plugin_name}],
        targets,
        what=f"Uninstall of {plugin_name}",
    )
