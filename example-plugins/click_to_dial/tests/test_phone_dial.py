import json
from unittest.mock import MagicMock

import pytest
from click_to_dial.handlers.phone_dial import ClickToDialConfiguration, PlaceCall

from canvas_generated.messages.effects_pb2 import EffectType


def _place_call(context: dict) -> PlaceCall:
    """Build the click handler for an event carrying the given context."""
    handler = PlaceCall(event=MagicMock())
    handler.event.context = context

    return handler


def test_configuration_responds_to_the_phone_dial_configuration_event() -> None:
    """The configuration handler subscribes to the phone dial configuration event."""
    assert ClickToDialConfiguration.RESPONDS_TO == "PHONE_DIAL__GET_CONFIGURATION"


def test_configuration_splits_the_sections_by_who_dials_them() -> None:
    """A labelled Zoom section, an unlabelled recorded section, and one left to the device."""
    effects = ClickToDialConfiguration(event=MagicMock()).compute()

    assert [effect.type for effect in effects] == [EffectType.PHONE_DIAL__CONFIGURATION] * 3

    payloads = [json.loads(effect.payload)["data"] for effect in effects]
    assert payloads == [
        {
            "clickable_sections": ["contact"],
            "click_handling": "plugin",
            "dial_label": "Zoom",
        },
        {
            "clickable_sections": ["patient"],
            "click_handling": "plugin",
            "dial_label": None,
        },
        {
            "clickable_sections": ["external_care_team"],
            "click_handling": "device",
            "dial_label": None,
        },
    ]


def test_place_call_responds_to_the_phone_number_clicked_event() -> None:
    """The click handler subscribes to the phone number clicked event."""
    assert PlaceCall.RESPONDS_TO == "PHONE_NUMBER_CLICKED"


@pytest.mark.parametrize("section", ["patient", "contact", "external_care_team"])
def test_place_call_dials_every_section_through_zoom(section: str) -> None:
    """Every click dials, whatever section it came from, carrying only the number's digits."""
    handler = _place_call({"phone_number": "(347) 111-1234", "source": section})

    effects = handler.compute()

    assert len(effects) == 1
    assert effects[0].type == EffectType.REDIRECT

    data = json.loads(effects[0].payload)["data"]
    assert data["url"] == "zoomus://zoom.us/call?number=3471111234"
    # A new tab would be popup-blocked, since the redirect arrives outside the click.
    assert data["target"] == "same_tab"
