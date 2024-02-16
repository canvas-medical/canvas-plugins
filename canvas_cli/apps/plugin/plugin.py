import re
import subprocess
from pathlib import Path
from typing import Optional

import requests
import typer
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from canvas_cli.utils.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.urls.urls import CoreEndpoint
from canvas_cli.utils.validators import get_api_key, get_default_host

app = typer.Typer()


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

    try:
        output = subprocess.check_output(["poetry", "build"], cwd=package, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"'poetry build' failed with error: {e.output}")

    print.verbose(output)

    # The output should be in the 'output' variable.
    # We look for the line that says 'Built <path>'
    match = re.search(r"Built (.+)", output)
    if match:
        # Return the path of the built archive
        return package / "dist" / match.group(1)
    else:
        # If we can't find the path, raise an error
        raise RuntimeError("Could not find the path of the built archive in 'poetry build' output.")


def _get_name_from_metadata(host: str, api_key: str, package: Path) -> Optional[str]:
    """Extract metadata from a provided package and return the package name if it exists in the metadata."""
    try:
        metadata_response = requests.post(
            CoreEndpoint.PLUGIN.build(host, "extract-metadata"),
            headers={"Authorization": api_key},
            files={"package": open(package, "rb")},
        )
    except requests.exceptions.RequestException:
        print.json(f"Failed to connect to {host}", success=False)
        raise typer.Exit(1)

    if metadata_response.status_code != requests.codes.ok:
        print.response(metadata_response, success=False)
        raise typer.Exit(1)

    metadata = metadata_response.json()
    return metadata.get("name")


def get_base_plugin_template_path() -> Path:
    """Return context's base_plugin_template_path, so it can be used as a Typer default."""
    return context.plugin_template_dir / context.default_plugin_template_name


@app.command(short_help="Delete a disabled plugin from an instance")
def delete(
    name: str = typer.Argument(..., help="Plugin name to delete"),
    host: Optional[str] = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
    api_key: Optional[str] = typer.Option(
        help="Canvas api-key for the provided host", default=None
    ),
) -> None:
    """Delete a disabled plugin from an instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    url = CoreEndpoint.PLUGIN.build(host, name)

    print.verbose(f"Deleting {name} using {url}")

    if not (final_api_key := get_api_key(host, api_key)):
        raise typer.BadParameter("Please specify an api-key or add one via the `auth` command")

    try:
        r = requests.delete(
            url,
            headers={"Authorization": final_api_key},
        )
    except requests.exceptions.RequestException:
        print.json(f"Failed to connect to {host}", success=False)
        raise typer.Exit(1)

    if r.status_code == requests.codes.no_content:
        print.response(r)
    else:
        print.response(r, success=False)
        raise typer.Exit(1)


@app.command(short_help="Create a plugin from a template using Cookiecutter")
def init(
    template: Path = typer.Argument(default=get_base_plugin_template_path),
    no_input: bool = typer.Option(
        False, "--no-input", help="Don't prompt the user at command line", show_default=False
    ),
) -> None:
    """Create a plugin from a template using Cookiecutter."""
    try:
        project_dir = cookiecutter(str(template), no_input=no_input)
    except OutputDirExistsException:
        raise typer.BadParameter(f"The supplied directory already exists")

    print.json(f"Project created in {project_dir}", project_dir=project_dir)


@app.command(short_help="Installs a given Python package into a running Canvas instance")
def install(
    package: Path = typer.Argument(
        ...,
        help="Path to either a dir or wheel or sdist file containing the python package to install",
    ),
    host: Optional[str] = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
    api_key: Optional[str] = typer.Option(
        help="Canvas api-key for the provided host", default=None
    ),
) -> None:
    """Installs a given Python package into a running Canvas instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    if not (final_api_key := get_api_key(host, api_key)):
        raise typer.BadParameter("Please specify an api-key or add one via the `auth` command")

    if not package.exists():
        raise typer.BadParameter(f"Package {package} does not exist")

    if package.is_dir():
        built_package_path = _build_package(package)
    elif package.is_file() and (package.name.endswith("tar.gz") or package.name.endswith("whl")):
        built_package_path = package
    else:
        raise typer.BadParameter(
            f"Package {package} needs to be either a valid dir or a .tar.gz or .whl file"
        )

    print.verbose(f"Installing package: {built_package_path} into {host}")

    url = CoreEndpoint.PLUGIN.build(host)

    print.verbose(f"Posting {built_package_path.absolute()} to {url}")

    try:
        r = requests.post(
            url,
            data={"is_enabled": True},
            files={"package": open(built_package_path, "rb")},
            headers={"Authorization": final_api_key},
        )
    except requests.exceptions.RequestException:
        print.json(f"Failed to connect to {host}", success=False)
        raise typer.Exit(1)

    if r.status_code == requests.codes.created:
        print.response(r)
    # If we got a bad_request, means there's a duplicate plugin and install can't handle that.
    # So we need to get the plugin-name from the package and call `update` directly
    elif r.status_code == requests.codes.bad_request:
        plugin_name = _get_name_from_metadata(host, final_api_key, built_package_path)
        update(plugin_name, built_package_path, is_enabled=True, host=host, api_key=final_api_key)
    else:
        print.response(r, success=False)
        raise typer.Exit(1)


@app.command(short_help="Lists all plugins from the instance")
def list(
    host: Optional[str] = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
    api_key: Optional[str] = typer.Option(
        help="Canvas api-key for the provided host", default=None
    ),
) -> None:
    """Lists all plugins from the instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    url = CoreEndpoint.PLUGIN.build(host)

    if not (final_api_key := get_api_key(host, api_key)):
        raise typer.BadParameter("Please specify an api-key or add one via the `auth` command")

    try:
        r = requests.get(
            url,
            headers={"Authorization": final_api_key},
        )
    except requests.exceptions.RequestException:
        print.json(f"Failed to connect to {host}", success=False)
        raise typer.Exit(1)

    if r.status_code == requests.codes.ok:
        print.response(r)
    else:
        print.response(r, success=False)
        raise typer.Exit(1)


@app.command(short_help="Updates a plugin from an instance")
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
    api_key: Optional[str] = typer.Option(
        help="Canvas api-key for the provided host", default=None
    ),
) -> None:
    """Updates a plugin from an instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    if package:
        validate_package(package)

    if not (final_api_key := get_api_key(host, api_key)):
        raise typer.BadParameter("Please specify an api-key or add one via the `auth` command")

    print.verbose(f"Updating plugin {name} from {host} with {is_enabled=}, {package=}")

    binary_package = {"package": open(package, "rb")} if package else None

    url = CoreEndpoint.PLUGIN.build(host, name)

    try:
        r = requests.patch(
            url,
            data={"is_enabled": is_enabled} if is_enabled is not None else {},
            files=binary_package,
            headers={"Authorization": final_api_key},
        )
    except requests.exceptions.RequestException:
        print.json(f"Failed to connect to {host}", success=False)
        raise typer.Exit(1)

    if r.status_code == requests.codes.ok:
        print.response(r)
    else:
        print.response(r, success=False)
        raise typer.Exit(1)
