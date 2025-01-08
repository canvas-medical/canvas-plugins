import json
import os
import shutil
import tarfile
import tempfile
import zipfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypedDict
from urllib import parse

import boto3
import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

import settings
from canvas_sdk.exceptions import InvalidPluginFormat, PluginInstallationError

Archive = zipfile.ZipFile | tarfile.TarFile
# Plugin "packages" include this prefix in the database record for the plugin and the S3 bucket key.
UPLOAD_TO_PREFIX = "plugins"


def get_database_dict_from_url() -> dict[str, Any]:
    """Creates a psycopg ready dictionary from the home-app database URL."""
    parsed_url = parse.urlparse(os.getenv("DATABASE_URL"))
    db_name = parsed_url.path[1:]
    return {
        "dbname": db_name,
        "user": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "port": parsed_url.port,
    }


def get_database_dict_from_env() -> dict[str, Any]:
    """Creates a psycopg ready dictionary from the environment variables."""
    return {
        "dbname": "home-app",
        "user": os.getenv("DB_USERNAME", "app"),
        "password": os.getenv("DB_PASSWORD", "app"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5435"),
    }


def open_database_connection() -> Connection:
    """Opens a psycopg connection to the home-app database."""
    # When running within Aptible, use the database URL, otherwise pull from the environment variables.
    if os.getenv("DATABASE_URL"):
        database_dict = get_database_dict_from_url()
    else:
        database_dict = get_database_dict_from_env()
    conn = psycopg.connect(**database_dict)
    return conn


class PluginAttributes(TypedDict):
    """Attributes of a plugin."""

    version: str
    package: str
    secrets: dict[str, str]


def enabled_plugins() -> dict[str, PluginAttributes]:
    """Returns a dictionary of enabled plugins and their attributes."""
    conn = open_database_connection()

    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "select name, package, version, key, value from plugin_io_plugin p "
            "left join plugin_io_pluginsecret s on p.id = s.plugin_id where is_enabled"
        )
        rows = cursor.fetchall()
        plugins = _extract_rows_to_dict(rows)

    return plugins


def _extract_rows_to_dict(rows: list) -> dict[str, PluginAttributes]:
    plugins = {}
    for row in rows:
        if row["name"] not in plugins:
            plugins[row["name"]] = PluginAttributes(
                version=row["version"],
                package=row["package"],
                secrets={row["key"]: row["value"]} if row["key"] else {},
            )
        else:
            plugins[row["name"]]["secrets"][row["key"]] = row["value"]
    return plugins


@contextmanager
def download_plugin(plugin_package: str) -> Generator:
    """Download the plugin package from the S3 bucket."""
    s3 = boto3.client("s3")
    with tempfile.TemporaryDirectory() as temp_dir:
        prefix_dir = Path(temp_dir) / UPLOAD_TO_PREFIX
        prefix_dir.mkdir()  # create an intermediate directory reflecting the prefix
        download_path = Path(temp_dir) / plugin_package
        with open(download_path, "wb") as download_file:
            s3.download_fileobj(
                "canvas-client-media",
                f"{settings.CUSTOMER_IDENTIFIER}/{plugin_package}",
                download_file,
            )
        yield download_path


def install_plugin(plugin_name: str, attributes: PluginAttributes) -> None:
    """Install the given Plugin's package into the runtime."""
    try:
        print(f"Installing plugin '{plugin_name}'")

        plugin_installation_path = Path(settings.PLUGIN_DIRECTORY) / plugin_name

        # if plugin exists, first uninstall it
        if plugin_installation_path.exists():
            uninstall_plugin(plugin_name)

        with download_plugin(attributes["package"]) as plugin_file_path:
            extract_plugin(plugin_file_path, plugin_installation_path)

        install_plugin_secrets(plugin_name=plugin_name, secrets=attributes["secrets"])
    except Exception as ex:
        print(f"Failed to install plugin '{plugin_name}', version {attributes['version']}")
        raise PluginInstallationError() from ex


def extract_plugin(plugin_file_path: Path, plugin_installation_path: Path) -> None:
    """Extract plugin in `file` to the given `path`."""
    archive: Archive | None = None

    try:
        if zipfile.is_zipfile(plugin_file_path):
            archive = zipfile.ZipFile(plugin_file_path)
            archive.extractall(plugin_installation_path)
        elif tarfile.is_tarfile(plugin_file_path):
            try:
                with open(plugin_file_path, "rb") as file:
                    archive = tarfile.TarFile.open(fileobj=file)
                    archive.extractall(plugin_installation_path, filter="data")
            except tarfile.ReadError as ex:
                print(f"Unreadable tar archive: '{plugin_file_path}'")
                raise InvalidPluginFormat from ex
        else:
            print(f"Unsupported file format: '{plugin_file_path}'")
            raise InvalidPluginFormat
    finally:
        if archive:
            archive.close()


def install_plugin_secrets(plugin_name: str, secrets: dict[str, str]) -> None:
    """Write the plugin's secrets to disk in the package's directory."""
    print(f"Writing plugin secrets for '{plugin_name}'")

    secrets_path = Path(settings.PLUGIN_DIRECTORY) / plugin_name / settings.SECRETS_FILE_NAME

    # Did the plugin ship a secrets.json? TOO BAD, IT'S GONE NOW.
    if Path(secrets_path).exists():
        os.remove(secrets_path)

    with open(str(secrets_path), "w") as f:
        json.dump(secrets, f)


def disable_plugin(plugin_name: str) -> None:
    """Disable the given plugin."""
    conn = open_database_connection()
    conn.cursor().execute(
        "update plugin_io_plugin set is_enabled = false where name = %s", (plugin_name,)
    )
    conn.commit()
    conn.close()

    uninstall_plugin(plugin_name)


def uninstall_plugin(plugin_name: str) -> None:
    """Remove the plugin from the filesystem."""
    plugin_path = Path(settings.PLUGIN_DIRECTORY) / plugin_name

    if plugin_path.exists():
        shutil.rmtree(plugin_path)


def install_plugins() -> None:
    """Install all enabled plugins."""
    if Path(settings.PLUGIN_DIRECTORY).exists():
        shutil.rmtree(settings.PLUGIN_DIRECTORY)

    os.mkdir(settings.PLUGIN_DIRECTORY)

    for plugin_name, attributes in enabled_plugins().items():
        try:
            print(f"Installing plugin '{plugin_name}', version {attributes['version']}")
            install_plugin(plugin_name, attributes)
        except PluginInstallationError:
            disable_plugin(plugin_name)
            print(
                f"Installation failed for plugin '{plugin_name}', version {attributes['version']}. The plugin has been disabled"
            )
            continue

    return None
