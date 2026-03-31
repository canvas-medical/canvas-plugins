import sys
from pathlib import Path
from typing import Any, cast

from django.contrib.postgres.indexes import GinIndex
from django.db.models import Field, Index, OneToOneField, Q
from django.db.models.constraints import UniqueConstraint
from django.db.models.sql import Query

from canvas_sdk.v1.data.base import IS_SQLITE, CustomModel
from logger import log
from plugin_runner.sandbox import Sandbox, suppress_model_registration

SQL_STATEMENT_DELIMITER = "\n\n"


def generate_create_table_sql(schema_name: str, model_class: type[CustomModel]) -> str:
    """Generate CREATE TABLE SQL from Django model metadata with dynamic column addition.

    Args:
        schema_name: The PostgreSQL schema name (namespace or plugin name) where the table will be created.
        model_class: The Django model class to generate SQL for.

    Automatically detects SQLite and generates compatible SQL without schema prefixes.
    """
    from django.db import connection

    # For SQLite, don't use schema prefix; for PostgreSQL, use schema_name.table_name
    if IS_SQLITE:
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

    if IS_SQLITE:
        # SQLite: include all fields in CREATE TABLE
        for field in model_class._meta.local_fields:
            field_sql = generate_field_sql(field, connection)
            field_definitions.append(f"    {field.column} {field_sql}")
    else:
        # PostgreSQL: only primary key fields initially
        for field in pk_fields:
            field_sql = generate_field_sql(field, connection)
            field_definitions.append(f"    {field.column} {field_sql}")

    # Construct CREATE TABLE statement
    fields_sql = ",\n".join(field_definitions)
    create_table = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{fields_sql}\n);"

    # Generate ALTER TABLE statements for regular fields
    # SQLite doesn't support "IF NOT EXISTS" in ALTER TABLE, so for SQLite we'll
    # include all columns in the initial CREATE TABLE instead
    alter_statements = []
    if not IS_SQLITE:
        # PostgreSQL: use dynamic column addition with IF NOT EXISTS
        for field in regular_fields:
            field_sql = generate_field_sql(field, connection)
            alter_statement = (
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {field.column} {field_sql};"
            )
            alter_statements.append(alter_statement)

    # Build index definitions
    index_statements = []
    for index in model_class._meta.indexes:
        index_sql = generate_index_sql(
            schema_name,
            model_class._meta.db_table,
            index,
            model_class=model_class,
            is_sqlite=IS_SQLITE,
        )
        index_statements.append(index_sql)

    # Build unique constraint definitions
    constraint_statements = []

    # OneToOneFields imply uniqueness on the FK column. Django normally enforces
    # this with a UNIQUE constraint in the DDL, but our generate_field_sql strips
    # all constraints. Emit an explicit unique index to honor the intent.
    for field in model_class._meta.local_fields:
        if isinstance(field, OneToOneField) and not field.primary_key:
            uq_sql = generate_constraint_sql(
                schema_name,
                model_class._meta.db_table,
                UniqueConstraint(
                    fields=[field.column], name=f"uq_{model_class._meta.db_table}_{field.column}"
                ),
                model_class=model_class,
                is_sqlite=IS_SQLITE,
            )
            constraint_statements.append(uq_sql)

    for constraint in model_class._meta.constraints:
        if isinstance(constraint, UniqueConstraint):
            constraint_sql = generate_constraint_sql(
                schema_name,
                model_class._meta.db_table,
                constraint,
                model_class=model_class,
                is_sqlite=IS_SQLITE,
            )
            constraint_statements.append(constraint_sql)

    # Combine all statements
    all_statements = [create_table]
    if alter_statements:
        all_statements.extend(alter_statements)
    if index_statements:
        all_statements.extend(index_statements)
    if constraint_statements:
        all_statements.extend(constraint_statements)

    return SQL_STATEMENT_DELIMITER.join(all_statements)


def generate_field_sql(field: Field, connection: Any) -> str:
    """Convert Django field to database-specific column definition.

    Uses Django's field.db_type(connection) for type mapping, which automatically
    handles SQLite vs PostgreSQL differences. We override CharField/TextField to
    always use "text" so plugins can change max_length without a column migration.

    We do not allow database constraints or default values. Validations will be
    performed by the plugin and the plugin runner. This protects against dangerous
    operations like adding a column with a default value on a large table (table
    rewrite), or needing to alter a datatype to change a constraint.

    Args:
        field: Django model field instance
        connection: Django database connection

    Returns:
        SQL column type definition (e.g., "text", "integer PRIMARY KEY", "jsonb")
    """
    from django.db.models import CharField, DecimalField, TextField

    # CharField/TextField: always use "text" regardless of backend so plugins can
    # change max_length without needing a column type migration.
    if isinstance(field, (CharField, TextField)):
        db_type = "text"
    elif isinstance(field, DecimalField):
        # Apply defaults if the developer omitted max_digits/decimal_places
        max_digits = field.max_digits if field.max_digits is not None else 20
        decimal_places = field.decimal_places if field.decimal_places is not None else 10
        field.max_digits = max_digits
        field.decimal_places = decimal_places
        db_type = field.db_type(connection) or "text"
    else:
        db_type = field.db_type(connection) or "text"

    # Append PRIMARY KEY before the auto-increment suffix because SQLite
    # requires the order: INTEGER PRIMARY KEY AUTOINCREMENT
    if field.primary_key:
        db_type = f"{db_type} PRIMARY KEY"

    suffix = field.db_type_suffix(connection)  # type: ignore[attr-defined]
    if suffix:
        db_type = f"{db_type} {suffix}"

    return db_type


