import json
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from io import StringIO
from typing import Any
from unittest.mock import Mock, patch

import pytest
import typer
import websocket
from typer.testing import CliRunner

from canvas_cli.apps.logs.logs import (
    _format_line,
    _on_close,
    _on_error,
    _on_message,
    _on_open,
    _parse_duration,
    _parse_when,
    iter_history,
    make_resume_token,
    parse_resume_token,
    search_logs,
)
from canvas_cli.main import app


@pytest.fixture(scope="module", autouse=True)
def mock_host() -> Generator[None]:
    """Fixture for mocking get_default_host."""
    with patch("canvas_cli.apps.logs.logs.get_default_host") as mock_host:
        mock_host.return_value = "example.canvas.com"
        yield


@pytest.fixture(scope="module", autouse=True)
def mock_token() -> Generator[None]:
    """Fixture for mocking get_or_request_api_token."""
    with patch("canvas_cli.apps.logs.logs.get_or_request_api_token") as mock_api_token:
        mock_api_token.return_value = "test-api-token-12345"
        yield mock_api_token.return_value


@pytest.fixture
def sample_log_hit() -> dict[str, Any]:
    """Fixture providing a sample log hit structure."""
    return {
        "ts": "2024-01-15T10:30:00Z",
        "message": "Test log message",
        "log": {"level": "INFO"},
        "service": {"name": "plugin_runner"},
        "error": {},
    }


@pytest.fixture
def sample_search_response() -> dict[str, Any]:
    """Fixture providing a sample search API response."""
    return {
        "hits": [
            {
                "ts": "2024-01-15T10:30:00Z",
                "message": "Log entry 1",
                "log": {"level": "INFO"},
                "service": {"name": "plugin_runner"},
            },
            {
                "ts": "2024-01-15T10:31:00Z",
                "message": "Log entry 2",
                "log": {"level": "ERROR"},
                "service": {"name": "plugin_runner"},
            },
        ],
        "next": {"search_after": ["cursor-123", 456]},
    }


def test_format_line_basic(sample_log_hit: dict[str, Any]) -> None:
    """Test basic formatting of log lines."""
    result = _format_line(sample_log_hit)

    assert "plugin_runner" in result
    assert "INFO" in result
    assert "2024-01-15T10:30:00Z" in result
    assert "Test log message" in result


def test_format_line_with_prefix(sample_log_hit: dict[str, Any]) -> None:
    """Test formatting of log lines with a prefix."""
    result = _format_line(sample_log_hit, log_prefix="[PREFIX] ")

    assert "[PREFIX] " in result
    assert "INFO" in result
    assert "Test log message" in result


def test_format_line_with_error() -> None:
    """Test formatting of log lines containing error information."""
    hit_with_error = {
        "ts": "2024-01-15T10:30:00Z",
        "message": "Error occurred",
        "log": {"level": "ERROR"},
        "service": {"name": "api"},
        "error": {"type": "ValueError", "message": "Invalid input"},
    }

    result = _format_line(hit_with_error)

    assert "ERROR" in result
    assert "Error occurred" in result
    assert "ValueError" in result
    assert "Invalid input" in result


def test_format_line_with_stack_trace() -> None:
    """Test formatting of plugin-runner logs with stack traces."""
    hit_with_stack = {
        "ts": "2024-01-15T10:30:00Z",
        "message": "Plugin error",
        "log": {"level": "ERROR"},
        "service": {"name": "plugin-runner"},
        "error": {"stack_trace": ["Traceback:\n", "  File test.py\n", "    raise Error\n"]},
    }

    result = _format_line(hit_with_stack)

    assert "Plugin error" in result
    assert "Traceback:" in result
    assert "File test.py" in result


@pytest.mark.parametrize(
    "input",
    [
        ("15m", timedelta(minutes=15)),
        ("2h", timedelta(hours=2)),
        ("1d", timedelta(days=1)),
        ("45s", timedelta(seconds=45)),
        ("1d2h30m", timedelta(days=1, hours=2, minutes=30)),
        ("1h30m", timedelta(hours=1, minutes=30)),
        ("90s", timedelta(seconds=90)),
    ],
    ids=(
        "15m",
        "2h",
        "1d",
        "45s",
        "1d2h30m",
        "1h30m",
        "90s",
    ),
)
def test_parse_duration_valid_inputs(input: tuple) -> None:
    """Test parsing of various valid duration strings."""
    input_str, expected = input
    assert _parse_duration(input_str) == expected


def test_parse_duration_invalid_input() -> None:
    """Test that invalid duration strings raise BadParameter."""
    with pytest.raises(typer.BadParameter, match="Use durations like"):
        _parse_duration("invalid")

    with pytest.raises(typer.BadParameter):
        _parse_duration("2x")

    with pytest.raises(typer.BadParameter):
        _parse_duration("abc123")


