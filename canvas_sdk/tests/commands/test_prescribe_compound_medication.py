import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.prescribe import CompoundMedicationData, PrescribeCommand
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
def valid_regular_prescription_data() -> dict[str, Any]:
    """Valid data for creating a regular prescription."""
    return {
        "note_uuid": str(uuid4()),
        "fdb_code": "123456",
        "sig": "Take one tablet by mouth daily",
        "days_supply": 30,
        "quantity_to_dispense": 30,
        "refills": 5,
    }


@pytest.fixture
def valid_compound_medication_prescription_data() -> dict[str, Any]:
    """Valid data for creating a compound medication prescription."""
    return {
        "note_uuid": str(uuid4()),
        "compound_medication_data": CompoundMedicationData(
            formulation="Test Compound Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
            controlled_substance_ndc="",
            active=True,
        ),
        "sig": "Take one tablet by mouth daily",
        "days_supply": 30,
        "quantity_to_dispense": 30,
        "refills": 5,
    }


@pytest.fixture
def valid_scheduled_compound_medication_prescription_data() -> dict[str, Any]:
    """Valid data for creating a scheduled compound medication prescription."""
    return {
        "note_uuid": str(uuid4()),
        "compound_medication_data": CompoundMedicationData(
            formulation="Scheduled Compound Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.CAPSULE,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
            controlled_substance_ndc="12345-678-90",
            active=True,
        ),
        "sig": "Take one capsule by mouth daily",
        "days_supply": 30,
        "quantity_to_dispense": 30,
        "refills": 0,  # Scheduled substances typically have no refills
    }


@pytest.fixture
def valid_existing_compound_medication_prescription_data() -> dict[str, Any]:
    """Valid data for creating a prescription with an existing compound medication."""
    return {
        "note_uuid": str(uuid4()),
        "compound_medication_id": str(uuid4()),
        "sig": "Take one tablet by mouth daily",
        "days_supply": 30,
        "quantity_to_dispense": 30,
        "refills": 2,
    }


def test_prescribe_regular_medication_success(
    mock_db_queries: dict[str, MagicMock], valid_regular_prescription_data: dict[str, Any]
) -> None:
    """Test successful regular medication prescription."""
    prescribe_cmd = PrescribeCommand(**valid_regular_prescription_data)
    effect = prescribe_cmd.originate()

    assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND
    payload = json.loads(effect.payload)
    assert payload["data"]["fdb_code"] == "123456"
    assert payload["data"]["sig"] == "Take one tablet by mouth daily"
    assert "compound_medication_formulation" not in payload["data"]


