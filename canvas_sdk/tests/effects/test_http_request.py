import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.http_request import HttpRequestEffect


def test_http_request_apply_produces_correct_effect_type() -> None:
    """HttpRequestEffect.apply() should produce an effect with type HTTP_REQUEST."""
    effect = HttpRequestEffect(url="https://api.example.com/test", method="GET").apply()
    assert effect.type == EffectType.HTTP_REQUEST


def test_http_request_payload_contains_request_details() -> None:
    """The payload should contain url, method, headers, and body."""
    effect = HttpRequestEffect(
        url="https://api.example.com/submit",
        method="POST",
        headers={"Authorization": "Bearer tok123", "Content-Type": "application/json"},
        body='{"key": "value"}',
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "https://api.example.com/submit"
    assert data["method"] == "POST"
    assert data["headers"]["Authorization"] == "Bearer tok123"
    assert data["body"] == '{"key": "value"}'


def test_http_request_defaults() -> None:
    """Default method should be GET, headers empty, body empty."""
    effect = HttpRequestEffect(url="https://api.example.com").apply()

    data = json.loads(effect.payload)["data"]
    assert data["method"] == "GET"
    assert data["headers"] == {}
    assert data["body"] == ""


# def test_http_request_with_delay() -> None:
#     """delay_seconds should be set on the Effect protobuf."""
#     effect = HttpRequestEffect(
#         url="https://api.example.com",
#     ).apply(delay_seconds=60)

#     assert effect.HasField("delay_seconds")
#     assert effect.delay_seconds == 60


def test_http_request_invalid_method_raises() -> None:
    """An invalid HTTP method should raise a validation error."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(url="https://api.example.com", method="INVALID")


def test_http_request_empty_url_raises() -> None:
    """An empty URL should raise a validation error."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(url="", method="GET")