def _resolve_column_name(model_class: type[CustomModel], field_name: str) -> str:
    """Resolve a Django field name to its database column name.

    For example, a ForeignKey field named ``room`` resolves to column ``room_id``.
    If the field name is not found on the model (e.g. it's already a column name),
    it is returned unchanged.
    """
    try:
        field = cast(Field, model_class._meta.get_field(field_name))
        return str(field.column)
    except Exception:
        return field_name


def _compile_condition(condition: Q, model_class: type) -> str:
    """Compile a Django Q object into a SQL WHERE clause fragment.

    Uses the same approach as Django's ``Index._get_condition_sql``:
    build a Query with ``alias_cols=False`` (suppresses table name prefixes),
    compile to SQL, and inline quoted parameter values.

    Args:
        condition: A Django Q object representing the filter condition.
        model_class: The Django model class, needed for field resolution.

    Returns:
        A SQL expression string suitable for use after ``WHERE``.
    """
    from django.db import connection

    query = Query(model=model_class, alias_cols=False)
    where = query.build_where(condition)
    compiler = query.get_compiler(connection=connection)
    sql, params = where.as_sql(compiler, connection)
    # Instantiate the schema editor directly (not as a context manager) to
    # avoid opening a DB transaction — quote_value is pure computation.
    schema_editor = connection.SchemaEditorClass(connection)
    return sql % tuple(schema_editor.quote_value(p) for p in params)


def generate_index_sql(
    schema_name: str,
    table_name: str,
    index: Index,
    model_class: type | None = None,
    is_sqlite: bool = False,
) -> str:
    """Generate CREATE INDEX SQL from Django Index object.

    Args:
        schema_name: The PostgreSQL schema name (namespace or plugin name).
        table_name: Name of the table (without schema prefix).
        index: Django Index object.
        model_class: The Django model class, used to resolve field names to column names.
        is_sqlite: If True, generate SQLite-compatible SQL without schema prefix.

    Returns:
        CREATE INDEX SQL statement.
    """
    index_name = f"{schema_name}_{table_name}_{index.name}"

    # For SQLite, don't use schema prefix; for PostgreSQL, use schema_name.table_name
    table_full_name = table_name if is_sqlite else f"{schema_name}.{table_name}"

    field_parts = []
    for field in index.fields:
        if field.startswith("-"):
            # Descending order - remove the '-' prefix
            col = _resolve_column_name(model_class, field[1:]) if model_class else field[1:]
            field_parts.append(f"{col} DESC")
        else:
            col = _resolve_column_name(model_class, field) if model_class else field
            # Ascending order (default)
            field_parts.append(col)
    field_list = ", ".join(field_parts)

    # Compile optional WHERE clause for partial indexes
    condition = getattr(index, "condition", None)
    where_clause = ""
    if condition is not None:
        if model_class is None:
            raise ValueError("model_class is required when index has a condition")
        where_clause = f" WHERE {_compile_condition(condition, model_class)}"

    # Support GIN indexes on JSONB fields
    if not is_sqlite and isinstance(index, GinIndex):
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} USING GIN({field_list}){where_clause};"
    else:
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_full_name} ({field_list}){where_clause};"


def generate_constraint_sql(
    schema_name: str,
    table_name: str,
    constraint: UniqueConstraint,
    model_class: type | None = None,
    is_sqlite: bool = False,
) -> str:
    """Generate CREATE UNIQUE INDEX SQL from a Django UniqueConstraint.

    Uses CREATE UNIQUE INDEX IF NOT EXISTS for idempotency — safe to run on
    every deployment regardless of whether the constraint already exists.

    Args:
        schema_name: The PostgreSQL schema name (namespace or plugin name).
        table_name: Name of the table (without schema prefix).
        constraint: Django UniqueConstraint object.
        model_class: The Django model class, used to resolve field names to column names.
        is_sqlite: If True, generate SQLite-compatible SQL without schema prefix.

    Returns:
        CREATE UNIQUE INDEX IF NOT EXISTS SQL statement.
    """
    index_name = f"{schema_name}_{table_name}_{constraint.name}"
    table_full_name = table_name if is_sqlite else f"{schema_name}.{table_name}"
    if model_class:
        field_list = ", ".join(_resolve_column_name(model_class, f) for f in constraint.fields)
    else:
        field_list = ", ".join(constraint.fields)

    condition = getattr(constraint, "condition", None)
    where_clause = ""
    if condition is not None:
        if model_class is None:
            raise ValueError("model_class is required when constraint has a condition")
        where_clause = f" WHERE {_compile_condition(condition, model_class)}"

    return f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON {table_full_name} ({field_list}){where_clause};"