def test_prescribe_compound_medication_success(
    mock_db_queries: dict[str, MagicMock],
    valid_compound_medication_prescription_data: dict[str, Any],
) -> None:
    """Test successful compound medication prescription."""
    prescribe_cmd = PrescribeCommand(**valid_compound_medication_prescription_data)
    effect = prescribe_cmd.originate()

    assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND
    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["formulation"] == "Test Compound Formulation"
    assert compound_med_data["potency_unit_code"] == CompoundMedicationModel.PotencyUnits.TABLET
    assert (
        compound_med_data["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED
    )
    assert compound_med_data["controlled_substance_ndc"] == ""
    assert compound_med_data["active"] is True
    assert "fdb_code" not in payload["data"]


def test_prescribe_scheduled_compound_medication_success(
    mock_db_queries: dict[str, MagicMock],
    valid_scheduled_compound_medication_prescription_data: dict[str, Any],
) -> None:
    """Test successful scheduled compound medication prescription."""
    prescribe_cmd = PrescribeCommand(**valid_scheduled_compound_medication_prescription_data)
    effect = prescribe_cmd.originate()

    assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND
    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["formulation"] == "Scheduled Compound Formulation"
    assert (
        compound_med_data["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II
    )
    # NDC should have dashes removed
    assert compound_med_data["controlled_substance_ndc"] == "1234567890"


def test_prescribe_existing_compound_medication_success(
    mock_db_queries: dict[str, MagicMock],
    valid_existing_compound_medication_prescription_data: dict[str, Any],
) -> None:
    """Test successful prescription with existing compound medication."""
    prescribe_cmd = PrescribeCommand(**valid_existing_compound_medication_prescription_data)
    effect = prescribe_cmd.originate()

    assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND
    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert (
        compound_med_data["id"]
        == valid_existing_compound_medication_prescription_data["compound_medication_id"]
    )
    assert payload["data"]["sig"] == "Take one tablet by mouth daily"
    assert "compound_medication_formulation" not in payload["data"]
    assert "fdb_code" not in payload["data"]


def test_prescribe_multiple_medication_types(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that prescription fails when multiple medication types are provided."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        fdb_code="123456",
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any("Cannot specify multiple medication types" in msg for msg in error_messages)


def test_prescribe_compound_medication_formulation_too_long(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test compound medication prescription with formulation too long."""
    long_formulation = "A" * 106
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation=long_formulation,
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any(
        "Field 'formulation' must be 105 characters or less" in msg for msg in error_messages
    )


def test_prescribe_compound_medication_strips_formulation_whitespace(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that formulation whitespace is stripped."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="  Test Formulation  ",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )
    effect = prescribe_cmd.originate()

    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["formulation"] == "Test Formulation"


def test_prescribe_compound_medication_invalid_potency_unit(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test compound medication prescription with invalid potency unit."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code="INVALID_CODE",
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any("Invalid potency unit code" in msg for msg in error_messages)


def test_prescribe_compound_medication_invalid_controlled_substance(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test compound medication prescription with invalid controlled substance."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance="INVALID_SCHEDULE",
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any("Invalid controlled substance" in msg for msg in error_messages)


def test_prescribe_compound_medication_ndc_required_for_scheduled(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that NDC is required for scheduled substances."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
            controlled_substance_ndc="",
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_prescribe_compound_medication_ndc_cleaning(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that NDC dashes are removed."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
            controlled_substance_ndc="12345-678-90",
        ),
        sig="Take one tablet by mouth daily",
    )
    effect = prescribe_cmd.originate()

    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["controlled_substance_ndc"] == "1234567890"


def test_prescribe_compound_medication_values_property(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the values property returns correct data for compound medications."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="  Test Formulation  ",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
            controlled_substance_ndc="12345-678-90",
        ),
        sig="Take one tablet by mouth daily",
    )

    values = prescribe_cmd.values
    assert "compound_medication_values" in values
    compound_med_values = values["compound_medication_values"]
    assert compound_med_values["formulation"] == "  Test Formulation  "  # Raw unprocessed data
    assert compound_med_values["controlled_substance_ndc"] == "12345-678-90"  # Raw unprocessed data
    assert compound_med_values["potency_unit_code"] == CompoundMedicationModel.PotencyUnits.TABLET
    assert (
        compound_med_values["controlled_substance"]
        == CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II
    )
    assert compound_med_values["active"] is True


def test_prescribe_compound_medication_values_property_is_ommitted_if_fdb_code_is_present(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the values property does not return data for compound medications when an fdb_code is provided."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        fdb_code="abc123",
        sig="Take one tablet by mouth daily",
    )

    values = prescribe_cmd.values
    assert "compound_medication_values" not in values
    assert values["fdb_code"] == "abc123"


def test_prescribe_compound_medication_edit_command(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test editing a compound medication prescription."""
    prescribe_cmd = PrescribeCommand(
        command_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Updated Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
            controlled_substance_ndc="12345-678-90",
        ),
        sig="Take two tablets by mouth daily",
    )
    effect = prescribe_cmd.edit()

    assert effect.type == EffectType.EDIT_PRESCRIBE_COMMAND
    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["formulation"] == "Updated Formulation"
    assert payload["data"]["sig"] == "Take two tablets by mouth daily"


def test_prescribe_compound_medication_multiple_validation_errors(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that multiple validation errors are collected and reported together."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="",
            potency_unit_code="INVALID_CODE",
            controlled_substance="INVALID_SCHEDULE",
            controlled_substance_ndc="",
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    assert len(errors) == 4  # Five validation errors

    error_messages = [e["msg"] for e in errors]
    assert any("Field 'formulation' cannot be empty" in msg for msg in error_messages)
    assert any("Invalid potency unit code" in msg for msg in error_messages)
    assert any("Invalid controlled substance" in msg for msg in error_messages)
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_prescribe_compound_medication_all_potency_units_valid(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that all defined potency units are valid."""
    for potency_unit_code, _ in CompoundMedicationModel.PotencyUnits.choices:
        prescribe_cmd = PrescribeCommand(
            note_uuid=str(uuid4()),
            compound_medication_data=CompoundMedicationData(
                formulation="Test Formulation",
                potency_unit_code=potency_unit_code,
                controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
            ),
            sig="Take one tablet by mouth daily",
        )

        # Should not raise validation error
        effect = prescribe_cmd.originate()
        assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND


def test_prescribe_compound_medication_all_controlled_substances_valid(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that all defined controlled substances are valid."""
    for controlled_substance, _ in CompoundMedicationModel.ControlledSubstanceOptions.choices:
        ndc = "12345-678-90" if controlled_substance != "N" else ""

        prescribe_cmd = PrescribeCommand(
            note_uuid=str(uuid4()),
            compound_medication_data=CompoundMedicationData(
                formulation="Test Formulation",
                potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
                controlled_substance=controlled_substance,
                controlled_substance_ndc=ndc,
            ),
            sig="Take one tablet by mouth daily",
        )

        # Should not raise validation error
        effect = prescribe_cmd.originate()
        assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND


def test_prescribe_compound_medication_edge_case_formulation_length(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test formulation at exactly 105 characters (boundary case)."""
    formulation_105 = "A" * 105
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation=formulation_105,
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )

    # Should not raise validation error
    effect = prescribe_cmd.originate()
    assert effect.type == EffectType.ORIGINATE_PRESCRIBE_COMMAND

    payload = json.loads(effect.payload)
    assert "compound_medication_values" in payload["data"]
    compound_med_data = payload["data"]["compound_medication_values"]
    assert compound_med_data["formulation"] == formulation_105


def test_prescribe_compound_medication_ndc_whitespace_validation(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that whitespace-only NDC fails validation for scheduled substances."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
            controlled_substance_ndc="   ",  # Only whitespace
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_prescribe_existing_compound_medication_nonexistent_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that prescription fails when compound medication ID doesn't exist."""
    mock_db_queries["compound_medication"].filter.return_value.exists.return_value = False

    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_id=str(uuid4()),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any(
        "Compound medication with ID" in msg and "does not exist" in msg for msg in error_messages
    )


def test_prescribe_fdb_code_and_compound_medication_id_conflict(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that prescription fails when both fdb_code and compound_medication_id are provided."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        fdb_code="123456",
        compound_medication_id=str(uuid4()),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any("Cannot specify multiple medication types" in msg for msg in error_messages)


def test_prescribe_compound_medication_id_and_formulation_conflict(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that prescription fails when both compound_medication_id and formulation are provided."""
    prescribe_cmd = PrescribeCommand(
        note_uuid=str(uuid4()),
        compound_medication_id=str(uuid4()),
        compound_medication_data=CompoundMedicationData(
            formulation="Test Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        ),
        sig="Take one tablet by mouth daily",
    )

    with pytest.raises(ValidationError) as exc_info:
        prescribe_cmd.originate()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]
    assert any("Cannot specify multiple medication types" in msg for msg in error_messages)
