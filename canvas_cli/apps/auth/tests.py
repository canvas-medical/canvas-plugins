from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from canvas_cli.apps.auth.auth import validate_host
from canvas_cli.main import app
from canvas_cli.utils.context import context

runner = CliRunner()


def test_validate_host_invalid() -> None:
    """Test invalid host validation."""
    # Might as well just do a bunch of asserts in the same testcase due to the brevity of the asserts
    with pytest.raises(typer.BadParameter):
        validate_host("this won't validate")

    with pytest.raises(typer.BadParameter):
        validate_host("localhost.com")

    with pytest.raises(typer.BadParameter):
        validate_host("just-domain-name.com")

    with pytest.raises(typer.BadParameter):
        validate_host("just-domain-name.com:1234")

    with pytest.raises(typer.BadParameter):
        validate_host("just-domain-name.com/a-path")


def test_validate_host_special_case_localhost() -> None:
    """Test localhost host validation."""
    assert validate_host("localhost") == "http://localhost"


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_validate_host_valid(scheme: str) -> None:
    """Test valid host validation."""
    # Might as well just do a bunch of asserts in the same testcase due to the brevity of the asserts
    assert validate_host(f"{scheme}://localhost") == f"{scheme}://localhost"
    assert validate_host(f"{scheme}://localhost/") == f"{scheme}://localhost"
    assert validate_host(f"{scheme}://localhost/something-or-other") == f"{scheme}://localhost"
    assert validate_host(f"{scheme}://a-domain-name.com") == f"{scheme}://a-domain-name.com"
    assert validate_host(f"{scheme}://a-domain-name.com/a-path") == f"{scheme}://a-domain-name.com"
    assert (
        validate_host(f"{scheme}://a-domain-name.com:1234") == f"{scheme}://a-domain-name.com:1234"
    )


@patch("keyring.get_password")
@patch("keyring.set_password")
def test_add_api_client_credentials_new_host(
    mock_set_password: MagicMock, mock_get_password: MagicMock
) -> None:
    """Test a new password is set if the host doesn't already exist and ensure it isn't written to the config."""
    mock_get_password.return_value = None
    runner.invoke(
        app,
        "auth add-api-client-credentials --host localhost --client-id mock-client-id --client-secret mock-client-secret --no-is-default",
    )
    mock_set_password.assert_called()
    assert context.default_host is None


@patch("keyring.get_password")
@patch("keyring.set_password")
def test_add_api_client_credentials_new_host_set_default(
    mock_set_password: MagicMock, mock_get_password: MagicMock
) -> None:
    """Test a new password is set if the host doesn't already exist and ensure it is written to the config."""
    mock_get_password.return_value = None
    runner.invoke(
        app,
        "auth add-api-client-credentials --host localhost --client-id mock-client-id --client-secret mock-client-secret --is-default",
    )
    mock_set_password.assert_called()
    assert context.default_host == "http://localhost"


@patch("keyring.get_password")
@patch("keyring.set_password")
def test_add_api_client_credentials_existing_host_overwrite(
    mock_set_password: MagicMock, mock_get_password: MagicMock
) -> None:
    """Test a new password is set if the host exists, but we want to override."""
    mock_get_password.return_value = "http://a-domain-name.com"
    result = runner.invoke(
        app,
        "auth add-api-client-credentials --host http://a-domain-name.com --client-id mock-client-id --client-secret mock-client-secret --no-is-default",
        input="y\n",
    )
    mock_set_password.assert_called()
    assert result.exit_code == 0


@patch("keyring.get_password")
@patch("keyring.set_password")
def test_add_api_key_existing_host_abort(
    mock_set_password: MagicMock, mock_get_password: MagicMock
) -> None:
    """Test a new password is NOT set if the host already exists and we DO NOT override."""
    mock_get_password.return_value = "http://a-domain-name.com"

    result = runner.invoke(
        app,
        "auth add-api-client-credentials --host http://a-domain-name.com --client-id mock-client-id --client-secret mock-client-secret --no-is-default",
        input="n\n",
    )

    mock_set_password.assert_not_called()
    assert result.exit_code == 1


