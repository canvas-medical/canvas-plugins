from unittest.mock import Mock, patch

import pytest
import requests
import typer

from canvas_cli.apps.namespace.namespace import (
    _confirm_destructive_action,
    drop,
    inspect,
    list_namespaces,
    namespace_url,
    reset,
)

# --- URL helper tests ---


def test_namespace_url_base() -> None:
    """Test URL generation for the namespace list endpoint."""
    result = namespace_url("http://localhost:8000")
    assert result == "http://localhost:8000/plugin-io/namespaces/"


def test_namespace_url_with_name() -> None:
    """Test URL generation for a specific namespace."""
    result = namespace_url("http://localhost:8000", "acme__clinical")
    assert result == "http://localhost:8000/plugin-io/namespaces/acme__clinical/"


def test_namespace_url_with_action() -> None:
    """Test URL generation for a namespace action."""
    result = namespace_url("http://localhost:8000", "acme__clinical", "reset")
    assert result == "http://localhost:8000/plugin-io/namespaces/acme__clinical/reset/"


# --- list_namespaces tests ---


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.get")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_list_namespaces_success(
    mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test successful namespace listing."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {
        "namespaces": [
            {"name": "acme__clinical", "table_count": 5, "custom_table_count": 2},
            {"name": "acme__billing", "table_count": 3, "custom_table_count": 0},
        ]
    }
    mock_requests_get.return_value = mock_response

    list_namespaces(host=host)

    mock_get_token.assert_called_once_with(host)
    assert mock_print.call_count == 2
    mock_print.assert_any_call("acme__clinical\ttables: 5\tcustom: 2")
    mock_print.assert_any_call("acme__billing\ttables: 3\tcustom: 0")


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.get")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_list_namespaces_empty(
    mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test listing when no namespaces exist."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {"namespaces": []}
    mock_requests_get.return_value = mock_response

    list_namespaces(host=host)

    mock_print.assert_called_once_with("No custom data namespaces found.")


@patch("requests.get")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_list_namespaces_connection_error(mock_get_token: Mock, mock_requests_get: Mock) -> None:
    """Test listing when connection fails."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"
    mock_requests_get.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(typer.Exit):
        list_namespaces(host=host)


# --- inspect tests ---


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.get")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_inspect_success(mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock) -> None:
    """Test successful namespace inspection."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {
        "namespace": "acme__clinical",
        "system_tables": [{"name": "namespace_auth", "approx_rows": 2}],
        "custom_tables": [
            {
                "name": "customnote",
                "approx_rows": 150,
                "columns": [
                    {"name": "dbid", "type": "bigint", "nullable": False},
                    {"name": "title", "type": "text", "nullable": False},
                ],
            }
        ],
    }
    mock_requests_get.return_value = mock_response

    inspect(namespace="acme__clinical", host=host)

    mock_get_token.assert_called_once_with(host)
    mock_print.assert_any_call("\nNamespace: acme__clinical")
    mock_print.assert_any_call("\nSystem tables:")
    mock_print.assert_any_call("  namespace_auth\t~2 rows")
    mock_print.assert_any_call("\nCustom tables:")
    mock_print.assert_any_call("  customnote\t~150 rows")
    mock_print.assert_any_call("    dbid\tbigint\tnot null")
    mock_print.assert_any_call("    title\ttext\tnot null")


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.get")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_inspect_not_found(mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock) -> None:
    """Test inspect when namespace doesn't exist."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(typer.Exit):
        inspect(namespace="nonexistent__ns", host=host)

    mock_print.assert_called_with("Namespace 'nonexistent__ns' does not exist.")


# --- reset tests ---


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.post")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_reset_dry_run(mock_get_token: Mock, mock_requests_post: Mock, mock_print: Mock) -> None:
    """Test reset in dry-run mode (no --execute)."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {
        "dry_run": True,
        "namespace": "acme__clinical",
        "tables_to_drop": [{"name": "customnote", "approx_rows": 150}],
        "tables_to_truncate": [{"name": "custom_attribute", "approx_rows": 500}],
    }
    mock_requests_post.return_value = mock_response

    reset(namespace="acme__clinical", execute=False, host=host)

    mock_requests_post.assert_called_once()
    # Verify dry_run=true was sent
    call_kwargs = mock_requests_post.call_args
    assert call_kwargs.kwargs["params"] == {"dry_run": "true"}

    mock_print.assert_any_call("\nThis is a dry run. To execute, re-run with --execute")


