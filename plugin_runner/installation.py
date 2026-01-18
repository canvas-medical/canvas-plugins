import json
import os
import shutil
import sys
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
from django.contrib.postgres.indexes import GinIndex
from django.db.models import Index, DateField
from psycopg import Connection
from psycopg.rows import dict_row

from logger import log
from plugin_runner.aws_headers import aws_sig_v4_headers
from plugin_runner.exceptions import (
    InvalidPluginFormat,
    PluginInstallationError,
    PluginUninstallationError,
)
from plugin_runner.sandbox import Sandbox
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


def enabled_plugins(plugin_names: list[str] | None = None) -> dict[str, PluginAttributes]:
    """Returns a dictionary of enabled plugins and their attributes.

    If `plugin_names` is provided, only returns those plugins (if enabled).
    """
    conn = open_database_connection()

    with conn.cursor(row_factory=dict_row) as cursor:
        base_query = (
            "SELECT name, package, version, key, value "
            "FROM plugin_io_plugin p "
            "LEFT JOIN plugin_io_pluginsecret s ON p.id = s.plugin_id "
            "WHERE is_enabled"
        )

        params = []
        if plugin_names:
            placeholders = ",".join(["%s"] * len(plugin_names))
            base_query += f" AND name IN ({placeholders})"
            params.extend(plugin_names)

        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        plugins = _extract_rows_to_dict(rows)

    conn.close()

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
            response.raise_for_status()

            download_file.write(response.content)

        yield download_path


def create_plugin_schema(plugin_name: str) -> None:
    """Run database migrations for the given plugin."""
    log.info(f"Running migrations for plugin '{plugin_name}'")

    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "select count(*) as count from pg_catalog.pg_namespace where nspname = %s",
            (plugin_name,),
        )
        rows = cursor.fetchone()
        if rows["count"] == 0:
            # Execute SQL file for plugin schema initialization
            with open(Path(__file__).parent / "init_plugin_schema.sql") as f:
                sql_content = f.read()
                # Replace placeholder with actual plugin name
                sql_content = sql_content.replace("{plugin_name}", plugin_name)
                conn.cursor().execute(sql_content)
        # Execute SQL file to populate content types and create partitions. Always run this
        # to pick up any changes to available models
        with open(Path(__file__).parent / "init_plugin_partitions.sql") as f:
            sql_content = f.read()
            # Replace placeholder with actual plugin name
            sql_content = sql_content.replace("{plugin_name}", plugin_name)
            conn.cursor().execute(sql_content)
        conn.commit()


SQL_STATEMENT_DELIMITER = "\n\n"

def generate_create_table_sql(plugin_name: str, model_class) -> str:
    """Generate CREATE TABLE SQL from Django model metadata with dynamic column addition.

    Automatically detects SQLite and generates compatible SQL without schema prefixes.
    """
    from django.conf import settings

    # Detect if we're using SQLite
    is_sqlite = 'sqlite3' in settings.DATABASES['default']['ENGINE']

    # For SQLite, don't use schema prefix; for PostgreSQL, use plugin_name.table_name
    if is_sqlite:
        table_name = model_class._meta.db_table
    else:
        table_name = f"{plugin_name}.{model_class._meta.db_table}"

    # Separate primary key and regular fields
    pk_fields = []
    regular_fields = []

    for field in model_class._meta.local_fields:
        if field.primary_key:
            pk_fields.append(field)
        else:
            regular_fields.append(field)

    # Build initial table
    # For SQLite: include all fields in CREATE TABLE (no dynamic ALTER TABLE support)
    # For PostgreSQL: only include primary key, add other fields via ALTER TABLE
    field_definitions = []

    if is_sqlite:
        # SQLite: include all fields in CREATE TABLE
        for field in model_class._meta.local_fields:
            field_sql = generate_field_sql(field, is_sqlite=is_sqlite)
            field_definitions.append(f"    {field.column} {field_sql}")
    else:
        # PostgreSQL: only primary key fields initially
        for field in pk_fields:
            field_sql = generate_field_sql(field, is_sqlite=is_sqlite)
            field_definitions.append(f"    {field.column} {field_sql}")

    # Construct CREATE TABLE statement
    fields_sql = ",\n".join(field_definitions)
    create_table = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{fields_sql}\n);"

    # Generate ALTER TABLE statements for regular fields
    # SQLite doesn't support "IF NOT EXISTS" in ALTER TABLE, so for SQLite we'll
    # include all columns in the initial CREATE TABLE instead
    alter_statements = []
    if not is_sqlite:
        # PostgreSQL: use dynamic column addition with IF NOT EXISTS
        for field in regular_fields:
            field_sql = generate_field_sql(field, is_sqlite=is_sqlite)
            alter_statement = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {field.column} {field_sql};"
            alter_statements.append(alter_statement)

    # Build index definitions
    index_statements = []
    for index in model_class._meta.indexes:
        index_sql = generate_index_sql(plugin_name, model_class._meta.db_table, index, is_sqlite=is_sqlite)
        index_statements.append(index_sql)

    # Combine all statements
    all_statements = [create_table]
    if alter_statements:
        all_statements.extend(alter_statements)
    if index_statements:
        all_statements.extend(index_statements)

    return SQL_STATEMENT_DELIMITER.join(all_statements)


