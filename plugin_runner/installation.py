import json
import os
import shutil
import tarfile
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TypedDict

import requests
import sentry_sdk
from psycopg.rows import dict_row

from logger import log
from plugin_runner.aws_headers import aws_sig_v4_headers
from plugin_runner.ddl import generate_plugin_migrations  # noqa: F401 — re-export
from plugin_runner.exceptions import (
    InvalidPluginFormat,
    PluginInstallationError,
    PluginUninstallationError,
)
from plugin_runner.namespace import (
    compute_models_hash,  # noqa: F401 — re-export
    is_schema_manager,  # noqa: F401 — re-export
    mark_namespace_ready,  # noqa: F401 — re-export
    namespace_exists,
    open_database_connection,  # noqa: F401 — re-export
    setup_read_write_namespace,  # noqa: F401 — re-export
    verify_read_namespace_access,  # noqa: F401 — re-export
    wait_for_namespace,  # noqa: F401 — re-export
)
from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    CUSTOMER_IDENTIFIER,
    MANIFEST_FILE_NAME,
    MEDIA_S3_BUCKET_NAME,
    PLUGIN_DIRECTORY,
    SECRETS_FILE_NAME,
)

# Plugin "packages" include this prefix in the database record for the plugin and the S3 bucket key.
UPLOAD_TO_PREFIX = "plugins"


def clear_registered_models(plugin_name: str) -> None:
    """Remove previously registered models for a plugin from Django's app registry.

    This prevents 'Conflicting models' errors when a model is moved between
    files within a plugin's models/ directory during reinstallation.
    """
    from django.apps import apps

    apps.all_models.pop(plugin_name, None)
    apps.app_configs.pop(plugin_name, None)
    apps.clear_cache()


def register_plugin_app_config(plugin_name: str) -> None:
    """Register a minimal AppConfig for a plugin so Django's relation graph includes its models.

    Django's ``_populate_directed_relation_graph`` (which powers ``select_related``
    for reverse relations) iterates ``apps.get_models()``, and that only yields
    models from registered ``AppConfig`` instances.  Plugin models are added to
    ``apps.all_models`` during Sandbox execution, but without an ``AppConfig``
    they are invisible to the relation graph.  This function bridges that gap.
    """
    import types

    from django.apps import AppConfig, apps

    if plugin_name not in apps.all_models or plugin_name in apps.app_configs:
        return

    # Build a minimal AppConfig whose .models dict references the already-
    # populated all_models bucket for this plugin.  We subclass AppConfig with
    # a ``path`` class attribute so Django skips _path_from_module (our stub
    # module has no filesystem location).
    stub_module = types.ModuleType(plugin_name)

    config = type(
        f"{plugin_name}_AppConfig",
        (AppConfig,),
        {"path": "/dev/null"},
    )(plugin_name, stub_module)
    config.apps = apps
    config.models = apps.all_models[plugin_name]

    apps.app_configs[plugin_name] = config
    apps.clear_cache()


class PluginAttributes(TypedDict):
    """Attributes of a plugin."""

    version: str
    package: str
    secrets: dict[str, str]


