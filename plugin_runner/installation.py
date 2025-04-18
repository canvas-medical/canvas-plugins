import json
import os
import shutil
import tarfile
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TypedDict, cast
from urllib import parse

import psycopg
import requests
import sentry_sdk
from psycopg import Connection
from psycopg.rows import dict_row

from logger import log
from plugin_runner.aws_headers import aws_sig_v4_headers
from plugin_runner.exceptions import InvalidPluginFormat, PluginInstallationError
from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    CUSTOMER_IDENTIFIER,
    MEDIA_S3_BUCKET_NAME,
    PLUGIN_DIRECTORY,
    SECRETS_FILE_NAME,
)

# Plugin "packages" include this prefix in the database record for the plugin and the S3 bucket key.
UPLOAD_TO_PREFIX = "plugins"


def open_database_connection() -> Connection:
    """Opens a psycopg connection to the home-app database.

    When running within Aptible, use the database URL, otherwise pull from
    the environment variables.
    """
    if os.getenv("DATABASE_URL"):
        parsed_url = parse.urlparse(os.getenv("DATABASE_URL"))

        return psycopg.connect(
            dbname=cast(str, parsed_url.path[1:]),
            user=cast(str, parsed_url.username),
            password=cast(str, parsed_url.password),
            host=cast(str, parsed_url.hostname),
            port=parsed_url.port,
        )

    APP_NAME = os.getenv("APP_NAME")

    return psycopg.connect(
        dbname=APP_NAME,
        user=os.getenv("DB_USERNAME", "app"),
        password=os.getenv("DB_PASSWORD", "app"),
        host=os.getenv("DB_HOST", f"{APP_NAME}-db"),
        port=os.getenv("DB_PORT", "5432"),
    )


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
            "SELECT name, package, version, key, value FROM plugin_io_plugin p "
            "LEFT JOIN plugin_io_pluginsecret s ON p.id = s.plugin_id WHERE is_enabled"
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
def download_plugin(plugin_package: str) -> Generator[Path, None, None]:
    """Download the plugin package from the S3 bucket."""
    method = "GET"
    host = f"s3-{AWS_REGION}.amazonaws.com"
    bucket = MEDIA_S3_BUCKET_NAME
    customer_identifier = CUSTOMER_IDENTIFIER
    path = f"/{bucket}/{customer_identifier}/{plugin_package}"
    payload = b"This is required for the AWS headers because it is part of the signature"
    pre_auth_headers: dict[str, str] = {}
    query: dict[str, str] = {}
    headers = aws_sig_v4_headers(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        pre_auth_headers,
        "s3",
        AWS_REGION,
        host,
        method,
        path,
        query,
        payload,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        prefix_dir = Path(temp_dir) / UPLOAD_TO_PREFIX
        prefix_dir.mkdir()  # create an intermediate directory reflecting the prefix
        download_path = Path(temp_dir) / plugin_package

        with open(download_path, "wb") as download_file:
            response = requests.request(method=method, url=f"https://{host}{path}", headers=headers)
            download_file.write(response.content)

        yield download_path


def install_plugin(plugin_name: str, attributes: PluginAttributes) -> None:
    """Install the given Plugin's package into the runtime."""
    try:
        log.info(f'Installing plugin "{plugin_name}", version {attributes["version"]}')

        plugin_installation_path = Path(PLUGIN_DIRECTORY) / plugin_name

        # if plugin exists, first uninstall it
        if plugin_installation_path.exists():
            uninstall_plugin(plugin_name)

        with download_plugin(attributes["package"]) as plugin_file_path:
            extract_plugin(plugin_file_path, plugin_installation_path)

        install_plugin_secrets(plugin_name=plugin_name, secrets=attributes["secrets"])
    except Exception as e:
        log.error(f'Failed to install plugin "{plugin_name}", version {attributes["version"]}')
        sentry_sdk.capture_exception(e)

        raise PluginInstallationError() from e


def extract_plugin(plugin_file_path: Path, plugin_installation_path: Path) -> None:
    """Extract plugin in `file` to the given `path`."""
    log.info(f'Extracting plugin at "{plugin_file_path}"')

    archive: tarfile.TarFile | None = None

    try:
        if tarfile.is_tarfile(plugin_file_path):
            try:
                with open(plugin_file_path, "rb") as file:
                    archive = tarfile.TarFile.open(fileobj=file)
                    archive.extractall(plugin_installation_path, filter="data")
            except tarfile.ReadError as e:
                log.error(f"Unreadable tar archive: '{plugin_file_path}'")
                sentry_sdk.capture_exception(e)

                raise InvalidPluginFormat from e
        else:
            log.error(f"Unsupported file format: '{plugin_file_path}'")
            raise InvalidPluginFormat
    finally:
        if archive:
            archive.close()


def install_plugin_secrets(plugin_name: str, secrets: dict[str, str]) -> None:
    """Write the plugin's secrets to disk in the package's directory."""
    log.info(f"Writing plugin secrets for '{plugin_name}'")

    secrets_path = Path(PLUGIN_DIRECTORY) / plugin_name / SECRETS_FILE_NAME

    # Did the plugin ship a secrets.json? TOO BAD, IT'S GONE NOW.
    if Path(secrets_path).exists():
        os.remove(secrets_path)

    with open(str(secrets_path), "w") as f:
        json.dump(secrets, f)


def disable_plugin(plugin_name: str) -> None:
    """Disable the given plugin."""
    conn = open_database_connection()
    conn.cursor().execute(
        "UPDATE plugin_io_plugin SET is_enabled = false WHERE name = %s", (plugin_name,)
    )
    conn.commit()
    conn.close()

    uninstall_plugin(plugin_name)


def uninstall_plugin(plugin_name: str) -> None:
    """Remove the plugin from the filesystem."""
    log.info(f'Uninstalling plugin "{plugin_name}"')

    plugin_path = Path(PLUGIN_DIRECTORY) / plugin_name

    if plugin_path.exists():
        shutil.rmtree(plugin_path)


def install_plugins() -> None:
    """Install all enabled plugins."""
    log.info("Installing plugins")

    if Path(PLUGIN_DIRECTORY).exists():
        shutil.rmtree(PLUGIN_DIRECTORY)

    os.mkdir(PLUGIN_DIRECTORY)

    for plugin_name, attributes in enabled_plugins().items():
        try:
            install_plugin(plugin_name, attributes)
        except PluginInstallationError as e:
            disable_plugin(plugin_name)

            log.error(
                f'Installation failed for plugin "{plugin_name}", version {attributes["version"]};'
                " the plugin has been disabled"
            )

            sentry_sdk.capture_exception(e)

            continue

    return None
