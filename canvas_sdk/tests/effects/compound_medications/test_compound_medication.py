import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.compound_medications.compound_medication import CompoundMedication
from canvas_sdk.v1.data.compound_medication import CompoundMedication as CompoundMedicationModel


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with patch(
        "canvas_sdk.v1.data.compound_medication.CompoundMedication.objects"
    ) as mock_compound_med:
        # Setup default behaviors
        mock_compound_med.filter.return_value.exists.return_value = True

        yield {
            "compound_medication": mock_compound_med,
        }


@pytest.fixture
def valid_compound_medication_data() -> dict[str, Any]:
    """Valid data for creating a CompoundMedication."""
    return {
        "formulation": "Test Formulation",
        "potency_unit_code": CompoundMedicationModel.PotencyUnits.TABLET,
        "controlled_substance": CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        "controlled_substance_ndc": "",
        "active": True,
    }


@pytest.fixture
def valid_scheduled_compound_medication_data() -> dict[str, Any]:
    """Valid data for creating a scheduled CompoundMedication."""
    return {
        "formulation": "Scheduled Formulation",
        "potency_unit_code": CompoundMedicationModel.PotencyUnits.CAPSULE,
        "controlled_substance": CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        "controlled_substance_ndc": "12345-678-90",
        "active": True,
    }


