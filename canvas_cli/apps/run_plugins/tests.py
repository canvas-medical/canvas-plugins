from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from canvas_cli.apps.run_plugins.run_plugins import (
    _patch_default_db_connection,
    _reset_db,
    _run_plugins,
)


@patch("django.db.connections")
@patch("django.db.utils.ConnectionHandler")
def test_patches_connection_successfully(mock_handler_class: Mock, mock_connections: Mock) -> None:
    """Test that the context manager patches the connection correctly."""
    original_connection = MagicMock()
    mock_connections.__getitem__.return_value = original_connection
    mock_temp_handler = MagicMock()
    mock_new_connection = MagicMock()
    mock_temp_handler.__getitem__.return_value = mock_new_connection
    mock_handler_class.return_value = mock_temp_handler

    with _patch_default_db_connection():
        assert mock_connections.__setitem__.called

    mock_connections.__setitem__.assert_called_with("default", original_connection)


@patch("django.db.connections")
@patch("django.db.utils.ConnectionHandler")
def test_restores_connection_on_exception(mock_handler_class: Mock, mock_connections: Mock) -> None:
    """Test that the original connection is restored even if an exception occurs."""
    original_connection = MagicMock()
    mock_connections.__getitem__.return_value = original_connection

    mock_new_connection = MagicMock()
    mock_temp_handler = MagicMock()
    mock_temp_handler.__getitem__.return_value = mock_new_connection
    mock_handler_class.return_value = mock_temp_handler

    with pytest.raises(ValueError), _patch_default_db_connection():
        raise ValueError("Test exception")

    mock_connections.__setitem__.assert_called_with("default", original_connection)


@patch("canvas_cli.apps.run_plugins.run_plugins._run_db_seed_file")
@patch("canvas_cli.apps.run_plugins.run_plugins.call_command")
@patch("canvas_cli.apps.run_plugins.run_plugins._patch_default_db_connection")
@patch("canvas_cli.apps.run_plugins.run_plugins.settings")
def test_resets_database_without_seed_file(
    mock_settings: Mock, mock_patch_db: Mock, mock_call_command: Mock, mock_run_db_setup: Mock
) -> None:
    """Test that _reset_db resets the database without a seed file."""
    mock_db_path = Mock()
    mock_settings.SQLITE_DB_PATH = mock_db_path

    _reset_db()

    mock_db_path.unlink.assert_called_once_with(missing_ok=True)
    mock_patch_db.assert_called_once()
    mock_call_command.assert_called_once_with("migrate", run_syncdb=True, verbosity=0)
    mock_run_db_setup.assert_not_called()


@patch("canvas_cli.apps.run_plugins.run_plugins._run_db_seed_file")
@patch("canvas_cli.apps.run_plugins.run_plugins.call_command")
@patch("canvas_cli.apps.run_plugins.run_plugins._patch_default_db_connection")
@patch("canvas_cli.apps.run_plugins.run_plugins.settings")
def test_resets_database_with_seed_file(
    mock_settings: Mock, mock_patch_db: Mock, mock_call_command: Mock, mock_run_db_setup: Mock
) -> None:
    """Test that _reset_db resets the database and runs seed file."""
    mock_db_path = Mock()
    mock_settings.SQLITE_DB_PATH = mock_db_path
    seed_file = Mock(spec=Path)

    _reset_db(seed_file=seed_file)

    mock_db_path.unlink.assert_called_once_with(missing_ok=True)
    mock_patch_db.assert_called_once()
    mock_call_command.assert_called_once_with("migrate", run_syncdb=True, verbosity=0)
    mock_run_db_setup.assert_called_once_with(seed_file)


@pytest.mark.parametrize(
    "file,exists,is_file,expected_message",
    [
        (Path("/path/to/nonexistent.py"), False, True, "Database setup file not found"),
        (Path("/path/to/directory"), True, False, "Database setup file is not a regular file"),
        (Path("/path/to/setup.txt"), True, True, "Database setup file must be a Python script"),
    ],
    ids=("non-existent", "dir", "non-python-file"),
)
def test_raises_error_db_seed_file(
    cli_runner: CliRunner, file: Path, exists: bool, is_file: bool, expected_message: str
) -> None:
    """Test that error is raised for database setup file."""
    db_seed_file = MagicMock(spec=Path)
    db_seed_file.exists.return_value = exists
    db_seed_file.is_file.return_value = is_file
    db_seed_file.suffix.return_value = file.suffix
    db_seed_file.resolve.return_value = file

    with pytest.raises(typer.BadParameter, match=expected_message):
        _run_plugins(["some_dir"], db_seed_file=db_seed_file)


@patch("canvas_cli.apps.run_plugins.run_plugins.settings")
def test_raises_error_on_db_backend_not_supported(mock_settings: Mock) -> None:
    """Test that an error is raised when an unsupported database backend is specified."""
    mock_settings.CANVAS_SDK_DB_BACKEND = "postgres"

    with pytest.raises(typer.BadParameter, match="Database backend must be 'sqlite3'"):
        _run_plugins(["some_dir"], db_seed_file=None, reset_db=False)
