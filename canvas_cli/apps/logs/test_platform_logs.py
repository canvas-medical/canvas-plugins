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
from canvas_cli.apps.platform.auth import PLATFORM_URL_ENV, SERVICE_TOKEN_ENV
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
# What home-app's logs endpoint answers, with 403, for an expired or revoked token.
NOT_AUTHENTICATED = {"detail": "Authentication credentials were not provided."}
PLUGINS_DISABLED = {"detail": "Plugins are not enabled on this Canvas instance."}
INSTANCE_OUTDATED = {
    "error": (
        "acme-prod runs a Canvas release that cannot issue log tokens yet. "
        "Sign out of Canvas Platform (canvas logout, or unset CANVAS_PLATFORM_TOKEN for a "
        "service account) to read its logs through credentials.ini until it updates."
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


@pytest.mark.parametrize(
    ("instances", "cause"),
    [
        ([_instance("acme-prod", managed=False)], "Canvas Platform does not manage acme-prod."),
        ([], "acme-prod is not one of your instances on Canvas Platform."),
    ],
    ids=["unmanaged", "not-listed"],
)
def test_signed_in_refuses_instance_platform_does_not_manage(
    instances: list[dict[str, Any]],
    cause: str,
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """Signed in, an instance Platform does not manage is refused, never read with credentials.ini."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": instances})
    _answer_logs_for(requests_mock, "ini-tok")

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert cause in result.output
    assert "sign out with `canvas logout`" in result.output
    credentials_token.assert_not_called()
    assert _calls_to(requests_mock, LOGS_URL) == 0
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 0


def test_service_token_refusal_names_the_variable(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    credentials_token: Mock,
) -> None:
    """Under CANVAS_PLATFORM_TOKEN the refusal names unsetting it, since logout leaves it."""
    monkeypatch.setenv(SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(
        f"{PLATFORM}/api/v1/instances",
        json={"instances": [_instance("acme-prod", managed=False)]},
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "unset CANVAS_PLATFORM_TOKEN" in result.output
    assert "canvas logout" not in result.output
    credentials_token.assert_not_called()


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


def test_reissues_after_expired_token_403(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """home-app answers an expired or revoked token with 403, which mints a fresh token too."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(
        LOGS_URL,
        [
            {"status_code": 403, "json": NOT_AUTHENTICATED},
            {"json": {"hits": [HIT], "next": {}}},
        ],
    )

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "hello from acme" in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_second_403_shows_the_instance_answer(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A refusal that survives a fresh token names the instance and what it answered."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(LOGS_URL, status_code=403, json=PLUGINS_DISABLED)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "acme-prod refused the log token Canvas Platform issued." in result.output
    assert PLUGINS_DISABLED["detail"] in result.output
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2


def test_second_refusal_without_detail_quotes_nothing(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A refusal whose body carries no ``detail`` adds no instance answer to the sentence."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(LOGS_URL, status_code=403, json={"error": "forbidden"})

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "acme-prod refused the log token Canvas Platform issued. Run the command again" in (
        result.output
    )
    assert "The instance answered" not in result.output


def test_second_refusal_under_service_token_names_the_variable(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    credentials_token: Mock,
) -> None:
    """``canvas logout`` leaves CANVAS_PLATFORM_TOKEN in force, so the way out is unsetting it."""
    monkeypatch.setenv(SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(LOGS_URL, status_code=403, json=PLUGINS_DISABLED)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "unset CANVAS_PLATFORM_TOKEN to use credentials.ini" in result.output
    assert "canvas logout" not in result.output


def test_credentials_ini_refusal_is_not_retried(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    credentials_token: Mock,
) -> None:
    """A refused credentials.ini token is sent once and never blamed on Canvas Platform."""
    requests_mock.get(LOGS_URL, status_code=403, json=NOT_AUTHENTICATED)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 1
    assert "Canvas Platform" not in result.output
    assert _calls_to(requests_mock, LOGS_URL) == 1
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 0
    credentials_token.assert_called_once()


def test_token_replaced_30_seconds_before_expiry(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    monkeypatch: pytest.MonkeyPatch,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """A 900-second token is replaced once it has under 30 seconds left, not at expiry."""
    clock: list[float] = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    pages: list[dict[str, Any]] = [
        {"hits": [HIT], "next": {"search_after": [1]}},
        {"hits": [HIT], "next": {}},
    ]

    def answer(request: Any, context: Any) -> dict[str, Any]:
        clock[0] += 875
        return pages.pop(0)

    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    requests_mock.get(LOGS_URL, json=answer)

    result = cli_runner.invoke(app, "logs --host acme-prod --no-follow --all --page-size 1")

    assert result.exit_code == 0, result.output
    assert _calls_to(requests_mock, LOGS_URL) == 2
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


class _FakeStream:
    """A ``WebSocketApp`` stand-in that replays one scripted connection per instance.

    Each script entry is ``(opens, close_code)``: whether the stream opens before it closes,
    and the close code Console sends. Every instance records the URL it was built with.
    """

    script: list[tuple[bool, int | None]] = []
    urls: list[str] = []

    def __init__(self, url: str, **callbacks: Any) -> None:
        self.url: str = url
        self.callbacks: dict[str, Any] = callbacks
        self.on_open: Any = None
        _FakeStream.urls.append(url)

    def run_forever(self) -> bool:
        opens, close_code = _FakeStream.script.pop(0)
        if opens:
            self.on_open(self)
        self.callbacks["on_close"](self, close_code, "")
        return False


@pytest.fixture
def fake_stream() -> Iterator[type[_FakeStream]]:
    """Patch the websocket client with ``_FakeStream`` and reset its script."""
    _FakeStream.script = []
    _FakeStream.urls = []
    with patch("canvas_cli.apps.logs.logs.websocket.WebSocketApp", _FakeStream):
        yield _FakeStream


def _stream_url(token: str) -> str:
    return f"wss://logs.console.canvasmedical.com/acme-prod?token={token}"


def test_stream_reconnects_with_fresh_token_after_4401(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
    fake_stream: type[_FakeStream],
) -> None:
    """Console closing a Platform stream with 4401 mints a new token through Platform and reconnects."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(
        LOG_TOKEN_URL,
        [{"json": MINTED}, {"json": {**MINTED, "access_token": "plat-tok-2"}}],
    )
    fake_stream.script = [(True, 4401), (True, 1000)]

    result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 0, result.output
    assert fake_stream.urls == [_stream_url("plat-tok"), _stream_url("plat-tok-2")]
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 2
    credentials_token.assert_not_called()


def test_stream_ends_when_platform_refuses_the_new_token(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
    fake_stream: type[_FakeStream],
) -> None:
    """A person who lost read_plugin_logs is stopped at the re-mint, with Platform's sentence."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(
        LOG_TOKEN_URL,
        [{"json": MINTED}, {"status_code": 403, "json": FORBIDDEN}],
    )
    fake_stream.script = [(True, 4401)]

    result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 1
    assert FORBIDDEN["error"] in result.output
    assert len(fake_stream.urls) == 1


def test_stream_refused_on_fresh_token_ends(
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
    fake_stream: type[_FakeStream],
) -> None:
    """A 4401 before the stream ever opened ends the run instead of reconnecting in a loop."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    fake_stream.script = [(False, 4401)]

    result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 1
    assert "acme-prod refused the log token Canvas Platform issued." in result.output
    assert len(fake_stream.urls) == 1


@pytest.mark.parametrize("close_code", [1000, 1011, None], ids=["normal", "error", "interrupt"])
def test_stream_other_closes_end_the_run(
    close_code: int | None,
    cli_runner: CliRunner,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
    fake_stream: type[_FakeStream],
) -> None:
    """Only 4401 reconnects; any other close, or Ctrl-C (no code), ends the stream."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    fake_stream.script = [(True, close_code)]

    result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 0, result.output
    assert len(fake_stream.urls) == 1
    assert _calls_to(requests_mock, LOG_TOKEN_URL) == 1


def test_credentials_ini_stream_does_not_reconnect_on_4401(
    cli_runner: CliRunner,
    credentials_token: Mock,
    fake_stream: type[_FakeStream],
) -> None:
    """credentials.ini streams keep check-at-connect: a 4401 ends them as any close does."""
    fake_stream.script = [(True, 4401)]

    result = cli_runner.invoke(app, "logs --host acme-prod")

    assert result.exit_code == 0, result.output
    assert fake_stream.urls == [_stream_url("ini-tok")]
    credentials_token.assert_called_once()


CREDENTIALS_INI_NOTICE = (
    "`canvas logs` with credentials.ini is deprecated in favor of `canvas login`, and is no "
    "longer supported as of December 14, 2026."
)


@pytest.mark.parametrize("host", ["acme-prod", "localhost"])
def test_credentials_ini_run_prints_deprecation_notice(
    host: str,
    requests_mock: requests_mock_module.Mocker,
    credentials_token: Mock,
) -> None:
    """Every credentials.ini run warns on stderr, leaving stdout to the logs."""
    requests_mock.get(LOGS_URL, json={"hits": [HIT], "next": {}})
    requests_mock.get(
        plugin_url("http://localhost:8000", "/logs"), json={"hits": [HIT], "next": {}}
    )

    result = CliRunner(mix_stderr=False).invoke(app, f"logs --host {host} --no-follow")

    assert result.exit_code == 0, result.output
    assert CREDENTIALS_INI_NOTICE in result.stderr
    assert "canvas-plugins#migrating-from-credentialsini-to-canvas-platform" in result.stderr
    assert "deprecated" not in result.stdout


def test_platform_run_prints_no_deprecation_notice(
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
    credentials_token: Mock,
) -> None:
    """The Platform path is the supported one, so it prints no credentials.ini notice."""
    requests_mock.get(f"{PLATFORM}/api/v1/instances", json={"instances": [_instance("acme-prod")]})
    requests_mock.post(LOG_TOKEN_URL, json=MINTED)
    _answer_logs_for(requests_mock, "plat-tok")

    result = CliRunner(mix_stderr=False).invoke(app, "logs --host acme-prod --no-follow")

    assert result.exit_code == 0, result.output
    assert "deprecated" not in result.stderr
