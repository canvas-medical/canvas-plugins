import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.observation.base import (
    CodingData,
    Observation,
    ObservationComponentData,
)


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with patch("canvas_sdk.effects.observation.base.ObservationModel.objects") as mock_obs:
        # Setup default behaviors - objects exist
        mock_obs.filter.return_value.exists.return_value = True

        yield {
            "observation": mock_obs,
        }


@pytest.fixture
def valid_observation_data() -> dict[str, Any]:
    """Valid data for creating an Observation."""
    return {
        "patient_id": "patient-123",
        "name": "Blood Pressure",
        "category": "vital-signs",
        "value": "120/80",
        "units": "mmHg",
        "note_id": 456,
        "effective_datetime": datetime.datetime(2024, 1, 15, 10, 30, 0),
    }


@pytest.fixture
def observation_coding() -> CodingData:
    """Create a CodingData for testing."""
    return CodingData(
        code="85354-9",
        display="Blood pressure panel",
        system="http://loinc.org",
        version="2.73",
        user_selected=True,
    )


@pytest.fixture
def observation_component() -> ObservationComponentData:
    """Create an ObservationComponentData for testing."""
    return ObservationComponentData(
        value_quantity="120",
        value_quantity_unit="mmHg",
        name="Systolic Blood Pressure",
    )


@pytest.fixture
def observation_value_coding() -> CodingData:
    """Create a CodingData for testing."""
    return CodingData(
        code="normal",
        display="Normal",
        system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
    )


def test_observation_coding_to_dict_with_all_fields(
    observation_coding: CodingData,
) -> None:
    """Test CodingData.to_dict() with all fields populated."""
    result = observation_coding.to_dict()

    assert result == {
        "code": "85354-9",
        "display": "Blood pressure panel",
        "system": "http://loinc.org",
        "version": "2.73",
        "user_selected": True,
    }


def test_observation_coding_to_dict_minimal_fields() -> None:
    """Test CodingData.to_dict() with only required fields."""
    coding = CodingData(
        code="test-code",
        display="Test Display",
        system="http://test.system",
    )
    result = coding.to_dict()

    assert result == {
        "code": "test-code",
        "display": "Test Display",
        "system": "http://test.system",
        "version": "",
        "user_selected": False,
    }


def test_observation_component_to_dict(observation_component: ObservationComponentData) -> None:
    """Test ObservationComponentData.to_dict() method."""
    result = observation_component.to_dict()

    assert result == {
        "value_quantity": "120",
        "value_quantity_unit": "mmHg",
        "name": "Systolic Blood Pressure",
        "codings": None,
    }


def test_observation_component_to_dict_with_codings() -> None:
    """Test ObservationComponentData.to_dict() with codings."""
    component = ObservationComponentData(
        value_quantity="80",
        value_quantity_unit="mmHg",
        name="Diastolic Blood Pressure",
        codings=[
            CodingData(
                code="8462-4",
                display="Diastolic blood pressure",
                system="http://loinc.org",
            )
        ],
    )
    result = component.to_dict()

    assert result == {
        "value_quantity": "80",
        "value_quantity_unit": "mmHg",
        "name": "Diastolic Blood Pressure",
        "codings": [
            {
                "code": "8462-4",
                "display": "Diastolic blood pressure",
                "system": "http://loinc.org",
                "version": "",
                "user_selected": False,
            }
        ],
    }


def test_observation_value_coding_to_dict(
    observation_value_coding: CodingData,
) -> None:
    """Test CodingData.to_dict() method."""
    result = observation_value_coding.to_dict()

    assert result == {
        "code": "normal",
        "display": "Normal",
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "version": "",
        "user_selected": False,
    }


def test_observation_values_includes_codings_when_set(
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
    observation_coding: CodingData,
) -> None:
    """Test that values includes codings when they are provided."""
    observation = Observation(**valid_observation_data, codings=[observation_coding])
    values = observation.values

    assert "codings" in values
    assert values["codings"] == [observation_coding.to_dict()]