@patch("keyring.get_password")
@patch("keyring.set_password")
@patch("keyring.delete_password")
def test_remove_api_client_credentials(
    mock_delete_password: MagicMock,
    mock_set_password: MagicMock,
    mock_get_password: MagicMock,
) -> None:
    """Test removing an api-key deletes it from the config file."""
    # First we need to add an api-key to the config file
    # The following command is tested, so we're not asserting the result
    runner.invoke(
        app,
        "auth add-api-client-credentials --host localhost --client-id mock-client-id --client-secret mock-client-secret --is-default",
    )

    # Then we remove the same host, which should delete the entry from the config file
    result = runner.invoke(app, "auth remove-api-client-credentials localhost")

    assert context.default_host is None
    mock_delete_password.assert_called()
    assert result.exit_code == 0


@patch("keyring.get_password")
def test_set_default_host_existing_host(mock_get_password: MagicMock) -> None:
    """Test saving a host to the config."""
    mock_get_password.return_value = "a-valid-api-key"
    result = runner.invoke(app, "auth set-default-host localhost")

    assert result.exit_code == 0
    assert context.default_host == "http://localhost"


@patch("keyring.get_password")
def test_set_default_host(mock_get_password: MagicMock) -> None:
    """Test trying to save a non-existing host to the config."""
    mock_get_password.return_value = None

    result = runner.invoke(app, "auth set-default-host localhost")
    assert context.default_host is None
    assert result.exit_code == 1


def test_get_api_token_without_existing_host_or_client_credentials_raises_exception() -> None:
    """Test getting an api token with no default host or client credentials."""

    runner.invoke(app, "auth remove-api-client-credentials http://george.com")

    result_without_host = runner.invoke(app, "auth get-api-token")
    assert result_without_host.exit_code == 2
    assert (
        "Invalid value: Please specify a host or set a default via the `auth` command"
        in result_without_host.stdout
    )

    result_without_client_id = runner.invoke(app, "auth get-api-token --host http://george.com")
    assert result_without_client_id.exit_code == 2
    print(result_without_client_id.stdout)
    assert (
        "Invalid value: Please specify a client_id and client_secret or add them via"
        in result_without_client_id.stdout
    )

    result_without_client_secret = runner.invoke(
        app, "auth get-api-token --host http://george.com --client-id mock-client-id"
    )
    assert result_without_client_secret.exit_code == 2
    assert (
        "Invalid value: Please specify a client_id and client_secret or add them via"
        in result_without_client_secret.stdout
    )


# @patch("requests.post")
# def test_get_api_token_requests_token_from_the_host_if_not_stored_in_context(
#     mock_post: MagicMock,
# ) -> None:
#     class FakeResponse:
#         status_code = 200

#         def json(self) -> dict:
#             return {"access_token": "a-valid-api-token", "expires_in": 3600}

#     mock_post.return_value = FakeResponse()

#     result = runner.invoke(
#         app,
#         "auth get-api-token --host http://george.com --client-id mock-client-id --client-secret mock-client-secret",
#     )
#     mock_post.assert_called_once()
#     assert result.exit_code == 0
#     assert '{"success": true, "token": "a-valid-api-token"}' in result.stdout
#     assert context.token_expiration_date is not None
#     assert datetime.fromisoformat(context.token_expiration_date) > datetime.now()


# @patch("keyring.get_password")
# @patch("requests.post")
# def test_get_api_token_uses_token_stored_in_context_first(
#     mock_post: MagicMock,
#     mock_get_password: MagicMock,
# ) -> None:
#     mock_get_password.return_value = "a-valid-api-token"
#     result = runner.invoke(
#         app,
#         "auth get-api-token --host http://george.com --client-id mock-client-id --client-secret mock-client-secret",
#     )
#     assert result.exit_code == 0
#     mock_get_password.assert_called_once_with(
#         "canvas_cli.apps.auth.utils", "http://george.com|token"
#     )
#     mock_post.assert_not_called()


# def test_get_api_token_uses_credentials_stored_in_context() -> None:
#     runner.invoke(
#         app,
#         "auth add-api-client-credentials --host http://george.com --client-id mock-client-id --client-secret mock-client-secret --is-default",
#     )
#     assert context.default_host == "http://george.com"

#     result = runner.invoke(app, "auth get-api-token")
#     assert result.exit_code == 0
#     assert '{"success": true, "token": "a-valid-api-token"}' in result.stdout
