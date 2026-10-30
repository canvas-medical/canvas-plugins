"""Scenario tests for `canvas logs` through a Platform-issued log token: one run across history
and the live stream, a refused re-mint after a 401, and a CI service account token.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests_mock as requests_mock_module
from typer.testing import CliRunner

from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.auth import PLATFORM_URL_ENV, SERVICE_TOKEN_ENV
from canvas_cli.apps.plugin.plugin import plugin_url
from canvas_cli.main import app

PLATFORM = "https://platform.example"
HOST = "https://acme-prod.canvasmedical.com"
LOGS_URL = plugin_url(HOST, "/logs")
INSTANCES_URL = f"{PLATFORM}/api/v1/instances"
LOG_TOKEN_URL = f"{PLATFORM}/api/v1/instances/acme-prod/log-token"
STREAM = "wss://logs.console.canvasmedical.com/acme-prod?token="
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
MANAGED = {
    "instances": [
        {
            "slug": "acme-prod",
            "organization": "acme",
            "stage": "production",
            "production": True,
            "managed": True,
            "capabilities": [],
        }
    ]
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


@pytest.fixture
def websocket_app() -> Iterator[MagicMock]:
    """The live stream's socket, which ends the run as soon as it would start streaming."""
    with patch("canvas_cli.apps.logs.logs.websocket.WebSocketApp") as mock:
        mock.return_value.run_forever.side_effect = KeyboardInterrupt
        yield mock


def test_history_and_stream_share_one_token(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
    websocket_app: MagicMock,
) -> None:
    """A run that reads history and then streams mints once and uses that token for both."""
    requests_mock.get(INSTANCES_URL, json=MANAGED)
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(
        LOGS_URL,
        request_headers={"Authorization": "Bearer plat-tok"},
        json={"hits": [HIT], "next": {}},
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --since 1h")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert websocket_app.call_args.args[0] == f"{STREAM}plat-tok"
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 1
    credentials_token.assert_not_called()


def test_stream_after_long_history_gets_a_fresh_token(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    signed_in: None,
    credentials_token: Mock,
    websocket_app: MagicMock,
) -> None:
    """History that outlasts the token hands Console a freshly minted one, never the expired one."""
    clock: list[float] = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])

    def history(request: Any, context: Any) -> dict[str, Any]:
        clock[0] += 900
        return {"hits": [HIT], "next": {}}

    requests_mock.get(INSTANCES_URL, json=MANAGED)
    requests_mock.post(
        LOG_TOKEN_URL,
        [{"json": MINTED}, {"json": {**MINTED, "access_token": "plat-tok-2"}}],
    )
    requests_mock.get(LOGS_URL, json=history)

    result = cli_runner.invoke(app, "logs --host acme-prod --since 1h")

    assert result.exit_code == 0, result.output
    assert requests_mock.request_history[-1].url.split("?")[0] == LOG_TOKEN_URL
    assert websocket_app.call_args.args[0] == f"{STREAM}plat-tok-2"
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_refused_remint_after_401_is_shown_once(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A capability revoked between two mints ends the run with Platform's sentence, no loop.

    D1: a refusal on a managed instance is shown, never silently replaced by credentials.ini.
    """
    requests_mock.get(INSTANCES_URL, json=MANAGED)
    requests_mock.post(
        LOG_TOKEN_URL,
        [{"json": MINTED}, {"status_code": 403, "json": FORBIDDEN}],
    )
    requests_mock.get(LOGS_URL, status_code=401)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert FORBIDDEN["error"] in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2
    assert _calls_to(requests_mock, LOGS_URL) == 1
    credentials_token.assert_not_called()


def test_ci_service_account_token_mints_log_token(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    credentials_token: Mock,
) -> None:
    """A CI job holding a service account token reads a managed instance's logs through Platform."""
    monkeypatch.setenv(SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    service = {"Authorization": "Bearer cnvs_sa_ci"}
    requests_mock.get(INSTANCES_URL, request_headers=service, json=MANAGED)
    requests_mock.post(LOG_TOKEN_URL, request_headers=service, json=MINTED)
    requests_mock.get(
        LOGS_URL,
        request_headers={"Authorization": "Bearer plat-tok"},
        json={"hits": [HIT], "next": {}},
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 1
    credentials_token.assert_not_called()
