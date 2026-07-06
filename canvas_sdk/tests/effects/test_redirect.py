import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.redirect import RedirectEffect


def test_redirect_apply_produces_correct_effect_type() -> None:
    """RedirectEffect.apply() should produce an effect with type REDIRECT."""
    effect = RedirectEffect(url="https://example.com").apply()
    assert effect.type == EffectType.REDIRECT


def test_redirect_payload_contains_url_target_and_application_id() -> None:
    """The payload should contain url, application_id, and target."""
    effect = RedirectEffect(
        url="https://example.com/next",
        target=RedirectEffect.TargetType.NEW_TAB,
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "https://example.com/next"
    assert data["application_id"] is None
    assert data["target"] == "new_tab"


def test_redirect_defaults_to_same_tab() -> None:
    """The default target should be same_tab."""
    effect = RedirectEffect(url="/panel").apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "/panel"
    assert data["target"] == "same_tab"


def test_redirect_accepts_internal_composed_path() -> None:
    """An internal Canvas path (composed with ids) should be a valid target string."""
    effect = RedirectEffect(url="/patient/abc123?noteId=42").apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "/patient/abc123?noteId=42"


@patch("canvas_sdk.effects.redirect.Application.objects.filter")
def test_redirect_accepts_application_id(mock_filter: MagicMock) -> None:
    """An existing application identifier should produce a valid payload."""
    mock_filter.return_value.exists.return_value = True

    effect = RedirectEffect(application_id="my_plugin.apps:MyApp").apply()

    data = json.loads(effect.payload)["data"]
    assert data["application_id"] == "my_plugin.apps:MyApp"
    assert data["url"] is None


def test_redirect_empty_url_raises() -> None:
    """An empty URL should raise a validation error at construction."""
    with pytest.raises(ValidationError):
        RedirectEffect(url="")


def test_redirect_invalid_target_raises() -> None:
    """An invalid target should raise a validation error at construction."""
    with pytest.raises(ValidationError):
        RedirectEffect(url="https://example.com", target="popup")  # type: ignore[arg-type]


def test_redirect_requires_a_destination() -> None:
    """Providing neither url nor application_id should raise at apply()."""
    with pytest.raises(ValidationError) as exc_info:
        RedirectEffect().apply()

    assert "Exactly one of 'url' or 'application_id' must be provided" in repr(exc_info.value)


@patch("canvas_sdk.effects.redirect.Application.objects.filter")
def test_redirect_url_and_application_id_are_mutually_exclusive(mock_filter: MagicMock) -> None:
    """Providing both url and application_id should raise at apply()."""
    mock_filter.return_value.exists.return_value = True

    with pytest.raises(ValidationError) as exc_info:
        RedirectEffect(url="/panel", application_id="my_plugin.apps:MyApp").apply()

    assert "Exactly one of 'url' or 'application_id' must be provided" in repr(exc_info.value)


@patch("canvas_sdk.effects.redirect.Application.objects.filter")
def test_redirect_nonexistent_application_raises(mock_filter: MagicMock) -> None:
    """An application_id that doesn't exist should raise at apply()."""
    mock_filter.return_value.exists.return_value = False

    with pytest.raises(ValidationError) as exc_info:
        RedirectEffect(application_id="nonexistent.apps:NoApp").apply()

    assert "Application with identifier nonexistent.apps:NoApp does not exist" in repr(
        exc_info.value
    )
