import json
import tarfile
import tempfile
from pathlib import Path
from typing import Optional
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
    """Runs `poetry build` on `package` and returns the built archive."""
    if not package.exists() or not package.is_dir():
        raise typer.BadParameter(f"Couldn't build {package}, not a dir")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as file:
        with tarfile.open(file.name, "w:gz") as tar:
            tar.add(package, arcname=".")

        return Path(file.name)


def _get_name_from_metadata(host: str, token: str, package: Path) -> Optional[str]:
    """Extract metadata from a provided package and return the package name if it exists in the metadata."""
    try:
        metadata_response = requests.post(
            plugin_url(host, "extract-metadata"),
            headers={"Authorization": f"Bearer {token}"},
            files={"package": open(package, "rb")},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1)

    if metadata_response.status_code != requests.codes.ok:
        print(f"Status code {metadata_response.status_code}: {metadata_response.text}")
        raise typer.Exit(1)

    metadata = metadata_response.json()
    return metadata.get("name")


def get_base_plugin_template_path() -> Path:
    """Return context's base_plugin_template_path, so it can be used as a Typer default."""
    return context.plugin_template_dir / context.default_plugin_template_name


def init() -> None:
    """Create a new plugin."""
    template = get_base_plugin_template_path()
    try:
        project_dir = cookiecutter(str(template))
    except OutputDirExistsException:
        raise typer.BadParameter(f"The supplied directory already exists")

    print(f"Project created in {project_dir}")


def install(
    plugin_name: Path = typer.Argument(..., help="Path to plugin to install"),
    host: Optional[str] = typer.Option(
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
        r = requests.post(
            url,
            data={"is_enabled": True},
            files={"package": open(built_package_path, "rb")},
            headers={"Authorization": f"Bearer {token}"},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1)

    if r.status_code == requests.codes.created:
        print("Plugin successfully installed!")

    # If we got a bad_request, means there's a duplicate plugin and install can't handle that.
    # So we need to get the plugin-name from the package and call `update` directly
    elif r.status_code == requests.codes.bad_request:
        plugin_name = _get_name_from_metadata(host, token, built_package_path)
        update(plugin_name, built_package_path, is_enabled=True, host=host)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def uninstall(
    name: str = typer.Argument(..., help="Plugin name to uninstall"),
    host: Optional[str] = typer.Option(
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
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1)

    if r.status_code == requests.codes.no_content:
        print(r.text)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def enable(
    name: str = typer.Argument(..., help="Plugin name to enable"),
    host: Optional[str] = typer.Option(
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
        raise typer.Exit(1)

    if r.status_code == requests.codes.no_content:
        print(r.text)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def disable(
    name: str = typer.Argument(..., help="Plugin name to disable"),
    host: Optional[str] = typer.Option(
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
        raise typer.Exit(1)

    if r.status_code == requests.codes.no_content:
        print(r.text)
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def list(
    host: Optional[str] = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    )
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
        raise typer.Exit(1)

    if r.status_code == requests.codes.ok:
        for plugin in r.json().get("results", []):
            print(
                f"{plugin['name']}@{plugin['version']}\t{'enabled' if plugin['is_enabled'] else 'not enabled'}"
            )
    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)


def validate_manifest(
    plugin_name: Path = typer.Argument(..., help="Path to plugin to validate"),
) -> None:
    """Validate the Canvas Manifest json file."""
    if not plugin_name.exists():
        raise typer.BadParameter(f"Plugin '{plugin_name}' does not exist")

    if not plugin_name.is_dir():
        raise typer.BadParameter(f"Plugin '{plugin_name}' is not a directory, nothing to validate")

    manifest = plugin_name / "CANVAS_MANIFEST.json"

    if not manifest.exists():
        raise typer.BadParameter(
            f"Plugin '{plugin_name}' does not have a CANVAS_MANIFEST.json file to validate"
        )

    try:
        manifest_json = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        print("There was a problem loading the manifest file, please ensure it's valid JSON")
        raise typer.Abort()

    validate_manifest_file(manifest_json)

    print(f"Plugin '{plugin_name}' has a valid CANVAS_MANIFEST.json file")


def update(
    name: str = typer.Argument(..., help="Plugin name to update"),
    package: Optional[Path] = typer.Option(
        help="Path to a wheel or sdist file containing the python package to install",
        default=None,
    ),
    is_enabled: Optional[bool] = typer.Option(
        None, "--enable/--disable", show_default=False, help="Enable/disable the plugin"
    ),
    host: Optional[str] = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
) -> None:
    """Updates a plugin from an instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    if package:
        validate_package(package)

    token = get_or_request_api_token(host)

    print(f"Updating plugin {name} from {host} with {is_enabled=}, {package=}")

    binary_package = {"package": open(package, "rb")} if package else None

    url = plugin_url(host, name)

    try:
        r = requests.patch(
            url,
            data={"is_enabled": is_enabled} if is_enabled is not None else {},
            files=binary_package,
            headers={"Authorization": f"Bearer {token}"},
        )
    except requests.exceptions.RequestException:
        print(f"Failed to connect to {host}")
        raise typer.Exit(1)

    if r.status_code == requests.codes.ok:
        print("Plugin successfully updated!")

    else:
        print(f"Status code {r.status_code}: {r.text}")
        raise typer.Exit(1)