@patch("canvas_cli.apps.namespace.namespace._confirm_destructive_action")
@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.post")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_reset_execute(
    mock_get_token: Mock,
    mock_requests_post: Mock,
    mock_print: Mock,
    mock_confirm: Mock,
) -> None:
    """Test reset with --execute flag."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    # First call: dry run preview; second call: actual execute
    dry_run_response = Mock()
    dry_run_response.status_code = requests.codes.ok
    dry_run_response.json.return_value = {
        "dry_run": True,
        "namespace": "acme__clinical",
        "tables_to_drop": [{"name": "customnote", "approx_rows": 150}],
        "tables_to_truncate": [{"name": "custom_attribute", "approx_rows": 500}],
    }

    execute_response = Mock()
    execute_response.status_code = requests.codes.ok
    execute_response.json.return_value = {
        "dry_run": False,
        "namespace": "acme__clinical",
        "tables_dropped": ["customnote"],
        "tables_truncated": ["custom_attribute"],
    }

    mock_requests_post.side_effect = [dry_run_response, execute_response]

    reset(namespace="acme__clinical", execute=True, host=host)

    assert mock_requests_post.call_count == 2
    mock_confirm.assert_called_once_with("acme__clinical", "reset")
    mock_print.assert_any_call("\nNamespace 'acme__clinical' has been reset.")


# --- drop tests ---


@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.post")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_drop_dry_run(mock_get_token: Mock, mock_requests_post: Mock, mock_print: Mock) -> None:
    """Test drop in dry-run mode (no --execute)."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {
        "dry_run": True,
        "namespace": "acme__clinical",
        "tables": [
            {"name": "customnote", "approx_rows": 150},
            {"name": "namespace_auth", "approx_rows": 2},
        ],
    }
    mock_requests_post.return_value = mock_response

    drop(namespace="acme__clinical", execute=False, host=host)

    call_kwargs = mock_requests_post.call_args
    assert call_kwargs.kwargs["params"] == {"dry_run": "true"}

    mock_print.assert_any_call("\nThis is a dry run. To execute, re-run with --execute")


@patch("canvas_cli.apps.namespace.namespace._confirm_destructive_action")
@patch("canvas_cli.apps.namespace.namespace.print")
@patch("requests.post")
@patch("canvas_cli.apps.namespace.namespace.get_or_request_api_token")
def test_drop_execute(
    mock_get_token: Mock,
    mock_requests_post: Mock,
    mock_print: Mock,
    mock_confirm: Mock,
) -> None:
    """Test drop with --execute flag."""
    host = "http://localhost:8000"
    mock_get_token.return_value = "test-token"

    dry_run_response = Mock()
    dry_run_response.status_code = requests.codes.ok
    dry_run_response.json.return_value = {
        "dry_run": True,
        "namespace": "acme__clinical",
        "tables": [{"name": "customnote", "approx_rows": 150}],
    }

    execute_response = Mock()
    execute_response.status_code = requests.codes.ok
    execute_response.json.return_value = {
        "dry_run": False,
        "namespace": "acme__clinical",
        "dropped": True,
    }

    mock_requests_post.side_effect = [dry_run_response, execute_response]

    drop(namespace="acme__clinical", execute=True, host=host)

    assert mock_requests_post.call_count == 2
    mock_confirm.assert_called_once_with("acme__clinical", "permanently drop")
    mock_print.assert_any_call("\nNamespace 'acme__clinical' has been dropped.")


# --- _confirm_destructive_action tests ---


@patch("builtins.input", return_value="acme__clinical")
@patch("canvas_cli.apps.namespace.namespace.print")
def test_confirm_destructive_action_success(mock_print: Mock, mock_input: Mock) -> None:
    """Test that confirmation succeeds when the user types the correct name."""
    # Should not raise
    _confirm_destructive_action("acme__clinical", "reset")
    mock_input.assert_called_once()


@patch("builtins.input", return_value="wrong_name")
@patch("canvas_cli.apps.namespace.namespace.print")
def test_confirm_destructive_action_mismatch(mock_print: Mock, mock_input: Mock) -> None:
    """Test that confirmation fails when the user types the wrong name."""
    with pytest.raises(typer.Exit):
        _confirm_destructive_action("acme__clinical", "reset")

    mock_print.assert_any_call("Confirmation did not match. Aborting.")


# --- no host tests ---


def test_list_namespaces_no_host() -> None:
    """Test that list_namespaces raises BadParameter when no host is provided."""
    with pytest.raises(typer.BadParameter):
        list_namespaces(host=None)


def test_inspect_no_host() -> None:
    """Test that inspect raises BadParameter when no host is provided."""
    with pytest.raises(typer.BadParameter):
        inspect(namespace="acme__clinical", host=None)


def test_reset_no_host() -> None:
    """Test that reset raises BadParameter when no host is provided."""
    with pytest.raises(typer.BadParameter):
        reset(namespace="acme__clinical", execute=False, host=None)


def test_drop_no_host() -> None:
    """Test that drop raises BadParameter when no host is provided."""
    with pytest.raises(typer.BadParameter):
        drop(namespace="acme__clinical", execute=False, host=None)