def generate_field_sql(field, is_sqlite: bool = False) -> str:
    """Convert Django field to database-specific column definition.

    Args:
        field: Django model field instance
        is_sqlite: If True, generate SQLite-compatible types; otherwise PostgreSQL types

    Returns:
        SQL column type definition
    """
    from django.db.models import (
        BigAutoField,
        BooleanField,
        CharField,
        DateTimeField,
        DecimalField,
        ForeignKey,
        IntegerField,
        JSONField,
        OneToOneField,
        TextField,
    )

    # We do not allow database constraints or default values.
    # Validations will be performed by the plugin and the plugin runner
    # This is a decision meant to protect us from customers doing dangerous things like adding a column with a
    # default value on a large table (table rewrite), or needing to alter a datatype to chnage a constraint

    if isinstance(field, BigAutoField):
        return "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"
    elif isinstance(field, CharField) or isinstance(field, TextField):
        return "TEXT"
    elif isinstance(field, IntegerField):
        return "INTEGER"
    elif isinstance(field, DateField):
        return "TEXT" if is_sqlite else "DATE"
    elif isinstance(field, DateTimeField):
        return "TEXT" if is_sqlite else "TIMESTAMP WITH TIME ZONE"
    elif isinstance(field, BooleanField):
        return "INTEGER" if is_sqlite else "BOOLEAN"
    elif isinstance(field, ForeignKey) or isinstance(field, OneToOneField):
        return "INTEGER"
    elif isinstance(field, DecimalField):
        if is_sqlite:
            return "REAL"
        else:
            max_digits = getattr(field, "max_digits", 10)
            decimal_places = getattr(field, "decimal_places", 2)
            return f"NUMERIC({max_digits},{decimal_places})"
    elif isinstance(field, JSONField):
        return "TEXT" if is_sqlite else "JSONB"
    else:
        # Fallback for unknown field types
        return "TEXT"


def generate_index_sql(plugin_name: str, table_name: str, index: Index, is_sqlite: bool = False) -> str:
    """Generate CREATE INDEX SQL from Django Index object.

    Args:
        plugin_name: Name of the plugin
        table_name: Name of the table (without schema prefix)
        index: Django Index object
        is_sqlite: If True, generate SQLite-compatible SQL without schema prefix

    Returns:
        CREATE INDEX SQL statement
    """
    index_name = f"{plugin_name}_{index.name}"

    # For SQLite, don't use schema prefix; for PostgreSQL, use plugin_name.table_name
    if is_sqlite:
        table_full_name = table_name
    else:
        table_full_name = f"{plugin_name}.{table_name}"

    field_parts = []
    for field in index.fields:
        if field.startswith("-"):
            # Descending order - remove the '-' prefix
            field_parts.append(f"{field[1:]} DESC")
        else:
            # Ascending order (default)
            field_parts.append(field)
    field_list = ", ".join(field_parts)

    # Support GIN indexes on JSONB fields
    if not is_sqlite and isinstance(index, GinIndex):
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} USING GIN({field_list});"
    else:
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} ({field_list});"


def generate_plugin_migrations(plugin_name: str, plugin_path: Path) -> None:
    """Generate Django migrations for plugin models."""
    log.info(f"Generating migrations for plugin '{plugin_name}'")
    try:
        # Add plugin directory to Python path
        if str(plugin_path) not in sys.path:
            sys.path.insert(0, str(plugin_path))

        # Dynamically load plugin models
        models_path = plugin_path / "models"
        if models_path.exists():
            # Load all model files in the plugin
            for model_file in models_path.glob("*.py"):
                if model_file.name == "__init__.py":
                    continue
                module_name = f"{plugin_name}.models.{model_file.stem}"
                print(f"Loading module {module_name} from {model_file}")
                s = Sandbox(model_file, namespace=module_name)
                cls = s.execute()
                print(cls.keys())

                # Generate CREATE TABLE SQL for each model
                for name, value in cls.items():
                    if hasattr(value, "__module__") and value.__module__.startswith(
                        f"{plugin_name}.models"
                    ):
                        if hasattr(value, "_meta"):
                            if value._meta.proxy:
                                continue
                            db_table = value._meta.original_attrs["db_table"]
                            if "." in db_table and not db_table.startswith(f"{plugin_name}"):
                                print(f"Skipping {db_table} because it references another schema")
                                continue
                            create_sql = generate_create_table_sql(plugin_name, value)
                            print(f"Generated SQL for {name}:")
                            print(create_sql)

                            # Execute the CREATE TABLE statements
                            # SQLite requires executing one statement at a time
                            from django.conf import settings
                            from django.db import connection

                            is_sqlite = 'sqlite3' in settings.DATABASES['default']['ENGINE']

                            with connection.cursor() as cursor:
                                if is_sqlite:
                                    # Split by double newline and execute each statement separately
                                    for statement in create_sql.split(SQL_STATEMENT_DELIMITER):
                                        statement = statement.strip()
                                        if statement:
                                            cursor.execute(statement)
                                else:
                                    # PostgreSQL can handle multiple statements
                                    cursor.execute(create_sql)

    except Exception as e:
        log.exception(f"Failed to generate migrations for plugin '{plugin_name}'")
        raise e


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

        # if ENABLE_MIGRATIONS:
        create_plugin_schema(plugin_name=plugin_name)

        # Generate and apply migrations for plugin models
        generate_plugin_migrations(plugin_name, plugin_installation_path)

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
    conn = open_database_connection()
    conn.cursor().execute(
        "UPDATE plugin_io_plugin SET is_enabled = false WHERE name = %s", (plugin_name,)
    )
    conn.commit()
    conn.close()

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