def test_parse_when_now() -> None:
    """Test parsing 'now' as current UTC time."""
    with patch("canvas_cli.apps.logs.logs.datetime") as mock_datetime:
        mock_now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = _parse_when("now")

        assert result == mock_now


def test_parse_when_iso_format() -> None:
    """Test parsing ISO format datetime strings."""
    # With timezone
    result = _parse_when("2024-01-15T10:30:00+00:00")
    expected = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
    assert result == expected

    # With Z timezone
    result = _parse_when("2024-01-15T10:30:00Z")
    assert result == expected


def test_parse_when_invalid() -> None:
    """Test that invalid datetime strings raise BadParameter."""
    with pytest.raises(typer.BadParameter, match="Invalid datetime"):
        _parse_when("not-a-date")


def test_make_and_parse_resume_token() -> None:
    """Test creating and parsing resume tokens for pagination."""
    test_data = {
        "cursor": ["cursor-123", 456],
        "source": "plugin_runner",
        "levels": ["ERROR", "WARN"],
        "start": "2024-01-15T00:00:00Z",
        "end": "2024-01-15T23:59:59Z",
    }

    # Create token
    token = make_resume_token(**test_data)

    assert isinstance(token, str)
    assert len(token) > 0

    parsed = parse_resume_token(token)

    assert parsed == test_data
    assert parsed["cursor"] == ["cursor-123", 456]
    assert parsed["source"] == "plugin_runner"


@patch("canvas_cli.apps.logs.logs.requests.get")
def test_search_logs_basic(
    mock_get: Mock, sample_search_response: dict[str, Any], mock_token: str
) -> None:
    """Test basic search_logs functionality."""
    mock_response = Mock()
    mock_response.json.return_value = sample_search_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = search_logs(
        token=mock_token,
        host="",
        source="plugin_runner",
        levels=["INFO", "ERROR"],
        start_time="2024-01-15T00:00:00Z",
        end_time="2024-01-15T23:59:59Z",
        size=100,
        search_after=None,
    )

    assert result["hits"] == sample_search_response["hits"]
    assert result["next"] == sample_search_response["next"]

    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["headers"]["Authorization"] == f"Bearer {mock_token}"
    assert call_args.kwargs["params"]["size"] == 100
    assert call_args.kwargs["params"]["source"] == "plugin_runner"
    assert call_args.kwargs["params"]["level"] == ["INFO", "ERROR"]


@patch("canvas_cli.apps.logs.logs.search_logs")
def test_iter_history_single_page_default(
    mock_search: Mock, sample_search_response: dict[str, Any]
) -> None:
    """Test iter_history fetches single page by default."""
    mock_search.return_value = sample_search_response

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=200,
            limit=None,
            interactive=False,
            fetch_all=False,
        )
    )

    assert len(results) == 2
    assert results[0]["message"] == "Log entry 1"
    assert results[1]["message"] == "Log entry 2"

    mock_search.assert_called_once()


@patch("canvas_cli.apps.logs.logs.search_logs")
def test_iter_history_with_limit(
    mock_search: Mock,
) -> None:
    """Test iter_history respects limit parameter."""
    page1 = {
        "hits": [{"message": f"Log {i}"} for i in range(1, 6)],
        "next": {"search_after": ["cursor-1"]},
    }
    page2 = {
        "hits": [{"message": f"Log {i}"} for i in range(6, 11)],
        "next": {"search_after": ["cursor-2"]},
    }

    mock_search.side_effect = [page1, page2]

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=5,
            limit=7,
            interactive=False,
            fetch_all=False,
        )
    )

    assert len(results) == 7
    assert results[0]["message"] == "Log 1"
    assert results[6]["message"] == "Log 7"

    assert mock_search.call_count == 2


@patch("canvas_cli.apps.logs.logs.search_logs")
@patch("canvas_cli.apps.logs.logs._ask")
def test_iter_history_interactive_mode(
    mock_ask: Mock,
    mock_search: Mock,
) -> None:
    """Test iter_history with interactive mode prompting."""
    page1 = {"hits": [{"message": "Log 1"}], "next": {"search_after": ["cursor-1"]}}
    page2 = {"hits": [{"message": "Log 2"}], "next": {}}

    mock_search.side_effect = [page1, page2]
    mock_ask.side_effect = ["y", "n"]  # Yes to first prompt, no to second

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=1,
            limit=None,
            interactive=True,
            fetch_all=False,
        )
    )

    assert len(results) == 2
    mock_ask.assert_called_once()


