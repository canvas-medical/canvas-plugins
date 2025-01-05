import json
import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib import parse

import boto3
import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

import settings

Archive = zipfile.ZipFile | tarfile.TarFile
# Plugin "packages" include this prefix in the database record for the plugin and the S3 bucket key.
UPLOAD_TO_PREFIX = "plugins"


class PluginError(Exception):
    """An exception raised for plugin-related errors."""


class PluginValidationError(PluginError):
    """An exception raised when a plugin package is not valid."""


class InvalidPluginFormat(PluginValidationError):
    """An exception raised when the plugin file format is not supported."""


class PluginInstallationError(PluginError):
    """An exception raised when a plugin fails to install."""


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


def enabled_plugins() -> dict[str, dict[str, str | dict[str, str]]]:
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


def _extract_rows_to_dict(rows: list[dict[str, Any]]) -> dict[str, dict[str, str | dict[str, str]]]:
    plugins = {}
    for row in rows:
        if row["name"] not in plugins:
            plugins[row["name"]] = {
                "version": row["version"],
                "package": row["package"],
                "secrets": {row["key"]: row["value"]} if row["key"] else {},
            }
        else:
            plugins[row["name"]]["secrets"][row["key"]] = row["value"]
    return plugins


def download_plugin(plugin_package: str) -> Path:
    """Download the plugin package from the S3 bucket."""
    s3 = boto3.client("s3")
    temp_dir = tempfile.mkdtemp()
    prefix_dir = Path(temp_dir) / UPLOAD_TO_PREFIX
    prefix_dir.mkdir()  # create an intermediate directory reflecting the prefix
    with open(Path(temp_dir) / plugin_package, "wb") as download_file:
        s3.download_fileobj(
            "canvas-client-media", f"{settings.CUSTOMER_IDENTIFIER}/{plugin_package}", download_file
        )
    return Path(temp_dir) / plugin_package


def install_plugin(plugin_name: str, attributes: dict[str, str | dict[str, str]]) -> None:
    """Install the given Plugin's package into the runtime."""
    try:
        print(f"Installing plugin '{plugin_name}'")

        plugin_installation_path = Path(settings.PLUGIN_DIRECTORY) / plugin_name

        # if plugin exists, first uninstall it
        if plugin_installation_path.exists():
            uninstall_plugin(plugin_name)

        plugin_file_path = download_plugin(attributes["package"])
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