def discover_model_files(plugin_path: Path) -> list[Path]:
    """Discover Python model files in a plugin's models/ directory.

    Args:
        plugin_path: Path to the plugin directory.

    Returns:
        Sorted list of .py file paths.
        Empty list if models/ doesn't exist.
    """
    models_path = plugin_path / "models"
    if not models_path.exists():
        return []
    return sorted(models_path.glob("*.py"))


def extract_models_from_module(plugin_name: str, model_file: Path) -> list[type[CustomModel]]:
    """Sandbox-exec a model file and return discovered CustomModel subclasses.

    Combines security validation and model extraction in a single execution.
    Cross-file imports (e.g. ``booking.py`` importing from ``room.py``) are
    handled by the sandbox's ``_evaluate_module``, which re-evaluates and
    registers the dependency in ``sys.modules`` on demand — so this function
    does not need to register anything itself.

    Args:
        plugin_name: Name of the plugin (used for module namespace).
        model_file: Path to a single .py model file.

    Returns:
        List of CustomModel subclasses whose __module__ starts with
        '{plugin_name}.models'.
    """
    module_name = (
        f"{plugin_name}.models"
        if model_file.name == "__init__.py"
        else f"{plugin_name}.models.{model_file.stem}"
    )

    sandbox = Sandbox(model_file, namespace=module_name)
    sandbox.execute()

    return [
        value
        for value in sandbox.scope.values()
        if isinstance(value, type)
        and issubclass(value, CustomModel)
        and value is not CustomModel
        and value.__module__.startswith(f"{plugin_name}.models")
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
    return "." not in db_table or db_table.startswith(f"{schema_name}.")


def execute_create_table_sql(create_sql: str) -> None:
    """Execute CREATE TABLE SQL, handling SQLite vs PostgreSQL differences.

    SQLite requires executing one statement at a time; PostgreSQL can handle
    multiple statements in a single call.

    Closes stale connections before executing so that long-running plugin
    installations don't fail on a connection that the server has already
    closed.

    Args:
        create_sql: The SQL string (possibly multi-statement) to execute.
    """
    from django.db import connection

    connection.close_if_unusable_or_obsolete()
    connection.ensure_connection()

    with connection.cursor() as cursor:
        if IS_SQLITE:
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

    Sandbox-execs each model file for security validation, extracts the
    resulting CustomModel subclasses, and generates CREATE TABLE SQL.

    Model registration with Django's app registry is suppressed during
    extraction — these classes exist only for DDL generation.  The runtime
    path (``_evaluate_module``) creates the canonical model classes.

    Args:
        plugin_name: Name of the plugin (used for module namespace).
        plugin_path: Path to the plugin directory.
        schema_name: The PostgreSQL schema where tables will be created.
                     Defaults to plugin_name.

    Returns:
        List of discovered model classes.
    """
    if schema_name is None:
        schema_name = plugin_name
    log.info(f"Generating migrations for plugin '{plugin_name}' in schema '{schema_name}'")
    discovered_models: list[type[CustomModel]] = []
    try:
        # Add the plugin's parent directory so that intra-plugin imports like
        # `from hello_custom_data.models import CustomPatient` can resolve.
        # The plugin directory itself is a Python package (has __init__.py),
        # so the *parent* must be on sys.path for the package to be importable.
        parent_dir = str(plugin_path.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        model_files = discover_model_files(plugin_path)

        # Suppress Django's model registration and lazy FK resolution.
        # The model classes created here are only needed for DDL
        # generation, which uses only model._meta.  FK fields with
        # direct class references have remote_field.model set during
        # ForeignKey.__init__, before any of this machinery runs.
        #
        # Without these two suppresions, ModelBase.__new__ and
        # ForeignKey.contribute_to_class would pollute apps.all_models,
        # apps._pending_operations, and apps.app_configs — requiring
        # fragile cleanup that risks destroying live state from a
        # prior installation.
        with suppress_model_registration():
            for model_file in model_files:
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
                        raise RuntimeError(
                            f"Model {model_class.__name__} (table '{db_table}') "
                            f"references a schema outside of '{schema_name}'. "
                            f"A plugin may only define tables within its own "
                            f"namespace."
                        )

    except Exception as e:
        log.exception(f"Failed to generate migrations for plugin '{plugin_name}'")
        raise e

    return discovered_models
