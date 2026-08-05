import json
from unittest.mock import MagicMock

from example_provider_menu_configuration.handlers.provider_menu import (
    HideAppointmentsPanelFilter,
    HideScheduleMenuItem,
    LandOnPatientsInsteadOfSchedule,
)

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.panel_configuration import PanelConfiguration
from canvas_sdk.effects.provider_menu_configuration import ProviderMenuConfiguration


def _panel_handler(target_id: str) -> HideAppointmentsPanelFilter:
    """Build the panel handler for an event carrying the given target id."""
    event = MagicMock()
    event.target.id = target_id

    return HideAppointmentsPanelFilter(event=event)


def test_hide_schedule_responds_to_the_provider_menu_configuration_event() -> None:
    """The menu handler subscribes to the provider menu configuration event."""
    assert HideScheduleMenuItem.RESPONDS_TO == "GET_PROVIDER_MENU_CONFIGURATION"


def test_hide_schedule_omits_only_schedule() -> None:
    """The allow-list carries every menu item except Schedule."""
    effects = HideScheduleMenuItem(event=MagicMock()).compute()

    assert len(effects) == 1
    assert effects[0].type == EffectType.SHOW_PROVIDER_MENU_ITEMS

    items = json.loads(effects[0].payload)["data"]["items"]
    expected = [item.value for item in ProviderMenuConfiguration.Items if item.value != "schedule"]
    assert items == expected


def test_panel_handler_responds_to_the_panel_sections_configuration_event() -> None:
    """The panel handler subscribes to the panel sections configuration event."""
    assert HideAppointmentsPanelFilter.RESPONDS_TO == "PANEL_SECTIONS_CONFIGURATION"


def test_panel_handler_omits_only_appointments_on_the_global_panel() -> None:
    """The global panel keeps every section except Appointments."""
    effects = _panel_handler("").compute()

    assert len(effects) == 1
    assert effects[0].type == EffectType.SHOW_PANEL_SECTIONS

    sections = json.loads(effects[0].payload)["data"]["sections"]
    expected = [
        section.value
        for section in PanelConfiguration.PanelGlobalSection
        if section is not PanelConfiguration.PanelGlobalSection.APPOINTMENT
    ]
    assert sections == expected


def test_panel_handler_leaves_a_patients_panel_alone() -> None:
    """A patient's panel carries a target and must not be reconfigured.

    The global and patient panels share one event, and the patient panel has no
    Appointments section, so returning global sections there would replace a
    patient's panel with the wrong set.
    """
    assert _panel_handler("a-patient-key").compute() == []


def test_homepage_handler_responds_to_the_homepage_configuration_event() -> None:
    """The homepage handler subscribes to the homepage configuration event."""
    assert LandOnPatientsInsteadOfSchedule.RESPONDS_TO == "GET_HOMEPAGE_CONFIGURATION"


def test_homepage_handler_points_at_the_patients_page() -> None:
    """Providers land on the patients page rather than the hidden schedule page."""
    effects = LandOnPatientsInsteadOfSchedule(event=MagicMock()).compute()

    assert len(effects) == 1
    assert effects[0].type == EffectType.HOMEPAGE_CONFIGURATION
    assert json.loads(effects[0].payload)["data"]["page"] == "/patients"
