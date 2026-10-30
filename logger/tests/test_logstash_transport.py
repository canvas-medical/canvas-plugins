"""Tests for the HTTP transport that ships plugin logs to Logstash.

``python-logstash-async`` hands the transport a batch of encoded events and
requeues the batch when ``send`` raises, so ``send`` must raise on anything
worth retrying and return normally once the batch is delivered or rejected.
"""

import json
import logging

import pytest
import requests
import requests_mock as rm
from logstash_async.handler import AsynchronousLogstashHandler
from pytest_django.fixtures import SettingsWrapper
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context

from logger.logger import LOGSTASH_EVENT_TTL_SECONDS, PluginLogger
from logger.logstash import HttpTransport

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


def test_send_posts_an_event_that_is_not_strict_json_on_its_own(requests_mock: rm.Mocker) -> None:
    """Logstash fails to parse NaN, and a parse failure turns the whole request body into one
    unparsed event, so a NaN event must not share a request with valid ones.
    """
    requests_mock.post(URL, status_code=200)
    nan_event = b'{"message": "line 1", "ratio": NaN}\n'
    events = _events()

    HttpTransport(URL).send([events[0], nan_event, events[2]])

    bodies = [request.body for request in requests_mock.request_history]
    assert bodies == [nan_event.strip(), b"[" + events[0].strip() + b"," + events[2].strip() + b"]"]