def test_observation_values_includes_components_when_set(
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
    observation_component: ObservationComponentData,
) -> None:
    """Test that values includes components when they are provided."""
    observation = Observation(**valid_observation_data, components=[observation_component])
    values = observation.values

    assert "components" in values
    assert values["components"] == [observation_component.to_dict()]


def test_observation_values_includes_value_codings_when_set(
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
    observation_value_coding: CodingData,
) -> None:
    """Test that values includes value_codings when they are provided."""
    observation = Observation(**valid_observation_data, value_codings=[observation_value_coding])
    values = observation.values

    assert "value_codings" in values
    assert values["value_codings"] == [observation_value_coding.to_dict()]


def test_observation_values_excludes_collections_when_not_dirty(
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
) -> None:
    """Test that values excludes collections that are not marked as dirty."""
    observation = Observation(**valid_observation_data)
    values = observation.values

    assert "codings" not in values or observation.is_dirty("codings")
    assert "components" not in values or observation.is_dirty("components")
    assert "value_codings" not in values or observation.is_dirty("value_codings")


def test_observation_values_handles_none_collections(
    mock_db_queries: dict[str, MagicMock], valid_observation_data: dict[str, Any]
) -> None:
    """Test that values handles None collections properly."""
    observation = Observation(
        **valid_observation_data, codings=None, components=None, value_codings=None
    )
    values = observation.values

    if "codings" in values:
        assert values["codings"] is None
    if "components" in values:
        assert values["components"] is None
    if "value_codings" in values:
        assert values["value_codings"] is None


def test_observation_create_validation_with_observation_id_error(
    mock_db_queries: dict[str, MagicMock], valid_observation_data: dict[str, Any]
) -> None:
    """Test that create validation fails when observation_id is provided."""
    observation = Observation(observation_id="obs-123", **valid_observation_data)

    with pytest.raises(ValidationError):
        observation.create()


def test_observation_create_validation_requires_patient_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that create validation fails when patient_id is missing."""
    observation = Observation(
        name="Test Observation",
        effective_datetime=datetime.datetime.now(),
        # Missing patient_id
    )

    with pytest.raises(ValidationError):
        observation.create()


def test_observation_create_validation_requires_name(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that create validation fails when name is missing."""
    observation = Observation(
        patient_id="patient-123",
        effective_datetime=datetime.datetime.now(),
        # Missing name
    )

    with pytest.raises(ValidationError):
        observation.create()


