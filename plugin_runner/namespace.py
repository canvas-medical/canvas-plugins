import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import cast
from urllib import parse

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from logger import log
from plugin_runner.exceptions import PluginInstallationError
from settings import PLUGIN_DIRECTORY, SECRETS_FILE_NAME

# Secret key names for namespace access credentials.
READ_ACCESS_KEY = "namespace_read_access_key"
READ_WRITE_ACCESS_KEY = "namespace_read_write_access_key"

# Default: wait up to 60 seconds for the schema manager to create a namespace.
NAMESPACE_WAIT_TIMEOUT = int(os.getenv("NAMESPACE_WAIT_TIMEOUT", "60"))

# Namespace format: org__name — lowercase alphanumeric/underscore on each side.
# Shared with the manifest JSON Schema in canvas_cli/utils/validators/manifest_schema.py.
NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$")


def is_schema_manager() -> bool:
    """Return True if this process should perform DDL operations.

    Schema creation, partition setup, and table migrations should only run
    once per deployment. In Aptible this means the first 'cmd' container
    (APTIBLE_PROCESS_TYPE=cmd, APTIBLE_PROCESS_INDEX=0). Outside Aptible
    (local development) DDL is always allowed.
    """
    aptible_process_type = os.getenv("APTIBLE_PROCESS_TYPE")
    if not aptible_process_type:
        return True
    return aptible_process_type == "cmd" and os.getenv("APTIBLE_PROCESS_INDEX", "0") == "0"


PG_NAMEDATALEN = 63
_CHANNEL_PREFIX = "ns_ready_"


def _namespace_notify_channel(namespace: str) -> str:
    """Return the PostgreSQL NOTIFY channel name for a namespace.

    PostgreSQL silently truncates identifiers to 63 characters (NAMEDATALEN - 1).
    If the full channel name would exceed this limit, we replace the namespace
    portion with a short hash to guarantee both sides of the LISTEN/NOTIFY
    pair use the same string.
    """
    full = f"{_CHANNEL_PREFIX}{namespace}"
    if len(full) <= PG_NAMEDATALEN:
        return full
    # Use a 16-char hex digest (8 bytes of entropy) — collision-resistant
    # enough for a channel name, and leaves room for the prefix.
    short_hash = hashlib.sha256(namespace.encode()).hexdigest()[:16]
    return f"{_CHANNEL_PREFIX}{short_hash}"


