import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.redirect import RedirectEffect


def test_redirect_apply_produces_correct_effect_type() -> None:
    """RedirectEffect.apply() should produce an effect with type REDIRECT."""
    effect = RedirectEffect(url="https://example.com").apply()
    assert effect.type == EffectType.REDIRECT


def test_redirect_payload_contains_url_and_target() -> None:
    """The payload should contain url and target."""
    effect = RedirectEffect(
        url="https://example.com/next",
        target=RedirectEffect.TargetType.NEW_TAB,
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "https://example.com/next"
    assert data["target"] == "new_tab"


def test_redirect_defaults_to_same_tab() -> None:
    """The default target should be same_tab."""
    effect = RedirectEffect(url="/panel").apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "/panel"
    assert data["target"] == "same_tab"


def test_redirect_accepts_internal_relative_path() -> None:
    """An internal Canvas path should be a valid target string."""
    effect = RedirectEffect(url="/patient/abc123?noteId=42").apply()

    data = json.loads(effect.payload)["data"]
    assert data["url"] == "/patient/abc123?noteId=42"


def test_redirect_empty_url_raises() -> None:
    """An empty URL should raise a validation error."""
    with pytest.raises(ValidationError):
        RedirectEffect(url="")


def test_redirect_invalid_target_raises() -> None:
    """An invalid target should raise a validation error."""
    with pytest.raises(ValidationError):
        RedirectEffect(url="https://example.com", target="popup")  # type: ignore[arg-type]
