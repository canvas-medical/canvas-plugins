import ast
import json
import tarfile
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast
from urllib.parse import urljoin

import requests
import typer
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token
from canvas_cli.utils.context import context
from canvas_cli.utils.validators import validate_manifest_file


def plugin_url(host: str, *paths: str) -> str:
    """Generates the plugin url for managing plugins in a Canvas instance."""
    join = "/".join(["plugin-io/plugins", "/".join(paths or [])])
    join = join if join.endswith("/") else join + "/"

    return urljoin(host, join)


def validate_package(package: Path) -> Path:
    """Validate if `package` Path exists and it is a file."""
    if not package.exists():
        raise typer.BadParameter(f"Package {package} does not exist")

    if not package.is_file():
        raise typer.BadParameter(f"Package {package} isn't a file")

    if not package.name.endswith("tar.gz") and not package.name.endswith("whl"):
        raise typer.BadParameter(f"Package {package} needs to be a tar.gz or a whl")

    return package


def _build_package(package: Path) -> Path:
    """Compresses `package` and returns the built archive, ignoring symlinks, hidden folders, and hidden files."""
    package = package.resolve()

    if not package.exists() or not package.is_dir():
        raise typer.BadParameter(f"Couldn't build {package}, not a dir")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as file:
        with tarfile.open(file.name, "w:gz") as tar:
            for root in package.rglob("*"):
                # Skip hidden files and directories (starting with '.') and symlinks
                if any(part.startswith(".") for part in root.parts) or root.is_symlink():
                    continue

                tar.add(root, arcname=root.relative_to(package))
        return Path(file.name)


def _get_name_from_metadata(host: str, token: str, package: Path) -> str | None:
    """Extract metadata from a provided package and return the package name if it exists in the metadata."""
    try:
        with open(package, "rb") as package_file:
            metadata_response = requests.post(
                plugin_url(host, "extract-metadata"),
                headers={"Authorization": f"Bearer {token}"},
                files={"package": package_file},
            )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if metadata_response.status_code != requests.codes.ok:
        print(f"Status code {metadata_response.status_code}: {metadata_response.text}")
        raise typer.Exit(1)

    metadata = metadata_response.json()
    return metadata.get("name")


def _get_meta_class(text: str, classname: str) -> ast.ClassDef | None:
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            class_def = node
            for b in class_def.body:
                if isinstance(b, ast.ClassDef) and b.name == "Meta":
                    return b
    return None


def _get_meta_properties(protocol_path: Path, classname: str) -> dict[str, str]:
    meta: dict[str, str] = {}

    if not protocol_path.exists():
        return meta

    meta_class = _get_meta_class(protocol_path.read_text(), classname)
    if not meta_class:
        return meta

    for meta_b in meta_class.body:
        if not isinstance(meta_b, ast.Assign):
            continue
        target_id = next((t.id for t in meta_b.targets if isinstance(t, ast.Name)), None)
        if not target_id:
            continue
        if isinstance(meta_b.value, ast.Constant):
            value = meta_b.value.value
        elif isinstance(meta_b.value, ast.List):
            value = [cast(ast.Constant, e).value for e in meta_b.value.elts]
        elif isinstance(meta_b.value, ast.Dict):
            keys = meta_b.value.keys
            values = meta_b.value.values
            value = {
                cast(ast.Constant, k).value: cast(ast.Constant, values[i]).value
                for i, k in enumerate(keys)
            }
        else:
            value = None
        meta[target_id] = value

    return meta


def _get_protocols_with_new_cqm_properties(
    protocol_classes: Iterable[dict[str, Any]], plugin: Path
) -> Iterable[dict[str, Any]] | None:
    """Extract the meta properties of any ClinicalQualityMeasure Protocols included in the plugin if they have changed."""
    has_updates = False
    protocol_props = []
    for p in protocol_classes:
        mod, classname = p["class"].split(":")
        mod = mod.replace(f"{plugin.name}.", "").replace(".", "/") + ".py"
        p_path: Path = plugin / mod
        meta = _get_meta_properties(p_path, classname)
        if meta and meta != p.get("meta"):
            has_updates = True
            protocol_props.append(p | {"meta": meta})
        else:
            protocol_props.append(p)

    return protocol_props if has_updates else None


def get_base_plugin_template_path(plugin_type: str) -> Path:
    """Return context's base_plugin_template_path, so it can be used as a Typer default."""
    match plugin_type:
        case "application":
            return context.plugin_template_dir / "application"
        case _:
            return context.plugin_template_dir / context.default_plugin_template_name


def init(
    plugin_type: str = typer.Argument(
        "protocol",
        help="The type of plugin to create. Options are 'application' or 'protocol'.",
    ),
) -> None:
    """Create a new plugin."""
    template = get_base_plugin_template_path(plugin_type)
    try:
        project_dir = cookiecutter(str(template))
    except OutputDirExistsException:
        raise typer.BadParameter("The supplied directory already exists") from None

    print(f"Project created in {project_dir}")