def test_observation_create_validation_requires_effective_datetime(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that create validation fails when effective_datetime is missing."""
    observation = Observation(
        patient_id="patient-123",
        name="Test Observation",
        # Missing effective_datetime
    )

    with pytest.raises(ValidationError):
        observation.create()


def test_observation_update_validation_missing_observation_id(
    mock_db_queries: dict[str, MagicMock], valid_observation_data: dict[str, Any]
) -> None:
    """Test that update validation fails when observation_id is missing."""
    observation = Observation(**valid_observation_data)

    with pytest.raises(ValidationError):
        observation.update()


def test_observation_update_validation_nonexistent_observation(
    mock_db_queries: dict[str, MagicMock], valid_observation_data: dict[str, Any]
) -> None:
    """Test that update validation fails when observation doesn't exist."""
    # Mock observation not existing
    mock_db_queries["observation"].filter.return_value.exists.return_value = False

    observation = Observation(observation_id="nonexistent", **valid_observation_data)

    with pytest.raises(ValidationError):
        observation.update()


def test_observation_validation_invalid_parent_observation(
    mock_db_queries: dict[str, MagicMock], valid_observation_data: dict[str, Any]
) -> None:
    """Test validation fails when is_member_of_id doesn't exist."""

    def mock_exists(id: str) -> bool:
        # Make the parent observation not exist
        return id != "invalid_parent"

    mock_db_queries["observation"].filter.return_value.exists.side_effect = lambda: mock_exists(
        "invalid_parent"
    )

    observation = Observation(is_member_of_id="invalid_parent", **valid_observation_data)

    with pytest.raises(ValidationError):
        observation.create()


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_create_effect(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
) -> None:
    """Test that create() generates correct effect."""
    observation = Observation(**valid_observation_data)

    observation.create()

    # Verify Effect was called with correct type and payload
    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_OBSERVATION"

    # Test the payload data
    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["name"] == "Blood Pressure"
    assert payload_data["data"]["category"] == "vital-signs"
    assert payload_data["data"]["value"] == "120/80"
    assert payload_data["data"]["units"] == "mmHg"
    assert payload_data["data"]["note_id"] == 456
    assert payload_data["data"]["effective_datetime"] == "2024-01-15T10:30:00"


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_update_effect(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
) -> None:
    """Test that update() generates correct effect."""
    observation = Observation(observation_id="obs-123", **valid_observation_data)

    observation.update()

    # Verify Effect was called with correct type and payload
    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "UPDATE_OBSERVATION"

    # Test the payload data
    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["observation_id"] == "obs-123"
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["name"] == "Blood Pressure"


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_update_effect_partial_data(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update() only includes dirty fields."""
    observation = Observation(
        observation_id="obs-123",
        value="125/85",  # Only updating value
    )

    observation.update()

    # Verify Effect was called with correct type and payload
    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "UPDATE_OBSERVATION"

    # Test the payload data - should only include dirty fields
    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["observation_id"] == "obs-123"
    assert payload_data["data"]["value"] == "125/85"
    # These should not be in the payload since they weren't set
    assert "patient_id" not in payload_data["data"]
    assert "name" not in payload_data["data"]


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_create_with_complex_data(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    observation_coding: CodingData,
    observation_component: ObservationComponentData,
    observation_value_coding: CodingData,
) -> None:
    """Test creating observation with codings, components, and value_codings."""
    observation = Observation(
        patient_id="patient-456",
        name="Complete Blood Count",
        category="laboratory",
        value="Normal",
        units="",
        note_id=789,
        effective_datetime=datetime.datetime(2024, 1, 20, 14, 0, 0),
        codings=[observation_coding],
        components=[observation_component],
        value_codings=[observation_value_coding],
    )

    observation.create()

    # Verify Effect was called with correct type and payload
    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_OBSERVATION"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-456"
    assert payload_data["data"]["name"] == "Complete Blood Count"
    assert len(payload_data["data"]["codings"]) == 1
    assert len(payload_data["data"]["components"]) == 1
    assert len(payload_data["data"]["value_codings"]) == 1
    assert payload_data["data"]["codings"][0]["code"] == "85354-9"
    assert payload_data["data"]["components"][0]["name"] == "Systolic Blood Pressure"
    assert payload_data["data"]["value_codings"][0]["code"] == "normal"


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_validation_all_valid_references(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
) -> None:
    """Test validation passes when all foreign key references exist."""
    observation = Observation(
        observation_id="obs-123",
        is_member_of_id="parent-obs-456",
        **valid_observation_data,
    )

    # Should not raise validation error
    observation.update()
    # Just check that it was called without error
    mock_effect.assert_called_once()


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_update_validation_allows_optional_fields(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update validation allows optional fields."""
    observation = Observation(
        observation_id="obs-123",
        category="updated-category",
        # All other fields are optional for updates
    )

    # Should not raise validation error
    observation.update()
    mock_effect.assert_called_once()


@patch("canvas_sdk.effects.observation.base.Effect")
def test_observation_create_with_member_of(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_observation_data: dict[str, Any],
) -> None:
    """Test creating an observation as a member of another observation."""
    observation = Observation(
        **valid_observation_data,
        is_member_of_id="parent-obs-123",
    )

    observation.create()

    # Verify Effect was called with correct type and payload
    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_OBSERVATION"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["is_member_of_id"] == "parent-obs-123"
