import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TypedDict, cast
from urllib import parse

import psycopg
import requests
import sentry_sdk
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db.models import DateField, Field, Index
from psycopg import Connection
from psycopg.rows import dict_row

from canvas_sdk.v1.data.base import CustomModel
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
    MANIFEST_FILE_NAME,
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


# Reserved PostgreSQL schema names that cannot be used as namespaces
RESERVED_SCHEMAS = frozenset(
    {
        "public",
        "pg_catalog",
        "pg_toast",
        "information_schema",
    }
)

RESERVED_SCHEMA_PREFIXES = ("pg_",)


def is_valid_namespace_name(namespace: str) -> bool:
    """Validate namespace name format and check against reserved names.

    Valid namespaces must:
    - Not be a reserved PostgreSQL schema name
    - Not start with a reserved prefix (pg_)
    - Follow the pattern: org__name (double underscore separator)
    """
    if namespace in RESERVED_SCHEMAS:
        return False

    if any(namespace.startswith(prefix) for prefix in RESERVED_SCHEMA_PREFIXES):
        return False

    # Require org__name format (validated by regex in manifest schema,
    # but double-check here for safety)
    return "__" in namespace


def namespace_exists(namespace: str) -> bool:
    """Check if a namespace schema exists in the database.

    Args:
        namespace: The namespace schema name to check.

    Returns:
        True if the namespace exists, False otherwise.
    """
    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT count(*) AS count FROM pg_catalog.pg_namespace WHERE nspname = %s",
            (namespace,),
        )
        row = cursor.fetchone()
        return row is not None and row["count"] > 0


def create_namespace_schema(namespace: str) -> dict[str, str] | None:
    """Create a shared data namespace schema if it doesn't exist.

    This initializes the namespace with:
    - namespace_auth table for authentication (with auto-generated keys)
    - custom_attribute and attribute_hub tables for data storage

    Returns:
        Dict with 'read_access_key' and 'read_write_access_key' if namespace was created,
        None if namespace already existed.
    """
    if not is_valid_namespace_name(namespace):
        raise ValueError(f"Invalid namespace name: {namespace}")

    log.info(f"Creating namespace schema '{namespace}'")

    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT count(*) AS count FROM pg_catalog.pg_namespace WHERE nspname = %s",
            (namespace,),
        )
        row = cursor.fetchone()

        generated_keys = None

        if row is None or row["count"] == 0:
            # Execute SQL file for namespace schema initialization
            with open(Path(__file__).parent / "init_namespace_schema.sql") as f:
                sql_content = f.read()
                sql_content = sql_content.replace("{namespace}", namespace)
                conn.cursor().execute(sql_content)

            # Generate UUID keys for read and read_write access
            read_key = str(uuid.uuid4())
            read_write_key = str(uuid.uuid4())

            # Insert hashed keys into namespace_auth
            read_key_hash = hashlib.sha256(read_key.encode()).hexdigest()
            read_write_key_hash = hashlib.sha256(read_write_key.encode()).hexdigest()

            cursor.execute(
                f"""
                INSERT INTO {namespace}.namespace_auth (key_hash, access_level, description)
                VALUES (%s, %s, %s), (%s, %s, %s)
                """,
                (
                    read_key_hash,
                    "read",
                    "Auto-generated read access key",
                    read_write_key_hash,
                    "read_write",
                    "Auto-generated read_write access key",
                ),
            )

            generated_keys = {
                "read_access_key": read_key,
                "read_write_access_key": read_write_key,
            }

            log.info(f"Created namespace schema '{namespace}' with auto-generated access keys")
        else:
            log.info(f"Namespace schema '{namespace}' already exists")

        conn.commit()

    return generated_keys


def initialize_namespace_partitions(namespace: str) -> None:
    """Populate content types and create partitions for the custom_attribute table.

    This should be called every time a plugin with custom_data is installed,
    to ensure all content types and partitions exist.

    Args:
        namespace: The namespace schema name.
    """
    log.info(f"Initializing partitions for namespace '{namespace}'")

    with open_database_connection() as conn:
        with open(Path(__file__).parent / "init_namespace_partitions.sql") as f:
            sql_content = f.read()
            sql_content = sql_content.replace("{namespace}", namespace)
            conn.cursor().execute(sql_content)
        conn.commit()

    log.info(f"Initialized partitions for namespace '{namespace}'")


def check_namespace_auth_key(namespace: str, secret: str) -> str | None:
    """Verify a plugin's secret against the namespace's auth table.

    Args:
        namespace: The namespace schema name
        secret: The secret key value to verify

    Returns:
        The access level ('read' or 'read_write') if authorized, None if denied
    """
    key_hash = hashlib.sha256(secret.encode()).hexdigest()

    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"SELECT access_level FROM {namespace}.namespace_auth WHERE key_hash = %s",
            (key_hash,),
        )
        row = cursor.fetchone()

    if row:
        return row["access_level"]
    return None


