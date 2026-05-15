import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.configure_command_buttons import ConfigureCommandButtons

Location = ConfigureCommandButtons.Location
LocationConfig = ConfigureCommandButtons.LocationConfig
Visibility = ConfigureCommandButtons.Visibility


def test_effect_type() -> None:
    """Effect type must be PATIENT_CHART__CONFIGURE_COMMAND_BUTTONS."""
    assert (
        ConfigureCommandButtons.Meta.effect_type
        == EffectType.PATIENT_CHART__CONFIGURE_COMMAND_BUTTONS
    )


def test_location_enum_values() -> None:
    """Location enum must have the expected string values."""
    assert Location.CONDITIONS.value == "conditions"
    assert Location.MEDICATIONS.value == "medications"
    assert Location.ALLERGIES.value == "allergies"
    assert Location.IMMUNIZATIONS.value == "immunizations"
    assert Location.SURGICAL_HISTORY.value == "surgical_history"
    assert Location.FAMILY_HISTORY.value == "family_history"
    assert Location.QUALITY_PROTOCOLS.value == "quality_protocols"
    assert Location.LAB_REVIEWS.value == "lab_reviews"
    assert Location.IMAGING_REVIEWS.value == "imaging_reviews"
    assert Location.REFERRAL_REVIEWS.value == "referral_reviews"
    assert Location.DOCUMENT_REVIEWS.value == "document_reviews"


def test_visibility_enum_values() -> None:
    """Visibility enum must have visible, hidden, and disabled values."""
    assert Visibility.VISIBLE.value == "visible"
    assert Visibility.HIDDEN.value == "hidden"
    assert Visibility.DISABLED.value == "disabled"


def test_location_config_stores_location_and_visibility() -> None:
    """LocationConfig must store its location and visibility."""
    config = LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN)
    assert config.location == Location.CONDITIONS
    assert config.visibility == Visibility.HIDDEN


def test_empty_locations_produces_empty_list() -> None:
    """An empty locations list must serialize to an empty areas list."""
    effect = ConfigureCommandButtons(patient_id="patient-id", locations=[])
    assert effect.values == {"patient_id": "patient-id", "locations": []}


def test_single_hidden_location_payload() -> None:
    """A single hidden location must serialize correctly."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN)],
    )
    assert effect.values == {
        "patient_id": "patient-id",
        "locations": [{"location": "conditions", "visibility": "hidden"}],
    }


def test_multiple_locations_preserve_order() -> None:
    """Multiple locations must serialize in declaration order."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.MEDICATIONS, visibility=Visibility.DISABLED),
            LocationConfig(location=Location.ALLERGIES, visibility=Visibility.VISIBLE),
        ],
    )
    assert effect.values == {
        "patient_id": "patient-id",
        "locations": [
            {"location": "conditions", "visibility": "hidden"},
            {"location": "medications", "visibility": "disabled"},
            {"location": "allergies", "visibility": "visible"},
        ],
    }


def test_no_errors_for_valid_locations() -> None:
    """_get_error_details returns no errors when all locations are unique."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.MEDICATIONS, visibility=Visibility.DISABLED),
        ],
    )
    assert effect._get_error_details(method=None) == []


def test_duplicate_location_reported_in_error_details() -> None:
    """_get_error_details returns an error when the same location appears twice."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.DISABLED),
        ],
    )
    errors = effect._get_error_details(method=None)
    assert len(errors) == 1


def test_multiple_duplicate_locations_each_reported() -> None:
    """_get_error_details reports one error per duplicate location."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.DISABLED),
            LocationConfig(location=Location.MEDICATIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.MEDICATIONS, visibility=Visibility.VISIBLE),
        ],
    )
    errors = effect._get_error_details(method=None)
    assert len(errors) == 2


def test_duplicate_location_raises_on_apply() -> None:
    """apply() must raise a ValidationError when duplicate locations are present."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.HIDDEN),
            LocationConfig(location=Location.CONDITIONS, visibility=Visibility.DISABLED),
        ],
    )
    with pytest.raises(ValidationError, match="Duplicate location"):
        effect.apply()


def test_apply_wraps_payload_under_data_key() -> None:
    """apply() must wrap the values under a 'data' key in the JSON payload."""
    effect = ConfigureCommandButtons(
        patient_id="patient-id",
        locations=[LocationConfig(location=Location.VITALS, visibility=Visibility.DISABLED)],
    )
    payload = json.loads(effect.apply().payload)
    assert payload == {
        "data": {
            "patient_id": "patient-id",
            "locations": [{"location": "vitals", "visibility": "disabled"}],
        }
    }