@patch("canvas_cli.apps.logs.logs.search_logs")
def test_iter_history_fetch_all(
    mock_search: Mock,
) -> None:
    """Test iter_history with fetch_all=True retrieves all pages."""
    pages = [
        {"hits": [{"message": f"Log {i}"} for i in range(1, 4)], "next": {"search_after": ["c1"]}},
        {"hits": [{"message": f"Log {i}"} for i in range(4, 7)], "next": {"search_after": ["c2"]}},
        {"hits": [{"message": f"Log {i}"} for i in range(7, 9)], "next": {}},  # Last page
    ]

    mock_search.side_effect = pages

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=3,
            limit=None,
            interactive=False,
            fetch_all=True,
        )
    )

    assert len(results) == 8
    assert mock_search.call_count == 3


@patch("canvas_cli.apps.logs.logs.websocket.WebSocketApp")
@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_basic_streaming(
    mock_iter_history: Mock,
    mock_websocket: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test basic logs function with streaming (no --no-follow)."""
    mock_iter_history.return_value = iter([])

    mock_ws_instance = Mock()
    mock_websocket.return_value = mock_ws_instance

    mock_ws_instance.run_forever.side_effect = KeyboardInterrupt

    result = cli_runner.invoke(app, "logs --host localhost")
    assert result.exit_code == 0

    mock_websocket.assert_called_once()
    mock_ws_instance.run_forever.assert_called_once()


@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_with_since_filter(
    mock_iter_history: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test logs function with --since time filter."""
    mock_iter_history.return_value = iter(
        [{"message": "Historical log 1"}, {"message": "Historical log 2"}]
    )

    with patch("canvas_cli.apps.logs.logs.datetime") as mock_datetime:
        mock_now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = mock_now
        mock_datetime.return_value = datetime

        with patch("canvas_cli.apps.logs.logs._format_line") as mock_print:
            cli_runner.invoke(app, "logs --since 2h30m --no-follow --host localhost")

    call_args = mock_iter_history.call_args
    assert call_args.kwargs["start_time"] is not None
    assert call_args.kwargs["end_time"] is not None

    assert mock_print.call_count >= 2


def test_logs_with_start_end_filters(
    cli_runner: CliRunner,
) -> None:
    """Test logs function with --start and --end filters."""
    with patch("canvas_cli.apps.logs.logs.iter_history") as mock_iter:
        mock_iter.return_value = iter([])
        cli_runner.invoke(
            app, "logs --start 2024-01-15T10:00:00Z --end 2024-01-15T12:00:00Z --host localhost"
        )

        call_args = mock_iter.call_args
        assert "2024-01-15T10:00:00" in call_args.kwargs["start_time"]
        assert "2024-01-15T12:00:00" in call_args.kwargs["end_time"]


def test_logs_validation_errors(
    cli_runner: CliRunner,
) -> None:
    """Test logs function parameter validation."""
    result = cli_runner.invoke(app, "logs --since 2h --start 2024-01-15T10:00:00Z --host localhost")
    assert result.exit_code != 0
    assert "--since cannot be combined with --start" in result.output

    result = cli_runner.invoke(app, "logs --limit 100 --all --host localhost")
    assert result.exit_code != 0
    assert "--all cannot be combined with --limit" in result.output

    result = cli_runner.invoke(app, "logs --limit 0 --host localhost")
    assert result.exit_code != 0
    assert "must be a positive integer" in result.output

    result = cli_runner.invoke(
        app, "logs --start 2024-01-15T10:00:00Z --end 2024-01-15T09:00:00Z --host localhost"
    )
    assert result.exit_code != 0
    assert "End must be after start" in result.output


@patch("canvas_cli.apps.logs.logs.parse_resume_token")
@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_with_cursor_resume(
    mock_iter_history: Mock,
    mock_parse_token: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test logs function with --cursor for resuming pagination."""
    cursor_data = {
        "cursor": ["cursor-xyz", 999],
        "source": "plugin_runner",
        "levels": ["ERROR"],
        "start": "2024-01-15T00:00:00Z",
        "end": "2024-01-15T23:59:59Z",
    }
    mock_parse_token.return_value = cursor_data
    mock_iter_history.return_value = iter([])

    cli_runner.invoke(app, "logs --cursor encoded-cursor-token --no-follow --host localhost")

    # Verify cursor was parsed
    mock_parse_token.assert_called_once_with("encoded-cursor-token")

    # Verify iter_history was called with cursor data
    call_args = mock_iter_history.call_args
    assert call_args.kwargs["cursor"] == cursor_data["cursor"]
    assert call_args.kwargs["source"] == "plugin_runner"
    assert call_args.kwargs["levels"] == ["ERROR"]


@pytest.mark.parametrize(
    "cmd",
    (
        "logs --cursor some-cursor --since 2h --host localhost",
        "logs --cursor some-cursor --level ERROR --host localhost",
    ),
)
def test_logs_cursor_conflicts(
    cmd: str,
    cli_runner: CliRunner,
) -> None:
    """Test that --cursor cannot be combined with other filters."""
    result = cli_runner.invoke(app, cmd)
    assert result.exit_code != 0
    assert "--cursor cannot be combined with filters" in result.output


def test_websocket_message_handlers() -> None:
    """Test WebSocket event handler functions."""
    mock_ws = Mock(spec=websocket.WebSocket)

    with patch("builtins.print") as mock_print:
        message = json.dumps({"timestamp": "2024-01-15T10:30:00Z", "message": "Test log"})
        _on_message(mock_ws, message)
        mock_print.assert_called_once_with("2024-01-15T10:30:00Z | Test log")

    with patch("builtins.print") as mock_print:
        _on_message(mock_ws, "Plain text message")
        mock_print.assert_called_once_with("Plain text message")

    with patch("builtins.print") as mock_print:
        _on_error(mock_ws, "Connection failed")
        mock_print.assert_called_once_with("Error: Connection failed")

    with patch("builtins.print") as mock_print:
        _on_close(mock_ws, "1000", "Normal closure")
        mock_print.assert_called_once_with(
            "Connection closed with status code 1000: Normal closure"
        )

    # Test _on_open
    with patch("builtins.print") as mock_print:
        _on_open(mock_ws)
        mock_print.assert_called_once_with("Connected to the logging service")


@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_with_level_filters(
    mock_iter_history: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test logs function with --level filters."""
    mock_iter_history.return_value = iter([])

    result = cli_runner.invoke(app, "logs --level warn --level INFO --no-follow --host localhost")
    assert result.exit_code == 0

    call_args = mock_iter_history.call_args
    assert set(call_args.kwargs["levels"]) == {"WARN", "INFO"}


@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_with_source_filter(
    mock_iter_history: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test logs function with --source filter."""
    mock_iter_history.return_value = iter([])

    result = cli_runner.invoke(app, "logs --source plugin-runner --no-follow --host localhost")
    assert result.exit_code == 0

    call_args = mock_iter_history.call_args
    assert call_args.kwargs["source"] == "plugin-runner"


@patch("canvas_cli.apps.logs.logs.iter_history")
def test_logs_with_pagination_parameters(
    mock_iter_history: Mock,
    cli_runner: CliRunner,
) -> None:
    """Test logs function with pagination parameters."""
    mock_iter_history.return_value = iter([])

    result = cli_runner.invoke(
        app, "logs --since 2h --page-size 50 --limit 150 --no-follow --host localhost"
    )
    assert result.exit_code == 0

    call_args = mock_iter_history.call_args
    assert call_args.kwargs["page_size"] == 50
    assert call_args.kwargs["limit"] == 150
    assert call_args.kwargs["fetch_all"] is False
    assert call_args.kwargs["interactive"] is False


@patch("canvas_cli.apps.logs.logs.search_logs")
def test_iter_history_handles_empty_response(mock_search: Mock) -> None:
    """Test iter_history handles empty search responses gracefully."""
    # Return empty response
    mock_search.return_value = {"hits": [], "next": {}}

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=100,
            limit=None,
            interactive=False,
            fetch_all=False,
        )
    )

    assert results == []
    mock_search.assert_called_once()


@patch("sys.stdout", new_callable=StringIO)
@patch("builtins.input", return_value="yes")
def test_ask_function(mock_input: Mock, mock_stdout: StringIO) -> None:
    """Test the _ask function for user input."""
    from canvas_cli.apps.logs.logs import _ask

    result = _ask("Continue? [Y/n] ")

    assert result == "yes"
    mock_input.assert_called_once()

    # Test EOF handling
    mock_input.side_effect = EOFError
    result = _ask("Continue? ")
    assert result == "n"


@patch("canvas_cli.apps.logs.logs.search_logs")
@patch("canvas_cli.apps.logs.logs._ask")
def test_iter_history_interactive_eof(mock_ask: Mock, mock_search: Mock) -> None:
    """Test iter_history handles EOF in interactive mode."""
    page1 = {"hits": [{"message": "Log 1"}], "next": {"search_after": ["cursor-1"]}}

    mock_search.return_value = page1
    mock_ask.side_effect = EOFError  # Simulate Ctrl+D

    results = list(
        iter_history(
            token="",
            host="",
            source=None,
            levels=[],
            start_time=None,
            end_time=None,
            page_size=1,
            limit=None,
            interactive=True,
            fetch_all=False,
        )
    )

    # Should get first page but stop due to EOF
    mock_ask.assert_called_once()
    assert len(results) == 1


def test_parse_when_naive_datetime() -> None:
    """Test parsing naive datetime (assumes local timezone)."""
    naive_str = "2024-01-15T10:30:00"
    local_dt = datetime(2024, 1, 15, 10, 30).astimezone()

    expected = local_dt.astimezone(UTC)
    result = _parse_when(naive_str)

    assert result == expected
    assert result.tzinfo is UTC
