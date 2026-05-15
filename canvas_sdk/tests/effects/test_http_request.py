import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.http_request import HttpMethod, HttpRequestEffect


def test_http_request_apply_produces_correct_effect_type() -> None:
    """HttpRequestEffect.apply() should produce an effect with type HTTP_REQUEST."""
    effect = HttpRequestEffect(url="https://api.example.com/test", method=HttpMethod.GET).apply()
    assert effect.type == EffectType.HTTP_REQUEST


def test_http_request_payload_contains_request_details() -> None:
    """The payload should contain url, method, headers, and body."""
    effect = HttpRequestEffect(
        url="https://api.example.com/submit",
        method=HttpMethod.POST,
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
    assert data["retry_on_status_codes"] == []


def test_http_request_payload_contains_retry_on_status_codes() -> None:
    """retry_on_status_codes should be included in the payload data."""
    effect = HttpRequestEffect(
        url="https://api.example.com/submit",
        method=HttpMethod.POST,
        retry_on_status_codes=[500, 502, 503],
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["retry_on_status_codes"] == [500, 502, 503]


def test_http_request_async_props_contains_retry_on_status_codes() -> None:
    """retry_on_status_codes should be included in async_props with delay_seconds=0."""
    effect = HttpRequestEffect(
        url="https://api.example.com/submit",
        retry_on_status_codes=[500, 501],
    ).apply()

    payload = json.loads(effect.payload)
    assert payload["async_props"] == {
        "retry_on_status_codes": [500, 501],
        "delay_seconds": 0,
    }


def test_http_request_no_async_props_when_retry_on_status_codes_unset() -> None:
    """async_props should be omitted entirely when retry_on_status_codes isn't provided."""
    effect = HttpRequestEffect(url="https://api.example.com").apply()

    payload = json.loads(effect.payload)
    assert "async_props" not in payload


def test_http_request_no_async_props_when_retry_on_status_codes_empty() -> None:
    """An empty retry_on_status_codes list should not trigger async execution."""
    effect = HttpRequestEffect(
        url="https://api.example.com",
        retry_on_status_codes=[],
    ).apply()

    payload = json.loads(effect.payload)
    assert "async_props" not in payload


def test_http_request_set_async_overrides_default_delay_seconds() -> None:
    """.set_async(delay_seconds=N) should override the default delay_seconds=0."""
    effect = (
        HttpRequestEffect(
            url="https://api.example.com",
            retry_on_status_codes=[500],
        )
        .apply()
        .set_async(delay_seconds=30)
    )

    payload = json.loads(effect.payload)
    assert payload["async_props"]["delay_seconds"] == 30
    assert payload["async_props"]["retry_on_status_codes"] == [500]


def test_http_request_retry_on_status_codes_invalid_type_raises() -> None:
    """retry_on_status_codes must be a list of ints."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(
            url="https://api.example.com",
            retry_on_status_codes=["not-an-int"],  # type: ignore[list-item]
        )


@pytest.mark.parametrize("bad_code", [99, 600, 0, -1, 1000])
def test_http_request_retry_on_status_codes_out_of_range_raises(bad_code: int) -> None:
    """retry_on_status_codes items must be valid HTTP status codes (100-599)."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(
            url="https://api.example.com",
            retry_on_status_codes=[bad_code],
        )


@pytest.mark.parametrize("good_code", [100, 408, 429, 500, 599])
def test_http_request_retry_on_status_codes_in_range_accepted(good_code: int) -> None:
    """retry_on_status_codes items within 100-599 should be accepted."""
    effect = HttpRequestEffect(
        url="https://api.example.com",
        retry_on_status_codes=[good_code],
    )
    assert effect.retry_on_status_codes == [good_code]


def test_http_request_invalid_method_raises() -> None:
    """An invalid HTTP method should raise a validation error."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(url="https://api.example.com", method="INVALID")  # type: ignore[arg-type]


def test_http_request_empty_url_raises() -> None:
    """An empty URL should raise a validation error."""
    with pytest.raises(ValidationError):
        HttpRequestEffect(url="", method=HttpMethod.GET)