def add_namespace_auth_key(
    namespace: str, secret: str, access_level: str, description: str = ""
) -> None:
    """Add an authentication key to a namespace.

    This is an administrative function for setting up namespace access.

    Args:
        namespace: The namespace schema name
        secret: The secret key to hash and store
        access_level: 'read' or 'read_write'
        description: Optional description of who this key is for
    """
    if access_level not in ("read", "read_write"):
        raise ValueError(f"Invalid access level: {access_level}")

    key_hash = hashlib.sha256(secret.encode()).hexdigest()

    with open_database_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {namespace}.namespace_auth (key_hash, access_level, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (key_hash) DO UPDATE SET access_level = %s, description = %s
                """,
                (key_hash, access_level, description, access_level, description),
            )
        conn.commit()
    log.info(f"Added/updated auth key for namespace '{namespace}' with access '{access_level}'")


def store_namespace_keys_as_plugin_secrets(plugin_name: str, keys: dict[str, str]) -> None:
    """Store namespace access keys as plugin secrets.

    This makes the auto-generated namespace keys visible in the UI so developers
    can retrieve them and use them when setting up additional plugins.

    The keys are stored in two places:
    1. The database (plugin_io_pluginsecret table) - for UI visibility
    2. The secrets.json file on disk - so the plugin can load immediately

    Args:
        plugin_name: The plugin that created the namespace
        keys: Dict with 'read_access_key' and 'read_write_access_key'
    """
    # Store in database for UI visibility
    with open_database_connection() as conn, conn.cursor() as cursor:
        # Get the plugin's database ID
        cursor.execute(
            "SELECT id FROM plugin_io_plugin WHERE name = %s",
            (plugin_name,),
        )
        row = cursor.fetchone()
        if not row:
            log.warning(
                f"Plugin '{plugin_name}' not found in database, cannot store namespace keys"
            )
            return

        plugin_id = row[0]

        # Insert the keys as plugin secrets
        for key_name, key_value in keys.items():
            cursor.execute(
                """
                INSERT INTO plugin_io_pluginsecret (plugin_id, key, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (plugin_id, key) DO UPDATE SET value = %s
                """,
                (plugin_id, key_name, key_value, key_value),
            )

        conn.commit()

    # Also update the secrets.json file on disk so the plugin can load immediately
    secrets_path = Path(PLUGIN_DIRECTORY) / plugin_name / SECRETS_FILE_NAME
    existing_secrets = {}
    if secrets_path.exists():
        with open(secrets_path) as f:
            existing_secrets = json.load(f)

    # Merge in the new keys
    existing_secrets.update(keys)

    with open(secrets_path, "w") as f:
        json.dump(existing_secrets, f)

    log.info(f"Stored {len(keys)} namespace access keys for plugin '{plugin_name}'")


SQL_STATEMENT_DELIMITER = "\n\n"


def generate_create_table_sql(schema_name: str, model_class: type[CustomModel]) -> str:
    """Generate CREATE TABLE SQL from Django model metadata with dynamic column addition.

    Args:
        schema_name: The PostgreSQL schema name (namespace or plugin name) where the table will be created.
        model_class: The Django model class to generate SQL for.

    Automatically detects SQLite and generates compatible SQL without schema prefixes.
    """
    # Detect if we're using SQLite
    is_sqlite = "sqlite3" in settings.DATABASES["default"]["ENGINE"]

    # For SQLite, don't use schema prefix; for PostgreSQL, use schema_name.table_name
    if is_sqlite:
        table_name = model_class._meta.db_table
    else:
        table_name = f"{schema_name}.{model_class._meta.db_table}"

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
            alter_statement = (
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {field.column} {field_sql};"
            )
            alter_statements.append(alter_statement)

    # Build index definitions
    index_statements = []
    for index in model_class._meta.indexes:
        index_sql = generate_index_sql(
            schema_name, model_class._meta.db_table, index, is_sqlite=is_sqlite
        )
        index_statements.append(index_sql)

    # Combine all statements
    all_statements = [create_table]
    if alter_statements:
        all_statements.extend(alter_statements)
    if index_statements:
        all_statements.extend(index_statements)

    return SQL_STATEMENT_DELIMITER.join(all_statements)


def generate_field_sql(field: Field, is_sqlite: bool = False) -> str:
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
    field_type = type(field)
    if field_type is BigAutoField:
        return "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"
    elif field_type in (CharField, TextField):
        return "TEXT"
    elif field_type is IntegerField:
        return "INTEGER"
    elif field_type is DateField:
        return "TEXT" if is_sqlite else "DATE"
    elif field_type is DateTimeField:
        return "TEXT" if is_sqlite else "TIMESTAMP WITH TIME ZONE"
    elif field_type is BooleanField:
        return "INTEGER" if is_sqlite else "BOOLEAN"
    elif field_type in (ForeignKey, OneToOneField):
        return "INTEGER"
    elif field_type is DecimalField:
        if is_sqlite:
            return "REAL"
        else:
            assert isinstance(field, DecimalField)
            max_digits = field.max_digits or 20
            decimal_places = field.decimal_places or 10
            return f"NUMERIC({max_digits},{decimal_places})"
    elif field_type is JSONField:
        return "TEXT" if is_sqlite else "JSONB"
    else:
        # Fallback for unknown field types
        return "TEXT"


def generate_index_sql(
    schema_name: str, table_name: str, index: Index, is_sqlite: bool = False
) -> str:
    """Generate CREATE INDEX SQL from Django Index object.

    Args:
        schema_name: The PostgreSQL schema name (namespace or plugin name).
        table_name: Name of the table (without schema prefix).
        index: Django Index object.
        is_sqlite: If True, generate SQLite-compatible SQL without schema prefix.

    Returns:
        CREATE INDEX SQL statement.
    """
    index_name = f"{schema_name}_{index.name}"

    # For SQLite, don't use schema prefix; for PostgreSQL, use schema_name.table_name
    table_full_name = table_name if is_sqlite else f"{schema_name}.{table_name}"

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
        return (
            f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} USING GIN({field_list});"
        )
    else:
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} ({field_list});"


def discover_model_files(plugin_path: Path) -> list[Path]:
    """Discover Python model files in a plugin's models/ directory.

    Args:
        plugin_path: Path to the plugin directory.

    Returns:
        Sorted list of .py file paths, excluding __init__.py.
        Empty list if models/ doesn't exist.
    """
    models_path = plugin_path / "models"
    if not models_path.exists():
        return []
    return sorted(f for f in models_path.glob("*.py") if f.name != "__init__.py")


def extract_models_from_module(plugin_name: str, model_file: Path) -> list[type[CustomModel]]:
    """Execute a model file in a sandbox and return discovered model classes.

    Args:
        plugin_name: Name of the plugin (used for module namespace).
        model_file: Path to a single .py model file.

    Returns:
        List of model classes whose __module__ starts with '{plugin_name}.models'.
    """
    module_name = f"{plugin_name}.models.{model_file.stem}"
    s = Sandbox(model_file, namespace=module_name)
    scope = s.execute()
    return [
        value
        for value in scope.values()
        if hasattr(value, "__module__") and value.__module__.startswith(f"{plugin_name}.models")
    ]


def should_create_table(model_class: type, schema_name: str) -> bool:
    """Determine whether a table should be created for the given model.

    Returns False for:
    - Objects without _meta (not Django models)
    - Proxy models
    - Models whose db_table references a different schema

    Args:
        model_class: A model class discovered from a plugin.
        schema_name: The target schema name.

    Returns:
        True if a CREATE TABLE statement should be generated.
    """
    if not hasattr(model_class, "_meta"):
        return False
    if model_class._meta.proxy:
        return False
    db_table = model_class._meta.original_attrs["db_table"]
    return "." not in db_table or db_table.startswith(f"{schema_name}")


def execute_create_table_sql(create_sql: str) -> None:
    """Execute CREATE TABLE SQL, handling SQLite vs PostgreSQL differences.

    SQLite requires executing one statement at a time; PostgreSQL can handle
    multiple statements in a single call.

    Args:
        create_sql: The SQL string (possibly multi-statement) to execute.
    """
    from django.db import connection

    is_sqlite = "sqlite3" in settings.DATABASES["default"]["ENGINE"]

    with connection.cursor() as cursor:
        if is_sqlite:
            for statement in create_sql.split(SQL_STATEMENT_DELIMITER):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
        else:
            cursor.execute(create_sql)


def generate_plugin_migrations(
    plugin_name: str, plugin_path: Path, schema_name: str | None = None
) -> list[type[CustomModel]]:
    """Generate Django migrations for plugin models.

    Args:
        plugin_name: Name of the plugin (used for module namespace).
        plugin_path: Path to the plugin directory.
        schema_name: The PostgreSQL schema where tables will be created. Defaults to plugin_name.

    Returns:
        List of discovered model classes.
    """
    if schema_name is None:
        schema_name = plugin_name
    log.info(f"Generating migrations for plugin '{plugin_name}' in schema '{schema_name}'")
    discovered_models: list[type[CustomModel]] = []
    try:
        if str(plugin_path) not in sys.path:
            sys.path.insert(0, str(plugin_path))

        for model_file in discover_model_files(plugin_path):
            models = extract_models_from_module(plugin_name, model_file)
            for model_class in models:
                discovered_models.append(model_class)
                if should_create_table(model_class, schema_name):
                    create_sql = generate_create_table_sql(schema_name, model_class)
                    log.info(f"Generated SQL for {model_class.__name__}:")
                    log.info(create_sql)
                    execute_create_table_sql(create_sql)
                elif hasattr(model_class, "_meta") and model_class._meta.proxy:
                    log.info(f"Skipping proxy model {model_class.__name__}")
                elif hasattr(model_class, "_meta"):
                    db_table = model_class._meta.original_attrs["db_table"]
                    log.warning(f"Skipping {db_table} because it references another schema")

    except Exception as e:
        log.exception(f"Failed to generate migrations for plugin '{plugin_name}'")
        raise e
    return discovered_models


def setup_read_write_namespace(plugin_name: str, schema_name: str, secrets: dict[str, str]) -> bool:
    """Set up namespace for a plugin with read_write access.

    Creates the namespace if it doesn't exist, or verifies the access key
    if it already exists.

    Returns:
        True if the plugin can create tables in the namespace.

    Raises:
        PluginInstallationError: If the access key is missing or invalid.
    """
    if namespace_exists(schema_name):
        # Namespace already exists - must verify the key grants read_write access
        secret_value = secrets.get("read_write_access_key")
        if not secret_value:
            raise PluginInstallationError(
                f"Plugin '{plugin_name}' declares read_write access to namespace "
                f"'{schema_name}' but 'read_write_access_key' secret is not configured."
            )
        granted_access = check_namespace_auth_key(schema_name, secret_value)
        if granted_access != "read_write":
            raise PluginInstallationError(
                f"Plugin '{plugin_name}' has invalid or insufficient access key "
                f"for namespace '{schema_name}'. Ensure 'read_write_access_key' "
                f"contains a valid key from the namespace owner."
            )
        return True

    # Namespace doesn't exist - create it
    generated_keys = create_namespace_schema(namespace=schema_name)
    if generated_keys:
        store_namespace_keys_as_plugin_secrets(plugin_name, generated_keys)
        log.info(
            f"Stored namespace access keys for '{schema_name}' in plugin secrets. "
            f"View them in the UI to share with other plugins."
        )
    return True


def verify_read_namespace_access(
    plugin_name: str, schema_name: str, secrets: dict[str, str]
) -> None:
    """Verify a plugin has valid read access to an existing namespace.

    Raises:
        PluginInstallationError: If the namespace doesn't exist or the access key
            is missing or invalid.
    """
    if not namespace_exists(schema_name):
        raise PluginInstallationError(
            f"Plugin '{plugin_name}' declares read access to namespace "
            f"'{schema_name}', but the namespace does not exist. "
            f"A plugin with 'read_write' access must create the namespace first."
        )
    secret_value = secrets.get("read_access_key")
    if not secret_value:
        raise PluginInstallationError(
            f"Plugin '{plugin_name}' declares read access to namespace "
            f"'{schema_name}' but 'read_access_key' secret is not configured."
        )
    granted_access = check_namespace_auth_key(schema_name, secret_value)
    if not granted_access:
        raise PluginInstallationError(
            f"Plugin '{plugin_name}' has invalid access key for namespace "
            f"'{schema_name}'. Ensure 'read_access_key' contains a valid key "
            f"from the namespace owner."
        )


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

        # Read the manifest to check for custom_data declaration
        manifest_path = plugin_installation_path / MANIFEST_FILE_NAME
        custom_data = None
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                custom_data = manifest.get("custom_data")

        # Initialize namespace schema and generate model migrations if custom_data is declared
        if custom_data:
            schema_name = custom_data["namespace"]
            declared_access = custom_data.get("access", "read")
            secrets = attributes["secrets"]

            log.info(f"Plugin '{plugin_name}' uses namespace '{schema_name}'")

            if declared_access == "read_write":
                can_create_tables = setup_read_write_namespace(plugin_name, schema_name, secrets)
            else:
                verify_read_namespace_access(plugin_name, schema_name, secrets)
                can_create_tables = False

            initialize_namespace_partitions(schema_name)

            if can_create_tables:
                generate_plugin_migrations(plugin_name, plugin_installation_path, schema_name)
            else:
                log.info(
                    f"Plugin '{plugin_name}' has read-only access to namespace "
                    f"'{schema_name}' - skipping custom model table creation"
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