def test_create_compound_medication_success(
    mock_db_queries: dict[str, MagicMock], valid_compound_medication_data: dict[str, Any]
) -> None:
    """Test successful compound medication creation."""
    compound_med = CompoundMedication(**valid_compound_medication_data)
    effect = compound_med.create()

    assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION
    payload = json.loads(effect.payload)
    assert payload["data"]["formulation"] == "Test Formulation"
    assert payload["data"]["potency_unit_code"] == CompoundMedicationModel.PotencyUnits.TABLET
    assert (
        payload["data"]["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED
    )
    assert payload["data"]["controlled_substance_ndc"] == ""
    assert payload["data"]["active"] is True


def test_create_compound_medication_with_scheduled_substance(
    mock_db_queries: dict[str, MagicMock], valid_scheduled_compound_medication_data: dict[str, Any]
) -> None:
    """Test creating compound medication with scheduled substance."""
    compound_med = CompoundMedication(**valid_scheduled_compound_medication_data)
    effect = compound_med.create()

    assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION
    payload = json.loads(effect.payload)
    assert payload["data"]["formulation"] == "Scheduled Formulation"
    assert (
        payload["data"]["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II
    )
    # NDC should have dashes removed
    assert payload["data"]["controlled_substance_ndc"] == "1234567890"


def test_create_compound_medication_missing_required_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test compound medication creation with missing required fields."""
    compound_med = CompoundMedication()

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'formulation' is required to create a compound medication." in error_fields
    assert "Field 'potency_unit_code' is required to create a compound medication." in error_fields
    assert (
        "Field 'controlled_substance' is required to create a compound medication." in error_fields
    )


def test_create_compound_medication_defaults_active_to_true(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that active defaults to True when not specified."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )
    effect = compound_med.create()

    payload = json.loads(effect.payload)
    assert payload["data"]["active"] is True


def test_create_compound_medication_formulation_validation(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test formulation validation rules."""
    # Test empty formulation
    compound_med = CompoundMedication(
        formulation="",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("Field 'formulation' cannot be empty" in str(e) for e in errors)

    # Test formulation too long (over 105 characters)
    long_formulation = "A" * 106
    compound_med = CompoundMedication(
        formulation=long_formulation,
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("Field 'formulation' must be 105 characters or less" in str(e) for e in errors)


def test_create_compound_medication_strips_formulation_whitespace(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that formulation whitespace is stripped."""
    compound_med = CompoundMedication(
        formulation="  Test Formulation  ",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )
    effect = compound_med.create()

    payload = json.loads(effect.payload)
    assert payload["data"]["formulation"] == "Test Formulation"


def test_create_compound_medication_invalid_potency_unit(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test validation of invalid potency unit code."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code="INVALID_CODE",
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("Invalid potency unit code" in str(e) for e in errors)


def test_create_compound_medication_invalid_controlled_substance(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test validation of invalid controlled substance."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance="INVALID_SCHEDULE",
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("Invalid controlled substance" in str(e) for e in errors)


def test_create_compound_medication_ndc_required_for_scheduled(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that NDC is required for scheduled substances."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="",  # Empty NDC
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("NDC is required when a Controlled Substance is specified" in str(e) for e in errors)


def test_create_compound_medication_ndc_not_required_for_unscheduled(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that NDC is not required for unscheduled substances."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    # Should not raise validation error
    effect = compound_med.create()
    assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION


def test_create_compound_medication_ndc_cleaning(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that NDC dashes are removed."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="12345-678-90",
    )
    effect = compound_med.create()

    payload = json.loads(effect.payload)
    assert payload["data"]["controlled_substance_ndc"] == "1234567890"


def test_update_compound_medication_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful compound medication update."""
    compound_med = CompoundMedication(instance_id=str(uuid4()))
    compound_med.formulation = "Updated Formulation"
    compound_med.active = False

    effect = compound_med.update()

    assert effect.type == EffectType.UPDATE_COMPOUND_MEDICATION
    payload = json.loads(effect.payload)
    assert payload["data"]["formulation"] == "Updated Formulation"
    assert payload["data"]["active"] is False
    assert "instance_id" in payload["data"]


def test_update_compound_medication_missing_instance_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update without instance_id raises error."""
    compound_med = CompoundMedication()
    compound_med.formulation = "Updated Formulation"

    with pytest.raises(ValidationError) as exc_info:
        compound_med.update()

    errors = exc_info.value.errors()
    assert any("Field 'instance_id' is required to update" in str(e) for e in errors)


def test_update_compound_medication_nonexistent_instance(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test updating compound medication that doesn't exist."""
    mock_db_queries["compound_medication"].filter.return_value.exists.return_value = False

    compound_med = CompoundMedication(instance_id=str(uuid4()))
    compound_med.formulation = "Updated Formulation"

    with pytest.raises(ValidationError) as exc_info:
        compound_med.update()

    errors = exc_info.value.errors()
    assert any(
        "Compound medication with ID" in str(e) and "does not exist" in str(e) for e in errors
    )


def test_update_compound_medication_partial_update(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating only some fields."""
    compound_med = CompoundMedication(instance_id=str(uuid4()))
    compound_med.formulation = "Only formulation updated"

    effect = compound_med.update()
    payload = json.loads(effect.payload)

    # Should only contain instance_id and formulation
    assert set(payload["data"].keys()) == {"instance_id", "formulation"}
    assert payload["data"]["formulation"] == "Only formulation updated"


def test_update_compound_medication_ndc_validation(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test NDC validation during update."""
    compound_med = CompoundMedication(instance_id=str(uuid4()))
    compound_med.controlled_substance = (
        CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II
    )
    compound_med.controlled_substance_ndc = ""  # Empty NDC

    with pytest.raises(ValidationError) as exc_info:
        compound_med.update()

    errors = exc_info.value.errors()
    assert any("NDC is required when a Controlled Substance is specified" in str(e) for e in errors)


def test_all_potency_units_valid(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that all defined potency units are valid."""
    for potency_unit_code, _ in CompoundMedicationModel.PotencyUnits.choices:
        compound_med = CompoundMedication(
            formulation="Test Formulation",
            potency_unit_code=potency_unit_code,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        )

        # Should not raise validation error
        effect = compound_med.create()
        assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION


def test_all_controlled_substances_valid(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that all defined controlled substances are valid."""
    for controlled_substance, _ in CompoundMedicationModel.ControlledSubstanceOptions.choices:
        ndc = "12345-678-90" if controlled_substance != "N" else ""

        compound_med = CompoundMedication(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=controlled_substance,
            controlled_substance_ndc=ndc,
        )

        # Should not raise validation error
        effect = compound_med.create()
        assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION


def test_compound_medication_values_property(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the values property returns correct data."""
    compound_med = CompoundMedication(
        formulation="  Test Formulation  ",  # With whitespace
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="12345-678-90",  # With dashes
        active=True,
    )

    values = compound_med.values
    assert values["formulation"] == "Test Formulation"  # Stripped
    assert values["controlled_substance_ndc"] == "1234567890"  # Dashes removed
    assert values["potency_unit_code"] == CompoundMedicationModel.PotencyUnits.TABLET
    assert (
        values["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II
    )
    assert values["active"] is True


def test_compound_medication_values_property_none_values(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that None values are excluded from values property."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        # controlled_substance_ndc is None
        # active is None
    )

    values = compound_med.values
    assert "controlled_substance_ndc" not in values
    assert "active" not in values
    assert len(values) == 3  # Only formulation, potency_unit_code, controlled_substance


def test_compound_medication_multiple_validation_errors(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that multiple validation errors are collected and reported together."""
    compound_med = CompoundMedication(
        formulation="",  # Empty formulation
        potency_unit_code="INVALID_CODE",  # Invalid potency unit
        controlled_substance="INVALID_SCHEDULE",  # Invalid controlled substance
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert len(errors) == 5  # Five validation errors

    error_messages = [e["msg"] for e in errors]
    assert any(
        "Field 'formulation' is required to create a compound medication" in msg
        for msg in error_messages
    )
    assert any("Field 'formulation' cannot be empty" in msg for msg in error_messages)
    assert any("Invalid potency unit code" in msg for msg in error_messages)
    assert any("Invalid controlled substance" in msg for msg in error_messages)
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_compound_medication_whitespace_only_formulation(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that whitespace-only formulation fails validation."""
    compound_med = CompoundMedication(
        formulation="   ",  # Only whitespace
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("Field 'formulation' cannot be empty" in str(e) for e in errors)


def test_compound_medication_edge_case_formulation_length(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test formulation at exactly 105 characters (boundary case)."""
    formulation_105 = "A" * 105
    compound_med = CompoundMedication(
        formulation=formulation_105,
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
    )

    # Should not raise validation error
    effect = compound_med.create()
    assert effect.type == EffectType.CREATE_COMPOUND_MEDICATION

    payload = json.loads(effect.payload)
    assert payload["data"]["formulation"] == formulation_105


def test_compound_medication_ndc_whitespace_validation(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that whitespace-only NDC fails validation for scheduled substances."""
    compound_med = CompoundMedication(
        formulation="Test Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="   ",  # Only whitespace
    )

    with pytest.raises(ValidationError) as exc_info:
        compound_med.create()

    errors = exc_info.value.errors()
    assert any("NDC is required when a Controlled Substance is specified" in str(e) for e in errors)
