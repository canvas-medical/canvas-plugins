"""Tests for `canvas logs` through a log token issued by Canvas Platform."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests_mock as requests_mock_module
from typer.testing import CliRunner

from canvas_cli.apps.auth.utils import instance_slug
from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.auth import PLATFORM_URL_ENV
from canvas_cli.apps.plugin.plugin import plugin_url
from canvas_cli.main import app

PLATFORM = "https://platform.example"
HOST = "https://acme-prod.canvasmedical.com"
LOGS_URL = plugin_url(HOST, "/logs")
LOG_TOKEN_URL = f"{PLATFORM}/api/v1/instances/acme-prod/log-token"
MINTED = {
    "access_token": "plat-tok",
    "token_type": "Bearer",
    "expires_in": 900,
    "scope": "system/Plugins.logs",
}
HIT = {
    "ts": "2024-01-15T10:30:00Z",
    "message": "hello from acme",
    "log": {"level": "INFO"},
    "service": {"name": "plugin-runner"},
}
FORBIDDEN = {"error": "That needs read_plugin_logs in Acme.", "code": "forbidden"}
INSTANCE_OUTDATED = {
    "error": (
        "acme-prod runs a Canvas release that cannot issue log tokens yet. "
        "Use the instance's credentials.ini entry until it updates."
    ),
    "code": "instance_outdated",
}


def _instance(slug: str, *capabilities: str, managed: bool = True) -> dict[str, Any]:
    return {
        "slug": slug,
        "organization": "acme",
        "stage": "staging",
        "production": False,
        "managed": managed,
        "capabilities": list(capabilities),
    }


def _calls_to(mock: requests_mock_module.Mocker, url: str) -> int:
    return len([r for r in mock.request_history if r.url.split("?")[0] == url])


@pytest.fixture(autouse=True)
def platform_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the CLI at the test platform."""
    monkeypatch.setenv(PLATFORM_URL_ENV, PLATFORM)


@pytest.fixture
def signed_in() -> None:
    """A stored session with the test platform."""
    auth.save_tokens(
        PLATFORM,
        {"access_token": "cnvs_ua_1", "refresh_token": "cnvs_rt_1", "expires_in": 3600},
        make_default=True,
    )


@pytest.fixture
def credentials_token() -> Iterator[Mock]:
    """The credentials.ini token lookup, answering with a distinct token."""
    with patch("canvas_cli.apps.logs.logs.get_or_request_api_token") as mock:
        mock.return_value = "ini-tok"
        yield mock


def _answer_logs_for(mock: requests_mock_module.Mocker, token: str) -> None:
    """Answer the instance's logs only when the bearer token is ``token``."""
    mock.get(
        LOGS_URL,
        request_headers={"Authorization": f"Bearer {token}"},
        json={"hits": [HIT], "next": {}},
    )


def test_logs_uses_platform_token_for_managed_instance(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A signed-in person reads a managed instance's logs with the minted token."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "plat-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    credentials_token.assert_not_called()


def test_platform_chosen_over_credentials_ini(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """With both a session and a credentials.ini entry, Platform issues the token."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "plat-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    credentials_token.assert_not_called()
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 1


def test_unmanaged_instance_uses_credentials_ini(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """D1 keeps credentials.ini for instances Platform does not manage."""
    requests_mock.get(
        f"{PLATFORM}/api/v1/instances",
        json={"instances": [_instance("acme-prod", managed=False)]},
    )
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "ini-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 0


def test_instance_not_in_platform_list_uses_credentials_ini(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """An instance outside the person's Platform list keeps the credentials.ini path."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": []})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "ini-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 0


def test_signed_out_uses_credentials_ini(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    credentials_token: Mock,
) -> None:
    """Without a Platform session the run never contacts Platform."""
    _answer_logs_for(requests_mock, "ini-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert not [r for r in requests_mock.request_history if r.url.startswith(PLATFORM)]


def test_localhost_uses_credentials_ini(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A local instance has no Platform slug, so Platform is never asked."""
    requests_mock.get(
        plugin_url("http://localhost:8000", "/logs"), json={"hits": [HIT], "next": {}}
    )

    result = cli_runner.invoke(app, "logs --host localhost --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert not [r for r in requests_mock.request_history if r.url.startswith(PLATFORM)]


@pytest.mark.parametrize("refusal", [FORBIDDEN, INSTANCE_OUTDATED], ids=lambda r: r["code"])
def test_platform_refusal_shown(
    refusal: dict[str, str],
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A refusal on a managed instance is shown, never silently replaced by credentials.ini."""
    status = 403 if refusal["code"] == "forbidden" else 409
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, status_code=status, json=refusal)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert refusal["error"] in result.output
    credentials_token.assert_not_called()
    assert _calls_to(requests_mock, LOGS_URL) == 0


def test_platform_instances_error_is_shown(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A failed lookup never means unmanaged: a signed-in person is not routed to credentials.ini."""
    requests_mock.get(
        f"{PLATFORM}/api/v1/instances",
        status_code=500,
        json={"error": "Platform is unavailable.", "code": "internal"},
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "Platform is unavailable." in result.output
    credentials_token.assert_not_called()
    assert _calls_to(requests_mock, LOGS_URL) == 0


def test_reissues_after_401(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """An instance 401 mints a fresh token and retries once."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(
        LOGS_URL,
        [{"status_code": 401}, {"json": {"hits": [HIT], "next": {}}}],
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_second_401_names_the_instance(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A freshly minted token the instance still refuses ends the run with a clear sentence."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(LOGS_URL, status_code=401)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "acme-prod refused the log token Canvas Platform issued." in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_reissues_after_expiry(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A token past its expiry is replaced before the next page is requested."""
    clock: list[float] = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    pages: list[dict[str, Any]] = [
        {"hits": [HIT], "next": {"search_after": [1]}},
        {"hits": [HIT], "next": {}},
    ]

    def answer(request: Any, context: Any) -> dict[str, Any]:
        clock[0] += 100
        return pages.pop(0)

    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json={**MINTED, "expires_in": 1})
    requests_mock.get(LOGS_URL, json=answer)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow --all --page-size 1")

    assert result.exit_code == 0, result.output
    assert _calls_to(requests_mock, LOGS_URL) == 2
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_stream_uses_platform_token(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """The live stream connects with the minted token."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)

    with patch("canvas_cli.apps.logs.logs.websocket.WebSocketApp") as websocket_app:
        websocket_app.return_value.run_forever.side_effect = KeyboardInterrupt
        result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 0, result.output
    assert websocket_app.call_args.args[0] == (
        "wss://logs.console.canvasmedical.com/acme-prod?token=plat-tok"
    )
    credentials_token.assert_not_called()


def test_minted_token_is_not_cached_with_instance_tokens(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """The short-lived token never lands in the credentials.ini token cache."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "plat-tok")

    with patch("canvas_cli.apps.auth.utils.set_token") as set_token:
        cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    set_token.assert_not_called()


@pytest.mark.parametrize(
    ("host", "slug"),
    [
        ("https://acme-prod.canvasmedical.com", "acme-prod"),
        ("http://localhost:8000", None),
        ("https://example.org", None),
    ],
)
def test_instance_slug(host: str, slug: str | None) -> None:
    """Only a canvasmedical.com host names a Platform instance."""
    assert instance_slug(host) == slug
