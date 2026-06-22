"""Tests for the NoteFooterConfiguration effect."""

import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.note_footer_configuration import NoteFooterConfiguration


def test_defaults_to_not_hiding_state_buttons() -> None:
    """By default the configuration leaves the native state buttons in place."""
    effect = NoteFooterConfiguration().apply()

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.NOTE_FOOTER__CONFIGURATION
    assert json.loads(effect.payload)["data"]["hide_default_state_buttons"] is False


def test_can_hide_default_state_buttons() -> None:
    """hide_default_state_buttons=True is carried in the payload."""
    effect = NoteFooterConfiguration(hide_default_state_buttons=True).apply()

    assert json.loads(effect.payload)["data"]["hide_default_state_buttons"] is True
