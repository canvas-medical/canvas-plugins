# def test_get_api_token_without_existing_host_or_client_credentials_raises_exception() -> None:
#     """Test getting an api token with no default host or client credentials."""

#     runner.invoke(app, "auth remove-api-client-credentials http://george.com")

#     result_without_host = runner.invoke(app, "auth get-api-token")
#     assert result_without_host.exit_code == 2
#     assert (
#         "Invalid value: Please specify a host or set a default via the `auth` command"
#         in result_without_host.stdout
#     )

#     result_without_client_id = runner.invoke(app, "auth get-api-token --host http://george.com")
#     assert result_without_client_id.exit_code == 2
#     print(result_without_client_id.stdout)
#     assert (
#         "Invalid value: Please specify a client_id and client_secret or add them via"
#         in result_without_client_id.stdout
#     )

#     result_without_client_secret = runner.invoke(
#         app, "auth get-api-token --host http://george.com --client-id mock-client-id"
#     )
#     assert result_without_client_secret.exit_code == 2
#     assert (
#         "Invalid value: Please specify a client_id and client_secret or add them via"
#         in result_without_client_secret.stdout
#     )


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