def enabled_plugins(plugin_names: list[str] | None = None) -> dict[str, PluginAttributes]:
    """Returns a dictionary of enabled plugins and their attributes.

    If `plugin_names` is provided, only returns those plugins (if enabled).
    """
    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        base_query = (
            "SELECT name, package, version, key, value "
            "FROM plugin_io_plugin p "
            "LEFT JOIN plugin_io_pluginsecret s ON p.id = s.plugin_id "
            "WHERE is_enabled"
        )

        params: list[str] = []
        if plugin_names:
            placeholders = ",".join(["%s"] * len(plugin_names))
            base_query += f" AND name IN ({placeholders})"
            params.extend(plugin_names)

        cursor.execute(base_query, params)
        rows = cursor.fetchall()

    return _extract_rows_to_dict(rows)


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
            response.raise_for_status()

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

        # Clear any previously registered Django models for this plugin so that
        # models moved between files (e.g. from biography.py to __init__.py)
        # don't conflict with stale registrations from the prior version.
        # This must run on ALL containers, not just the schema manager.
        clear_registered_models(plugin_name)

        # Read the manifest to check for custom_data declaration
        manifest_path = plugin_installation_path / MANIFEST_FILE_NAME
        custom_data = None
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                custom_data = manifest.get("custom_data")

        # Initialize namespace schema and generate model migrations if custom_data is declared.
        # Only the schema manager (primary cmd container) performs DDL.
        # Non-schema-manager containers wait until the namespace is fully ready
        # (schema created + all DDL migrations complete).
        if custom_data and is_schema_manager():
            schema_name = custom_data["namespace"]
            declared_access = custom_data.get("access", "read")
            secrets = attributes["secrets"]

            log.info(f"Plugin '{plugin_name}' uses namespace '{schema_name}'")

            if declared_access == "read_write":
                can_create_tables = setup_read_write_namespace(plugin_name, schema_name, secrets)
            else:
                verify_read_namespace_access(plugin_name, schema_name, secrets)
                can_create_tables = False

            if can_create_tables:
                generate_plugin_migrations(plugin_name, plugin_installation_path, schema_name)
                models_hash = compute_models_hash(plugin_installation_path)
                mark_namespace_ready(schema_name, plugin_name, models_hash)
            else:
                log.info(
                    f"Plugin '{plugin_name}' has read-only access to namespace "
                    f"'{schema_name}' - skipping custom model table creation"
                )
        elif custom_data:
            schema_name = custom_data["namespace"]
            declared_access = custom_data.get("access", "read")

            if declared_access == "read_write":
                # read_write plugins need to wait for the schema manager to
                # finish DDL before they can safely use the tables.
                models_hash = compute_models_hash(plugin_installation_path)
                log.info(
                    f"Plugin '{plugin_name}' is not the schema manager — waiting for "
                    f"namespace '{schema_name}' to be initialized"
                )
                wait_for_namespace(schema_name, plugin_name, models_hash)
            else:
                # read-only plugins have no DDL to wait for — they just need
                # the namespace to already exist.
                if not namespace_exists(schema_name):
                    raise PluginInstallationError(
                        f"Plugin '{plugin_name}' declares read access to namespace "
                        f"'{schema_name}', but the namespace does not exist. "
                        f"A plugin with 'read_write' access must create the namespace first."
                    )
                log.info(
                    f"Plugin '{plugin_name}' has read access to namespace "
                    f"'{schema_name}' — namespace exists, proceeding"
                )
        else:
            log.info(f"Plugin '{plugin_name}' has no custom_data - skipping schema setup")

    except Exception as e:
        log.exception(f'Failed to install plugin "{plugin_name}", version {attributes["version"]}')
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
                log.exception(f"Unreadable tar archive: '{plugin_file_path}'")
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
    with open_database_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            "UPDATE plugin_io_plugin SET is_enabled = false WHERE name = %s", (plugin_name,)
        )
        conn.commit()

    uninstall_plugin(plugin_name)


def uninstall_plugin(plugin_name: str) -> None:
    """Remove the plugin from the filesystem."""
    try:
        log.info(f'Uninstalling plugin "{plugin_name}"')

        plugin_path = Path(PLUGIN_DIRECTORY) / plugin_name

        if plugin_path.exists():
            shutil.rmtree(plugin_path)
    except Exception as e:
        raise PluginUninstallationError() from e


def install_plugins() -> None:
    """Install all enabled plugins."""
    log.info("Installing plugins")
    try:
        plugins_dir = Path(PLUGIN_DIRECTORY).resolve()

        if plugins_dir.exists():
            shutil.rmtree(plugins_dir.as_posix())

        plugins_dir.mkdir(parents=False, exist_ok=True)
    except Exception as e:
        raise PluginInstallationError(
            f'Failed to reset plugin directory "{PLUGIN_DIRECTORY}": {e}"'
        ) from e

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
