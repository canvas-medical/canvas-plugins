"""Tests for the PhoneDialConfiguration effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.phone_dial_configuration import (
    PhoneDialClickHandling,
    PhoneDialConfiguration,
    PhoneDialSection,
)


def test_listed_sections_are_clickable_via_the_device_phone_app_by_default() -> None:
    """Listing a section makes it clickable, dialed by the device unless asked otherwise."""
    effect = PhoneDialConfiguration(
        clickable_sections=[PhoneDialSection.PATIENT, PhoneDialSection.CONTACT]
    ).apply()

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.PHONE_DIAL__CONFIGURATION
    assert json.loads(effect.payload)["data"] == {
        "clickable_sections": ["patient", "contact"],
        "click_handling": "device",
        "dial_label": None,
    }


def test_one_handling_covers_every_section_the_effect_lists() -> None:
    """A plugin placing calls itself asks for plugin handling across the sections it lists."""
    effect = PhoneDialConfiguration(
        clickable_sections=[PhoneDialSection.CONTACT, PhoneDialSection.EXTERNAL_CARE_TEAM],
        click_handling=PhoneDialClickHandling.PLUGIN,
    ).apply()

    assert json.loads(effect.payload)["data"] == {
        "clickable_sections": ["contact", "external_care_team"],
        "click_handling": "plugin",
        "dial_label": None,
    }


def test_a_dial_label_names_the_destination() -> None:
    """A labelled section renders the number plus a button naming where the call goes."""
    effect = PhoneDialConfiguration(
        clickable_sections=[PhoneDialSection.CONTACT],
        click_handling=PhoneDialClickHandling.PLUGIN,
        dial_label="Zoom",
    ).apply()

    assert json.loads(effect.payload)["data"] == {
        "clickable_sections": ["contact"],
        "click_handling": "plugin",
        "dial_label": "Zoom",
    }


def test_requires_at_least_one_section() -> None:
    """An effect listing no section says nothing, so it is rejected."""
    with pytest.raises(ValidationError):
        PhoneDialConfiguration(clickable_sections=[])


def test_rejects_an_unknown_section() -> None:
    """Sections are limited to the chart sections that render phone numbers."""
    with pytest.raises(ValidationError):
        PhoneDialConfiguration(clickable_sections=["pharmacy"])  # type: ignore[list-item]
