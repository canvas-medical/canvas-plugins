import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_portal.application_configuration import (
    PatientPortalApplicationConfiguration,
)
from canvas_sdk.v1.data import Application

APPLICATION_FILTER = (
    "canvas_sdk.effects.patient_portal.application_configuration.Application.objects.filter"
)


def test_apply_with_can_schedule_appointments_only() -> None:
    """The payload carries both keys, with a null default application identifier."""
    applied = PatientPortalApplicationConfiguration(can_schedule_appointments=True).apply()

    assert applied.type == EffectType.PATIENT_PORTAL__APPLICATION_CONFIGURATION
    assert json.loads(applied.payload) == {
        "data": {"can_schedule_appointments": True, "default_homepage_application_identifier": None}
    }


@pytest.mark.django_db
def test_apply_with_default_homepage_application_identifier_only() -> None:
    """The payload carries the identifier of an existing application and a null schedule flag."""
    Application.objects.create(
        identifier="my_plugin.apps:HomeApp", name="Home", description="Portal home page."
    )

    applied = PatientPortalApplicationConfiguration(
        default_homepage_application_identifier="my_plugin.apps:HomeApp"
    ).apply()

    assert json.loads(applied.payload) == {
        "data": {
            "can_schedule_appointments": None,
            "default_homepage_application_identifier": "my_plugin.apps:HomeApp",
        }
    }


@patch(APPLICATION_FILTER)
def test_apply_with_both_values(mock_filter: MagicMock) -> None:
    """The payload carries both values when both are set."""
    mock_filter.return_value.exists.return_value = True

    applied = PatientPortalApplicationConfiguration(
        can_schedule_appointments=False,
        default_homepage_application_identifier="my_plugin.apps:HomeApp",
    ).apply()

    assert json.loads(applied.payload) == {
        "data": {
            "can_schedule_appointments": False,
            "default_homepage_application_identifier": "my_plugin.apps:HomeApp",
        }
    }
    mock_filter.assert_called_once_with(identifier="my_plugin.apps:HomeApp")


@pytest.mark.parametrize("identifier", [None, ""])
@patch(APPLICATION_FILTER)
def test_apply_without_values(mock_filter: MagicMock, identifier: str | None) -> None:
    """An effect without values applies, so a plugin can set a value for some patients only."""
    applied = PatientPortalApplicationConfiguration(
        default_homepage_application_identifier=identifier
    ).apply()

    assert json.loads(applied.payload) == {
        "data": {
            "can_schedule_appointments": None,
            "default_homepage_application_identifier": identifier,
        }
    }
    mock_filter.assert_not_called()


@pytest.mark.django_db
def test_apply_raises_error_when_application_does_not_exist() -> None:
    """The apply method raises an error when the default application does not exist."""
    with pytest.raises(ValidationError) as exc_info:
        PatientPortalApplicationConfiguration(
            default_homepage_application_identifier="nonexistent.apps:NoApp"
        ).apply()

    assert "Application with identifier nonexistent.apps:NoApp does not exist" in repr(
        exc_info.value
    )
