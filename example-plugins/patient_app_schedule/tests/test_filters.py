"""Tests for the patient portal provider and location filters."""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from patient_app_schedule.handlers.filters import Locations, Providers

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.v1.data.care_team import CareTeamMembershipStatus

PROVIDERS = [{"id": "staff-1"}, {"id": "staff-2"}, {"id": "staff-3"}]
LOCATIONS = [{"id": "loc-1"}, {"id": "loc-2"}]


def make_event(context: dict[str, Any], patient_id: str | None = "patient-1") -> MagicMock:
    """Build an event carrying the given context and target patient."""
    event = MagicMock()
    event.context = context
    event.target.id = patient_id
    return event


def payload(effects: list[Effect]) -> dict[str, Any]:
    """Decode the single effect's JSON payload."""
    assert len(effects) == 1
    return json.loads(effects[0].payload)


def test_providers_keeps_only_care_team_members() -> None:
    """Providers outside the patient's care team are dropped."""
    handler = Providers(event=make_event({"providers": PROVIDERS}))

    with patch.object(handler, "_get_care_team_provider_ids", return_value={"staff-1", "staff-3"}):
        effects = handler.compute()

    assert (
        effects[0].type
        == EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS
    )
    assert payload(effects) == {"providers": [{"id": "staff-1"}, {"id": "staff-3"}]}


def test_providers_returns_nothing_without_providers() -> None:
    """An empty provider list produces no effect."""
    assert Providers(event=make_event({"providers": []})).compute() == []


def test_providers_returns_all_without_a_patient() -> None:
    """With no patient to filter for, every provider is returned."""
    handler = Providers(event=make_event({"providers": PROVIDERS}, patient_id=None))

    assert payload(handler.compute()) == {"providers": PROVIDERS}


def test_providers_returns_all_when_filtering_fails() -> None:
    """An error while filtering falls back to every provider."""
    handler = Providers(event=make_event({"providers": PROVIDERS}))

    with (
        patch.object(handler, "_get_care_team_provider_ids", side_effect=RuntimeError("boom")),
        patch("patient_app_schedule.handlers.filters.log") as log,
    ):
        effects = handler.compute()

    assert payload(effects) == {"providers": PROVIDERS}
    log.error.assert_called_once_with("Error filtering providers by care team: boom")


def test_care_team_provider_ids_queries_active_members() -> None:
    """The care team lookup asks for the patient's active members' staff ids."""
    handler = Providers(event=make_event({}))

    with patch("patient_app_schedule.handlers.filters.CareTeamMembership") as membership:
        membership.objects.filter.return_value.values_list.return_value = ["staff-1", "staff-2"]
        assert handler._get_care_team_provider_ids("patient-1") == {"staff-1", "staff-2"}

    membership.objects.filter.assert_called_once_with(
        patient__id="patient-1", status=CareTeamMembershipStatus.ACTIVE
    )
    membership.objects.filter.return_value.values_list.assert_called_once_with(
        "staff__id", flat=True
    )


def test_care_team_provider_ids_is_empty_when_the_query_fails() -> None:
    """A failed care team query yields no provider ids."""
    handler = Providers(event=make_event({}))

    with (
        patch("patient_app_schedule.handlers.filters.CareTeamMembership") as membership,
        patch("patient_app_schedule.handlers.filters.log") as log,
    ):
        membership.objects.filter.side_effect = RuntimeError("db down")
        assert handler._get_care_team_provider_ids("patient-1") == set()

    log.error.assert_called_once_with("Error fetching care team members: db down")


def test_locations_keeps_only_visited_locations() -> None:
    """Locations the patient has no appointments at are dropped."""
    handler = Locations(event=make_event({"locations": LOCATIONS}))

    with patch.object(handler, "_get_patient_location_ids", return_value={"loc-2"}):
        effects = handler.compute()

    assert (
        effects[0].type
        == EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS
    )
    assert payload(effects) == {"locations": [{"id": "loc-2"}]}


def test_locations_returns_nothing_without_locations() -> None:
    """An empty location list produces no effect."""
    assert Locations(event=make_event({"locations": []})).compute() == []


def test_locations_returns_all_without_a_patient() -> None:
    """With no patient to filter for, every location is returned."""
    handler = Locations(event=make_event({"locations": LOCATIONS}, patient_id=None))

    assert payload(handler.compute()) == {"locations": LOCATIONS}


def test_locations_returns_all_when_filtering_fails() -> None:
    """An error while filtering falls back to every location."""
    handler = Locations(event=make_event({"locations": LOCATIONS}))

    with (
        patch.object(handler, "_get_patient_location_ids", side_effect=RuntimeError("boom")),
        patch("patient_app_schedule.handlers.filters.log") as log,
    ):
        effects = handler.compute()

    assert payload(effects) == {"locations": LOCATIONS}
    log.error.assert_called_once_with("Error filtering locations by appointment history: boom")


@pytest.mark.parametrize("location_id", ["loc-1", 7])
def test_patient_location_ids_are_strings(location_id: str | int) -> None:
    """Location ids from the patient's appointments come back as strings."""
    handler = Locations(event=make_event({}))

    with patch("patient_app_schedule.handlers.filters.Appointment") as appointment:
        query = appointment.objects.filter.return_value.exclude.return_value
        query.values_list.return_value.distinct.return_value = [location_id]
        assert handler._get_patient_location_ids("patient-1") == {str(location_id)}

    appointment.objects.filter.assert_called_once_with(patient__id="patient-1")


def test_patient_location_ids_is_empty_when_the_query_fails() -> None:
    """A failed appointment query yields no location ids."""
    handler = Locations(event=make_event({}))

    with (
        patch("patient_app_schedule.handlers.filters.Appointment") as appointment,
        patch("patient_app_schedule.handlers.filters.log") as log,
    ):
        appointment.objects.filter.side_effect = RuntimeError("db down")
        assert handler._get_patient_location_ids("patient-1") == set()

    log.error.assert_called_once_with("Error fetching patient appointment locations: db down")
