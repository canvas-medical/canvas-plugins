"""Tests for the HTTP transport that ships plugin logs to Logstash.

``python-logstash-async`` hands the transport a batch of encoded events and
requeues the batch when ``send`` raises, so ``send`` must raise on anything
worth retrying and return normally once the batch is delivered or rejected.
"""

import json

import pytest
import requests
import requests_mock as rm

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


def test_send_drops_a_batch_logstash_rejects(
    requests_mock: rm.Mocker, capsys: pytest.CaptureFixture[str]
) -> None:
    """A 4xx would fail the same way on every retry, so it is reported and dropped."""
    requests_mock.post(URL, status_code=413)

    HttpTransport(URL).send(_events())

    assert "413" in capsys.readouterr().out
