from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import django.db
import typer
from django.core.management import call_command

import settings
from plugin_runner.plugin_runner import main as run_server


@contextmanager
def _patch_default_db_connection() -> Generator[None, None, None]:
    """
    Temporarily patch the 'default' Django DB connection to allow db writes.
    """
    original_default = django.db.connections["default"]
    try:
        temp_handler = django.db.utils.ConnectionHandler(
            {"default": settings.SQLITE_WRITE_MODE_DATABASE}
        )
        django.db.connections["default"] = temp_handler["default"]
        yield
    finally:
        django.db.connections["default"] = original_default


def _run_db_seed_file(path: Path) -> None:
    """Run the database setup file to initialize the database."""
    code = path.read_text()
    exec_globals = {"__name__": "__main__"}
    exec(code, exec_globals)


def _reset_db(seed_file: Path | None = None) -> None:
    """Reset the database."""
    settings.SQLITE_DB_PATH.unlink(missing_ok=True)

    with _patch_default_db_connection():
        call_command("migrate", run_syncdb=True, verbosity=0)
        if seed_file:
            _run_db_seed_file(seed_file)


def run_plugin(
    plugin_directory: str = typer.Argument(..., help="Path to the plugin directory to run."),
    db_seed_file: Path | None = typer.Option(
        help="Path to the database seed file to use.",
        default=None,
    ),
    reset_db: bool = typer.Option(
        help="Reset the database before running the plugin.", default=False
    ),
) -> None:
    """
    Run the specified plugin for local development.
    """
    _run_plugins([plugin_directory], db_seed_file=db_seed_file, reset_db=reset_db)


def run_plugins(
    plugin_directories: list[str],
    db_seed_file: Path | None = typer.Option(
        help="Path to the database seed file to use.",
        default=None,
    ),
    reset_db: bool = typer.Option(
        help="Reset the database before running the plugin(s).", default=False
    ),
) -> None:
    """
    Run the specified plugins for local development.
    """
    _run_plugins(plugin_directories, db_seed_file=db_seed_file, reset_db=reset_db)


def _run_plugins(
    plugin_directories: list[str], db_seed_file: Path | None = None, reset_db: bool = False
) -> None:
    """
    Run the specified plugins for local development.
    """
    if db_seed_file:
        if not db_seed_file.exists():
            raise typer.BadParameter(f"Database setup file not found: {db_seed_file.resolve()}")
        if not db_seed_file.is_file():
            raise typer.BadParameter(
                f"Database setup file is not a regular file: {db_seed_file.resolve()}"
            )
        if not db_seed_file.suffix == ".py":
            raise typer.BadParameter("Database setup file must be a Python script (.py)")

    if settings.CANVAS_SDK_DB_BACKEND != "sqlite3":
        raise typer.BadParameter(
            "Database backend must be 'sqlite3' for local plugin development. Please unset 'DATABASE_URL' env var."
        )

    if db_seed_file or reset_db:
        _reset_db(seed_file=db_seed_file)

    run_server(plugin_directories)
