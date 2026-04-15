import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.http_request import HttpRequest


def test_http_request_apply_produces_correct_effect_type() -> None:
    """HttpRequest.apply() should produce an effect with type HTTP_REQUEST."""
    effect = HttpRequest(url="https://api.example.com/test", method="GET").apply()
    assert effect.type == EffectType.HTTP_REQUEST


def test_http_request_payload_contains_request_details() -> None:
    """The payload should contain url, method, headers, and body."""
    effect = HttpRequest(
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
    effect = HttpRequest(url="https://api.example.com").apply()

    data = json.loads(effect.payload)["data"]
    assert data["method"] == "GET"
    assert data["headers"] == {}
    assert data["body"] == ""


def test_http_request_with_on_success_and_on_failure() -> None:
    """on_success and on_failure effects should be serialized into the payload."""
    success_effect = Effect(type=EffectType.LOG, payload='{"data": {"message": "ok"}}')
    failure_effect = Effect(type=EffectType.LOG, payload='{"data": {"message": "fail"}}')

    effect = HttpRequest(
        url="https://api.example.com/submit",
        method="POST",
        on_success=[success_effect],
        on_failure=[failure_effect],
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert len(data["on_success"]) == 1
    assert data["on_success"][0]["type"] == EffectType.LOG
    assert json.loads(data["on_success"][0]["payload"])["data"]["message"] == "ok"
    assert len(data["on_failure"]) == 1
    assert json.loads(data["on_failure"][0]["payload"])["data"]["message"] == "fail"


def test_http_request_without_chaining_omits_keys() -> None:
    """When on_success/on_failure are not set, they should not appear in the payload."""
    effect = HttpRequest(url="https://api.example.com").apply()

    data = json.loads(effect.payload)["data"]
    assert "on_success" not in data
    assert "on_failure" not in data


def test_http_request_with_delay() -> None:
    """delay_seconds should be set on the Effect protobuf."""
    effect = HttpRequest(
        url="https://api.example.com",
    ).apply(delay_seconds=60)

    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_http_request_invalid_method_raises() -> None:
    """An invalid HTTP method should raise a validation error."""
    with pytest.raises(ValidationError):
        HttpRequest(url="https://api.example.com", method="INVALID")
