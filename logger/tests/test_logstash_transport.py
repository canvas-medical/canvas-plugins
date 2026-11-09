"""Tests for the HTTP transport that ships plugin logs to Logstash.

``python-logstash-async`` hands the transport a batch of encoded events and
requeues the batch when ``send`` raises, so ``send`` must raise on anything
worth retrying and return normally once the batch is delivered or rejected.
"""

import json
import logging
import math
from typing import Any

import pytest
import requests
import requests_mock as rm
from logstash_async.constants import constants
from logstash_async.handler import AsynchronousLogstashHandler
from pytest_django.fixtures import SettingsWrapper
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context

from logger.logger import (
    LOGSTASH_ERROR_LOG_RATE_LIMIT,
    LOGSTASH_EVENT_TTL_SECONDS,
    PluginLogger,
)
from logger.logstash import LOGSTASH_TIMEOUT_SECONDS, HttpTransport, LogstashFormatterECS

URL = "https://logstash.example.com"


def _events() -> list[bytes]:
    """Events as the async handler produces them: UTF-8 JSON plus a newline."""
    return [json.dumps({"message": f"line {i}"}).encode() + b"\n" for i in range(3)]


def test_send_posts_the_whole_batch_as_one_json_array(requests_mock: rm.Mocker) -> None:
    """One request per batch, so a burst of log lines is not a burst of requests."""
    requests_mock.post(URL, status_code=200)

    HttpTransport(URL).send(_events())

    request = requests_mock.last_request
    assert requests_mock.call_count == 1
    assert request is not None
    assert json.loads(request.body) == [
        {"message": "line 0"},
        {"message": "line 1"},
        {"message": "line 2"},
    ]
    assert request.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("status_code", [429, 500, 502, 503])
def test_send_raises_on_retryable_status(requests_mock: rm.Mocker, status_code: int) -> None:
    """A 5xx or 429 raises so the worker requeues the batch instead of dropping it."""
    requests_mock.post(URL, status_code=status_code)

    with pytest.raises(requests.HTTPError):
        HttpTransport(URL).send(_events())


def test_send_raises_on_connection_error(requests_mock: rm.Mocker) -> None:
    """Network failures propagate so the worker requeues the batch."""
    requests_mock.post(URL, exc=requests.ConnectionError)

    with pytest.raises(requests.ConnectionError):
        HttpTransport(URL).send(_events())


def test_plugin_logger_expires_events_it_cannot_send(settings: SettingsWrapper) -> None:
    """Failed batches are requeued, so unsent events need a TTL or a long Logstash outage
    grows the plugin runner's in-memory queue without bound.
    """
    settings.LOGSTASH_HOST = URL
    plugin_logger = logging.getLogger("plugin_runner_logger")
    handlers_before = list(plugin_logger.handlers)

    PluginLogger()

    added = [h for h in plugin_logger.handlers if h not in handlers_before]
    for handler in added:
        plugin_logger.removeHandler(handler)
    [logstash_handler] = [h for h in added if isinstance(h, AsynchronousLogstashHandler)]
    assert logstash_handler._event_ttl == LOGSTASH_EVENT_TTL_SECONDS


def test_send_drops_an_event_logstash_rejects(
    requests_mock: rm.Mocker, capsys: pytest.CaptureFixture[str]
) -> None:
    """A 4xx would fail the same way on every retry, so it is reported and dropped."""
    requests_mock.post(URL, status_code=413)

    HttpTransport(URL).send(_events()[:1])

    assert requests_mock.call_count == 1
    assert "413" in capsys.readouterr().out


def test_send_retries_a_rejected_batch_one_event_at_a_time(
    requests_mock: rm.Mocker, capsys: pytest.CaptureFixture[str]
) -> None:
    """One event Logstash rejects does not take the rest of its batch down with it."""
    delivered = []

    def respond(request: _RequestObjectProxy, context: _Context) -> str:
        body = request.body
        assert isinstance(body, bytes)
        if body.startswith(b"[") or b"line 1" in body:
            context.status_code = 413
        else:
            delivered.append(json.loads(body))
        return ""

    requests_mock.post(URL, text=respond)

    HttpTransport(URL).send(_events())

    assert delivered == [{"message": "line 0"}, {"message": "line 2"}]
    assert "413" in capsys.readouterr().out


@pytest.mark.parametrize("status_code", [401, 403, 404])
def test_send_drops_a_batch_without_resending_when_logstash_is_misconfigured(
    requests_mock: rm.Mocker, capsys: pytest.CaptureFixture[str], status_code: int
) -> None:
    """A wrong URL or credential rejects every event alike, so resending one at a time would
    only multiply the requests before dropping them all.
    """
    requests_mock.post(URL, status_code=status_code)

    HttpTransport(URL).send(_events())

    assert requests_mock.call_count == 1
    assert str(status_code) in capsys.readouterr().out


def test_send_sets_a_timeout(requests_mock: rm.Mocker) -> None:
    """A hung connection must not hold the worker thread, which also expires queued events."""
    requests_mock.post(URL, status_code=200)

    HttpTransport(URL).send(_events())

    request = requests_mock.last_request
    assert request is not None
    # requests_mock's stub types timeout as int; it holds whatever was passed to post()
    assert request.timeout == LOGSTASH_TIMEOUT_SECONDS  # type: ignore[comparison-overlap]


def test_plugin_logger_rate_limits_logstash_error_logs() -> None:
    """Each failed retry logs a warning, so an outage would log one per flush per process."""
    assert constants.ERROR_LOG_RATE_LIMIT == LOGSTASH_ERROR_LOG_RATE_LIMIT


def _format(msg: object, args: tuple[object, ...] = (), **extra: object) -> str:
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0, msg=msg, args=args, exc_info=None
    )
    record.__dict__.update(extra)
    return LogstashFormatterECS().format(record)


def _loads_strict(event: str) -> Any:
    """Parse like Logstash does: NaN and Infinity are not JSON."""

    def reject(constant: str) -> Any:
        raise ValueError(constant)

    return json.loads(event, parse_constant=reject)


@pytest.mark.parametrize(
    ("msg", "message"),
    [
        ({"event": math.nan}, "NaN"),
        ({"event": {"ratio": math.inf}}, '{"ratio": Infinity}'),
        ({"event": {"url": "/icd/condition/"}}, '{"url": "/icd/condition/"}'),
        ({"event": 3}, "3"),
    ],
)
def test_formatter_ships_a_non_string_message_as_json_text(msg: object, message: str) -> None:
    """Logstash cannot parse NaN or Infinity, and the plugin log data streams map ``message`` as
    text, so a non-string message is shipped as its JSON text.
    """
    assert _loads_strict(_format(msg))["message"] == message


def test_formatter_output_is_strict_json_for_non_finite_args_and_extras() -> None:
    """Format args are rendered into the message text and extras are not shipped."""
    output = _loads_strict(_format("ratio %s", (math.nan,), ratio=math.inf))

    assert output["message"] == "ratio nan"