def install(
    plugin_name: Path = typer.Argument(..., help="Path to plugin to install"),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Install a plugin into a Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)

    if not plugin_name.exists():
        raise typer.BadParameter(f"Plugin '{plugin_name}' does not exist")

    if plugin_name.is_dir():
        validate_manifest(plugin_name)
        built_package_path = _build_package(plugin_name)
    else:
        raise typer.BadParameter(f"Plugin '{plugin_name}' needs to be a valid directory")

    print(f"Installing plugin: {built_package_path} into {host}")

    url = plugin_url(host)

    print(f"Posting {built_package_path.absolute()} to {url}")

    try:
        with open(built_package_path, "rb") as package:
            r = requests.post(
                url,
                data={"is_enabled": True},
                files={"package": package},
                headers={"Authorization": f"Bearer {token}"},
            )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.created:
        print(f"Plugin {plugin_name} successfully installed!")

    # If we got a conflict, means there's a duplicate plugin and install can't handle that.
    # So we need to get the plugin-name from the package and call `update` directly
    elif r.status_code == requests.codes.conflict and (
        package_name := _get_name_from_metadata(host, token, built_package_path)
    ):
        print(f"Plugin {package_name} already exists, updating instead...")
        update(package_name, built_package_path, is_enabled=True, host=host)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def uninstall(
    name: str = typer.Argument(..., help="Plugin name to uninstall"),
    force: bool = typer.Option(
        False, "--force", help="Force uninstallation of the plugin", show_default=False
    ),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Uninstall a plugin from a Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or or add one to the configuration file")

    url = plugin_url(host, name)

    print(f"Uninstalling {name} using {url}")

    token = get_or_request_api_token(host)

    try:
        r = requests.delete(
            url,
            headers={
                "Authorization": f"Bearer {token}",
            },
            params={"force": str(force)},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.no_content:
        print(f"Plugin {name} successfully uninstalled!")
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def enable(
    name: str = typer.Argument(..., help="Plugin name to enable"),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Enable a plugin from a Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or or add one to the configuration file")

    url = plugin_url(host, name)

    print(f"Enabling {name} using {url}")

    token = get_or_request_api_token(host)

    try:
        r = requests.patch(
            url,
            data={"is_enabled": True},
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.ok:
        print(f"Plugin {name} successfully enabled!")
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def disable(
    name: str = typer.Argument(..., help="Plugin name to disable"),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Disable a plugin from a Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or or add one to the configuration file")

    url = plugin_url(host, name)

    print(f"Disabling {name} using {url}")

    token = get_or_request_api_token(host)

    try:
        r = requests.patch(
            url,
            data={"is_enabled": False},
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.ok:
        print(f"Plugin {name} successfully disabled!")
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def list(
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """List all plugins from a Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    url = plugin_url(host)

    token = get_or_request_api_token(host)

    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.ok:
        plugins = r.json().get("results", [])
        if not plugins:
            print(f"No plugins are currently installed on {host}")
        for plugin in plugins:
            print(
                f"{plugin['name']}@{plugin['version']}\t{'enabled' if plugin['is_enabled'] else 'disabled'}"
            )
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def validate_manifest(
    plugin_name: Path = typer.Argument(..., help="Path to plugin to validate"),
) -> None:
    """Validate the Canvas Manifest json file."""
    if not plugin_name.exists():
        raise typer.BadParameter(f"Plugin {plugin_name} does not exist")

    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin {plugin_name} is not a directory, nothing to validate")

    manifest = plugin_name / "CANVAS_MANIFEST.json"

    if not manifest.exists():
        raise typer.BadParameter(
            f"Plugin {plugin_name} does not have a CANVAS_MANIFEST.json file to validate"
        )

    try:
        manifest_json = json.loads(manifest.read_text())
        protocols = manifest_json.get("components", {}).get("protocols", [])
        if new_protocols := _get_protocols_with_new_cqm_properties(protocols, plugin_name):
            print(
                f"Updating the CANVAS_MANIFEST.json file for {plugin_name} with CQM meta properties"
            )
            manifest_json["components"]["protocols"] = new_protocols
            manifest.write_text(json.dumps(manifest_json))
            manifest_json = json.loads(manifest.read_text())

    except json.JSONDecodeError:
        print("There was a problem loading the manifest file, please ensure it's valid JSON")
        raise typer.Abort() from None

    validate_manifest_file(manifest_json)

    print(f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file")


def update(
    name: str = typer.Argument(..., help="Plugin name to update"),
    package_path: Path | None = typer.Option(
        help="Path to a wheel or sdist file containing the python package to install",
        default=None,
    ),
    is_enabled: bool | None = typer.Option(
        None, "--enable/--disable", show_default=False, help="Enable/disable the plugin"
    ),
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Updates a plugin from an instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    if package_path:
        validate_package(package_path)

    token = get_or_request_api_token(host)

    print(f"Updating plugin {name} from {host} with {is_enabled=}, {package_path=}")

    url = plugin_url(host, name)

    try:
        data = {"is_enabled": is_enabled} if is_enabled is not None else {}
        headers = {"Authorization": f"Bearer {token}"}

        if package_path:
            with open(package_path, "rb") as package:
                r = requests.patch(
                    url,
                    data=data,
                    headers=headers,
                    files={"package": package},
                )
        else:
            r = requests.patch(
                url,
                data=data,
                headers=headers,
            )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1) from None

    if r.status_code == requests.codes.ok:
        print("Plugin successfully updated!")

    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)