def compute_models_hash(plugin_path: Path) -> str:
    """Compute a SHA-256 hash of the plugin's models/ directory contents.

    The hash is deterministic: sorted ``*.py`` filenames and their contents
    are fed into the hasher in order.  All containers extract the same plugin
    package, so the hash is identical across processes.

    Args:
        plugin_path: Root directory of the extracted plugin.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    hasher = hashlib.sha256()
    models_dir = plugin_path / "models"
    if not models_dir.exists():
        return hasher.hexdigest()
    for file_path in sorted(models_dir.glob("*.py")):
        hasher.update(file_path.name.encode())
        hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def open_database_connection() -> Connection:
    """Opens a psycopg connection to the home-app database.

    When running within Aptible, use the database URL, otherwise pull from
    the environment variables.
    """
    database_url = os.getenv("CANVAS_PLUGINS_BOUNCER_DATABASE_URL") or os.getenv("DATABASE_URL")
    if database_url:
        parsed_url = parse.urlparse(database_url)

        return psycopg.connect(
            dbname=parsed_url.path[1:],
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


def wait_for_namespace(
    namespace: str,
    plugin_name: str,
    models_hash: str,
    timeout: int = NAMESPACE_WAIT_TIMEOUT,
) -> None:
    """Block until a namespace is fully ready for a specific plugin, or raise after timeout.

    Uses PostgreSQL LISTEN/NOTIFY for instant notification when the schema
    manager completes DDL migrations.  The function subscribes via ``LISTEN``
    *before* checking the ``schema_version`` sentinel, so a ``NOTIFY`` that
    fires between the check and the wait is never missed.

    Falls back to the ``schema_version`` table for the case where the schema manager
    finishes before this function starts listening.

    Args:
        namespace: The namespace schema name to wait for.
        plugin_name: Name of the plugin whose readiness to check.
        models_hash: Expected SHA-256 hash of the plugin's models/ directory.
        timeout: Maximum seconds to wait before raising.

    Raises:
        PluginInstallationError: If the namespace does not become ready within the timeout.
    """
    channel = _namespace_notify_channel(namespace)
    expected_payload = f"{plugin_name}:{models_hash}"

    with open_database_connection() as conn:
        conn.autocommit = True
        conn.execute(f"LISTEN {channel}")

        # Check AFTER subscribing so any NOTIFY sent between this check and
        # the wait below is queued on the connection and not lost.
        if namespace_ready(namespace, plugin_name, models_hash):
            log.info(f"Namespace '{namespace}' is ready for plugin '{plugin_name}' (hash match)")
            return

        log.info(
            f"Waiting for namespace '{namespace}' plugin '{plugin_name}' to be initialized "
            f"(listening on '{channel}', timeout {timeout}s) ..."
        )

        for notify in conn.notifies(timeout=timeout):
            if notify.channel == channel and notify.payload == expected_payload:
                log.info(
                    f"Namespace '{namespace}' is ready for plugin '{plugin_name}' "
                    f"(received NOTIFY with matching payload)"
                )
                return

        # Generator exhausted without matching notification — timeout.
        raise PluginInstallationError(
            f"Timed out after {timeout}s waiting for namespace '{namespace}' "
            f"to be created by the schema manager."
        )


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


def namespace_ready(namespace: str, plugin_name: str, models_hash: str) -> bool:
    """Check if a namespace has completed migration setup for a specific plugin's models hash.

    Returns True when the namespace schema exists AND the ``schema_version``
    sentinel table contains a row for *plugin_name* whose ``models_hash``
    matches *models_hash*.

    Args:
        namespace: The namespace schema name to check.
        plugin_name: Name of the plugin whose readiness to check.
        models_hash: Expected SHA-256 hash of the plugin's models/ directory.

    Returns:
        True if the namespace is ready for this version of the plugin's models, False otherwise.
    """
    with open_database_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "SELECT count(*) AS count FROM pg_catalog.pg_namespace WHERE nspname = %s",
            (namespace,),
        )
        row = cursor.fetchone()
        if not row or row["count"] == 0:
            return False

        cursor.execute(
            f"SELECT models_hash FROM {namespace}.schema_version WHERE plugin_name = %s",
            (plugin_name,),
        )
        row = cursor.fetchone()
        return row is not None and row["models_hash"] == models_hash


def mark_namespace_ready(namespace: str, plugin_name: str, models_hash: str) -> None:
    """Write the readiness sentinel for a plugin and notify waiting containers.

    Upserts a row keyed on *plugin_name* in the ``schema_version`` table with
    the current *models_hash*, then sends a PostgreSQL ``NOTIFY`` whose payload
    is ``plugin_name:models_hash`` so that non-schema-manager containers
    (blocked in ``wait_for_namespace``) can filter by plugin.

    Both operations are in the same transaction, so the notification fires
    atomically at commit time.

    The ``schema_version`` table is guaranteed to exist because
    ``create_namespace_schema`` (which always runs the idempotent init SQL) is
    called before this function.

    Args:
        namespace: The namespace schema name.
        plugin_name: Name of the plugin whose models are ready.
        models_hash: SHA-256 hash of the plugin's models/ directory.
    """
    channel = _namespace_notify_channel(namespace)
    payload = f"{plugin_name}:{models_hash}"
    with open_database_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO {namespace}.schema_version (plugin_name, models_hash) "
            f"VALUES (%s, %s) "
            f"ON CONFLICT (plugin_name) DO UPDATE SET models_hash = %s, completed_at = NOW()",
            (plugin_name, models_hash, models_hash),
        )
        cursor.execute("SELECT pg_notify(%s, %s)", (channel, payload))
        conn.commit()


def is_valid_namespace_name(namespace: str) -> bool:
    """Validate namespace name format.

    Valid namespaces must follow the pattern org__name (double underscore
    separator), where each side starts with a lowercase letter and contains
    only lowercase alphanumerics and underscores.

    This implicitly excludes reserved PostgreSQL schemas (pg_catalog,
    information_schema, etc.) since none match the org__name pattern.
    """
    return NAMESPACE_PATTERN.match(namespace) is not None and len(namespace) <= PG_NAMEDATALEN


def create_namespace_schema(namespace: str) -> dict[str, str] | None:
    """Create or update a shared data namespace schema.

    Always runs the idempotent init SQL to ensure all schema objects
    (including the ``schema_version`` sentinel table) exist.  For new namespaces,
    also generates and inserts authentication keys.

    Returns:
        Dict with 'namespace_read_access_key' and 'namespace_read_write_access_key' if namespace was created,
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
        is_new = row is None or row["count"] == 0

        # Always run the idempotent init SQL to ensure all schema objects
        # (including the schema_version sentinel table) exist.
        with open(Path(__file__).parent / "init_namespace_schema.sql") as f:
            sql_content = f.read()
            sql_content = sql_content.replace("{namespace}", namespace)
            conn.cursor().execute(sql_content)

        generated_keys = None

        if is_new:
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
                READ_ACCESS_KEY: read_key,
                READ_WRITE_ACCESS_KEY: read_write_key,
            }

            log.info(f"Created namespace schema '{namespace}' with auto-generated access keys")
        else:
            log.info(f"Namespace schema '{namespace}' already exists, init SQL re-applied")

        conn.commit()

    return generated_keys


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
        keys: Dict with 'namespace_read_access_key' and 'namespace_read_write_access_key'
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
        secret_value = secrets.get(READ_WRITE_ACCESS_KEY)
        if not secret_value:
            raise PluginInstallationError(
                f"Plugin '{plugin_name}' declares read_write access to namespace "
                f"'{schema_name}' but '{READ_WRITE_ACCESS_KEY}' secret is not configured."
            )
        granted_access = check_namespace_auth_key(schema_name, secret_value)
        if granted_access != "read_write":
            raise PluginInstallationError(
                f"Plugin '{plugin_name}' has invalid or insufficient access key "
                f"for namespace '{schema_name}'. Ensure '{READ_WRITE_ACCESS_KEY}' "
                f"contains a valid key from the namespace owner."
            )
        # Re-run idempotent init SQL to ensure all schema objects are up to date
        # (e.g. the schema_version table for namespaces created before it existed).
        create_namespace_schema(namespace=schema_name)
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
    secret_value = secrets.get(READ_ACCESS_KEY)
    if not secret_value:
        raise PluginInstallationError(
            f"Plugin '{plugin_name}' declares read access to namespace "
            f"'{schema_name}' but '{READ_ACCESS_KEY}' secret is not configured."
        )
    granted_access = check_namespace_auth_key(schema_name, secret_value)
    if not granted_access:
        raise PluginInstallationError(
            f"Plugin '{plugin_name}' has invalid access key for namespace "
            f"'{schema_name}'. Ensure '{READ_ACCESS_KEY}' contains a valid key "
            f"from the namespace owner."
        )
