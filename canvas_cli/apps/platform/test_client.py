"""Tests for the Canvas Platform API client."""

from __future__ import annotations

import pytest
import requests
import requests_mock as requests_mock_module
from requests_mock.request import _RequestObjectProxy

from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.client import PlatformClient, PlatformError

PLATFORM = "https://platform.example"


def _last(mock: requests_mock_module.Mocker) -> _RequestObjectProxy:
    """The most recent request the mock answered."""
    request = mock.last_request
    assert request is not None
    return request


def _sign_in(n: int = 1) -> None:
    auth.save_tokens(
        PLATFORM,
        {"access_token": f"cnvs_ua_{n}", "refresh_token": f"cnvs_rt_{n}", "expires_in": 3600},
        make_default=True,
    )


def test_calls_carry_the_bearer_token(requests_mock: requests_mock_module.Mocker) -> None:
    """Every call sends the stored access token."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/me", json={"email": "dana@acme.example"})

    assert PlatformClient(PLATFORM).me() == {"email": "dana@acme.example"}
    assert _last(requests_mock).headers["Authorization"] == "Bearer cnvs_ua_1"


def test_a_401_refreshes_once_and_retries(requests_mock: requests_mock_module.Mocker) -> None:
    """A rejected access token is refreshed, the new pair is stored, and the call is retried."""
    _sign_in()
    requests_mock.get(
        f"{PLATFORM}/api/v1/me",
        [{"status_code": 401}, {"json": {"email": "dana@acme.example"}}],
    )
    requests_mock.post(
        f"{PLATFORM}/oauth/token",
        json={"access_token": "cnvs_ua_2", "refresh_token": "cnvs_rt_2", "expires_in": 3600},
    )

    assert PlatformClient(PLATFORM).me()["email"] == "dana@acme.example"
    assert _last(requests_mock).headers["Authorization"] == "Bearer cnvs_ua_2"
    stored = auth.stored_tokens(PLATFORM)
    assert stored is not None
    assert stored["refresh_token"] == "cnvs_rt_2"


def test_a_second_401_asks_for_a_login(requests_mock: requests_mock_module.Mocker) -> None:
    """A token refused even after a refresh points the person at `canvas login`."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/me", status_code=401)
    requests_mock.post(
        f"{PLATFORM}/oauth/token",
        json={"access_token": "cnvs_ua_2", "refresh_token": "cnvs_rt_2", "expires_in": 3600},
    )

    with pytest.raises(auth.PlatformAuthError, match="canvas login"):
        PlatformClient(PLATFORM).me()


def test_refusals_surface_the_server_sentence(requests_mock: requests_mock_module.Mocker) -> None:
    """A 4xx raises with the server's `error` sentence, its code and any field."""
    _sign_in()
    requests_mock.post(
        f"{PLATFORM}/api/v1/orgs/acme/plugins",
        status_code=409,
        json={"error": "Another publisher holds that name.", "code": "name_taken", "field": "name"},
    )

    with pytest.raises(PlatformError) as raised:
        PlatformClient(PLATFORM).register_plugin("acme", "acme__intake")
    assert raised.value.message == "Another publisher holds that name. (field: name)"
    assert raised.value.status == 409
    assert raised.value.code == "name_taken"


def test_a_refusal_without_json_still_names_the_status(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """An HTML error page becomes a sentence carrying the status."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/me", status_code=502, text="<html>bad gateway</html>")

    with pytest.raises(PlatformError, match="502"):
        PlatformClient(PLATFORM).me()


def test_transport_failures_name_the_platform(requests_mock: requests_mock_module.Mocker) -> None:
    """A connection failure says which platform could not be reached."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/me", exc=requests.exceptions.ConnectionError("down"))

    with pytest.raises(PlatformError, match="Could not reach Canvas Platform at") as raised:
        PlatformClient(PLATFORM).me()
    assert raised.value.status is None


def test_plugin_answers_none_for_a_404(requests_mock: requests_mock_module.Mocker) -> None:
    """A plugin platform does not have, or the person may not see, reads as None."""
    _sign_in()
    requests_mock.get(
        f"{PLATFORM}/api/v1/plugins/acme__intake", status_code=404, json={"error": "x"}
    )

    assert PlatformClient(PLATFORM).plugin("acme__intake") is None


def test_set_variable_sends_sensitive_only_when_given(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """A declared key's sensitivity is left to the declaration; an undeclared one states it."""
    _sign_in()
    url = f"{PLATFORM}/api/v1/instances/acme-staging/plugins/acme__intake/variables/API_KEY"
    requests_mock.put(url, json={})
    client = PlatformClient(PLATFORM)

    client.set_variable("acme-staging", "acme__intake", "API_KEY", "v", None)
    assert _last(requests_mock).json() == {"value": "v"}

    client.set_variable("acme-staging", "acme__intake", "API_KEY", "v", True)
    assert _last(requests_mock).json() == {"value": "v", "sensitive": True}


def test_calls_without_a_session_ask_for_a_login(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """No stored tokens means no call at all."""
    with pytest.raises(auth.PlatformAuthError, match="canvas login"):
        PlatformClient(PLATFORM).me()
    assert not requests_mock.called


# -- a service account's token, as CI sets it ---------------------------------


def test_ci_calls_with_the_service_account_token(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``CANVAS_PLATFORM_TOKEN`` is the bearer token, with no sign-in stored."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(f"{PLATFORM}/api/v1/me", json={"email": "github-actions"})

    assert PlatformClient(PLATFORM).me() == {"email": "github-actions"}
    assert _last(requests_mock).headers["Authorization"] == "Bearer cnvs_sa_ci"


def test_the_service_account_token_wins_over_a_stored_sign_in(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A runner that once ran ``canvas login`` still acts as its service account."""
    _sign_in()
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(f"{PLATFORM}/api/v1/me", json={})

    PlatformClient(PLATFORM).me()
    assert _last(requests_mock).headers["Authorization"] == "Bearer cnvs_sa_ci"


def test_a_refused_service_account_token_says_so_and_never_refreshes(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """There is no refresh token to spend; the token was rotated or revoked."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(f"{PLATFORM}/api/v1/me", status_code=401)
    refresh = requests_mock.post(f"{PLATFORM}/oauth/token", json={})

    with pytest.raises(auth.PlatformAuthError, match="CANVAS_PLATFORM_TOKEN"):
        PlatformClient(PLATFORM).me()
    assert not refresh.called


def test_with_a_service_account_token_the_cli_counts_as_signed_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Commands that ask whether there is a session see one, so CI takes the platform path."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")

    assert auth.stored_tokens(PLATFORM) is not None
    assert auth.valid_tokens(PLATFORM)["access_token"] == "cnvs_sa_ci"


def test_a_refusal_whose_json_is_not_an_object_still_names_the_status(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """A JSON body that is not an object carries no sentence, so the status is named."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/me", status_code=400, json=["unexpected"])

    with pytest.raises(PlatformError, match="Canvas Platform answered 400."):
        PlatformClient(PLATFORM).me()


def test_plugin_raises_for_errors_other_than_a_404(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """Only a 404 reads as "no such plugin"; a server error is raised."""
    _sign_in()
    requests_mock.get(f"{PLATFORM}/api/v1/plugins/acme__intake", status_code=500, json={})

    with pytest.raises(PlatformError) as raised:
        PlatformClient(PLATFORM).plugin("acme__intake")
    assert raised.value.status == 500
