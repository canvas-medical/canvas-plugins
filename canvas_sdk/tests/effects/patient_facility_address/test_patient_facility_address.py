import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.patient_facility_address.patient_facility_address import (
    AddressType,
    PatientFacilityAddress,
)


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock], None, None]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch(
            "canvas_sdk.effects.patient_facility_address.patient_facility_address.Patient.objects"
        ) as mock_patient,
        patch(
            "canvas_sdk.effects.patient_facility_address.patient_facility_address.Facility.objects"
        ) as mock_facility,
        patch(
            "canvas_sdk.effects.patient_facility_address.patient_facility_address.PatientFacilityAddressModel.objects"
        ) as mock_address,
    ):
        mock_patient.filter.return_value.exists.return_value = True
        mock_facility.filter.return_value.exists.return_value = True
        mock_address.filter.return_value.exists.return_value = True

        yield {
            "patient": mock_patient,
            "facility": mock_facility,
            "address": mock_address,
        }


@pytest.fixture
def valid_create_with_facility_id() -> dict[str, Any]:
    """Valid data for creating with existing facility."""
    return {
        "patient_id": "patient-123",
        "facility_id": "facility-456",
    }


@pytest.fixture
def valid_create_with_new_facility() -> dict[str, Any]:
    """Valid data for creating with new facility inline."""
    return {
        "patient_id": "patient-123",
        "facility_name": "Test Clinic",
        "facility_city": "Boston",
        "facility_state_code": "MA",
        "facility_postal_code": "02101",
    }


@pytest.fixture
def valid_create_with_all_fields() -> dict[str, Any]:
    """Valid data with all optional fields for new facility."""
    return {
        "patient_id": "patient-123",
        "facility_name": "Complete Test Clinic",
        "facility_npi_number": "1234567890",
        "facility_phone_number": "5551234567",
        "facility_fax_number": "5559876543",
        "facility_active": True,
        "facility_line1": "123 Main St",
        "facility_line2": "Suite 100",
        "facility_city": "Boston",
        "facility_district": "Suffolk",
        "facility_state_code": "MA",
        "facility_postal_code": "02101",
        "room_number": "101A",
        "address_type": AddressType.PHYSICAL,
    }


# =============================================================================
# Create Tests - With Existing Facility
# =============================================================================


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_create_with_facility_id_success(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create() with existing facility generates correct effect."""
    address = PatientFacilityAddress(**valid_create_with_facility_id)

    address.create()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_PATIENT_FACILITY_ADDRESS"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["facility_id"] == "facility-456"


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_create_with_facility_id_and_optional_fields(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create() with facility_id includes optional fields."""
    address = PatientFacilityAddress(
        **valid_create_with_facility_id,
        room_number="202B",
        address_type=AddressType.BOTH,
    )

    address.create()

    payload_data = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload_data["data"]["room_number"] == "202B"
    assert payload_data["data"]["address_type"] == "both"


# =============================================================================
# Create Tests - With New Facility
# =============================================================================


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_create_with_new_facility_success(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_new_facility: dict[str, Any],
) -> None:
    """Test create() with new facility generates correct effect."""
    address = PatientFacilityAddress(**valid_create_with_new_facility)

    address.create()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_PATIENT_FACILITY_ADDRESS"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["facility_name"] == "Test Clinic"
    assert payload_data["data"]["facility_city"] == "Boston"
    assert payload_data["data"]["facility_state_code"] == "MA"
    assert payload_data["data"]["facility_postal_code"] == "02101"
    assert "facility_id" not in payload_data["data"]


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_create_with_all_facility_fields(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_all_fields: dict[str, Any],
) -> None:
    """Test create() with all facility fields includes them in payload."""
    address = PatientFacilityAddress(**valid_create_with_all_fields)

    address.create()

    payload_data = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload_data["data"]["facility_name"] == "Complete Test Clinic"
    assert payload_data["data"]["facility_npi_number"] == "1234567890"
    assert payload_data["data"]["facility_phone_number"] == "5551234567"
    assert payload_data["data"]["facility_fax_number"] == "5559876543"
    assert payload_data["data"]["facility_active"] is True
    assert payload_data["data"]["facility_line1"] == "123 Main St"
    assert payload_data["data"]["facility_line2"] == "Suite 100"
    assert payload_data["data"]["facility_city"] == "Boston"
    assert payload_data["data"]["facility_district"] == "Suffolk"
    assert payload_data["data"]["facility_state_code"] == "MA"
    assert payload_data["data"]["facility_postal_code"] == "02101"
    assert payload_data["data"]["room_number"] == "101A"
    assert payload_data["data"]["address_type"] == "physical"


# =============================================================================
# Create Validation Tests
# =============================================================================


def test_create_fails_with_id_set(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create validation fails when id is provided."""
    address = PatientFacilityAddress(
        id="address-123",
        **valid_create_with_facility_id,
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_without_patient_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when patient_id is missing."""
    address = PatientFacilityAddress(
        facility_id="facility-456",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_without_facility(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when neither facility_id nor facility fields provided."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_both_facility_id_and_creation_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when both facility_id and creation fields provided."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
        facility_id="facility-456",
        facility_name="Test Clinic",
        facility_city="Boston",
        facility_state_code="MA",
        facility_postal_code="02101",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_nonexistent_patient(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create validation fails when patient doesn't exist."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False

    address = PatientFacilityAddress(**valid_create_with_facility_id)

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_nonexistent_facility(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create validation fails when facility doesn't exist."""
    mock_db_queries["facility"].filter.return_value.exists.return_value = False

    address = PatientFacilityAddress(**valid_create_with_facility_id)

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_missing_facility_name(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when facility_name is missing for new facility."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
        facility_city="Boston",
        facility_state_code="MA",
        facility_postal_code="02101",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_missing_facility_city(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when facility_city is missing for new facility."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
        facility_name="Test Clinic",
        facility_state_code="MA",
        facility_postal_code="02101",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_missing_facility_state_code(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when facility_state_code is missing for new facility."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
        facility_name="Test Clinic",
        facility_city="Boston",
        facility_postal_code="02101",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_missing_facility_postal_code(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create validation fails when facility_postal_code is missing for new facility."""
    address = PatientFacilityAddress(
        patient_id="patient-123",
        facility_name="Test Clinic",
        facility_city="Boston",
        facility_state_code="MA",
    )

    with pytest.raises(ValidationError):
        address.create()


def test_create_fails_with_invalid_address_type(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test create validation fails when address_type is invalid."""
    with pytest.raises(ValidationError):
        address = PatientFacilityAddress(
            **valid_create_with_facility_id,
            address_type="invalid",  # type: ignore[arg-type]
        )
        address.create()


# =============================================================================
# Update Tests
# =============================================================================


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_update_success(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update() generates correct effect."""
    address = PatientFacilityAddress(
        id="address-123",
        room_number="999",
    )

    address.update()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "UPDATE_PATIENT_FACILITY_ADDRESS"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["id"] == "address-123"
    assert payload_data["data"]["room_number"] == "999"


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_update_with_existing_facility(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update() with existing facility."""
    address = PatientFacilityAddress(
        id="address-123",
        facility_id="new-facility-789",
    )

    address.update()

    payload_data = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload_data["data"]["facility_id"] == "new-facility-789"


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_update_with_new_facility(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update() with new facility inline."""
    address = PatientFacilityAddress(
        id="address-123",
        facility_name="New Clinic",
        facility_city="Cambridge",
        facility_state_code="MA",
        facility_postal_code="02139",
    )

    address.update()

    payload_data = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload_data["data"]["facility_name"] == "New Clinic"
    assert payload_data["data"]["facility_city"] == "Cambridge"


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_update_only_includes_dirty_fields(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update() only includes fields that were set."""
    address = PatientFacilityAddress(
        id="address-123",
        room_number="404D",
    )

    address.update()

    payload_data = json.loads(mock_effect.call_args.kwargs["payload"])
    assert payload_data["data"]["id"] == "address-123"
    assert payload_data["data"]["room_number"] == "404D"
    assert "patient_id" not in payload_data["data"]
    assert "facility_id" not in payload_data["data"]
    assert "address_type" not in payload_data["data"]


# =============================================================================
# Update Validation Tests
# =============================================================================


def test_update_fails_without_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when id is missing."""
    address = PatientFacilityAddress(
        room_number="101A",
    )

    with pytest.raises(ValidationError):
        address.update()


def test_update_fails_with_nonexistent_address(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when address doesn't exist."""
    mock_db_queries["address"].filter.return_value.exists.return_value = False

    address = PatientFacilityAddress(
        id="nonexistent-address",
        room_number="101A",
    )

    with pytest.raises(ValidationError):
        address.update()


def test_update_fails_with_nonexistent_facility(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when new facility doesn't exist."""
    mock_db_queries["facility"].filter.return_value.exists.return_value = False

    address = PatientFacilityAddress(
        id="address-123",
        facility_id="nonexistent-facility",
    )

    with pytest.raises(ValidationError):
        address.update()


def test_update_fails_with_both_facility_id_and_creation_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when both facility_id and creation fields provided."""
    address = PatientFacilityAddress(
        id="address-123",
        facility_id="facility-456",
        facility_name="Test Clinic",
        facility_city="Boston",
        facility_state_code="MA",
        facility_postal_code="02101",
    )

    with pytest.raises(ValidationError):
        address.update()


def test_update_fails_with_invalid_address_type(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when address_type is invalid."""
    with pytest.raises(ValidationError):
        address = PatientFacilityAddress(
            id="address-123",
            address_type="invalid",  # type: ignore[arg-type]
        )
        address.update()


def test_update_fails_with_incomplete_facility_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test update validation fails when facility creation fields are incomplete."""
    address = PatientFacilityAddress(
        id="address-123",
        facility_name="Test Clinic",
        # Missing city, state_code, postal_code
    )

    with pytest.raises(ValidationError):
        address.update()


# =============================================================================
# Delete Tests
# =============================================================================


@patch("canvas_sdk.effects.patient_facility_address.patient_facility_address.Effect")
def test_delete_success(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test delete() generates correct effect."""
    address = PatientFacilityAddress(
        id="address-123",
    )

    address.delete()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "DELETE_PATIENT_FACILITY_ADDRESS"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["id"] == "address-123"


def test_delete_fails_without_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test delete validation fails when id is missing."""
    address = PatientFacilityAddress()

    with pytest.raises(ValidationError):
        address.delete()


def test_delete_fails_with_nonexistent_address(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test delete validation fails when address doesn't exist."""
    mock_db_queries["address"].filter.return_value.exists.return_value = False

    address = PatientFacilityAddress(
        id="nonexistent-address",
    )

    with pytest.raises(ValidationError):
        address.delete()


# =============================================================================
# Values Tests
# =============================================================================


def test_values_includes_facility_id_fields(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
) -> None:
    """Test values includes facility_id when set."""
    address = PatientFacilityAddress(**valid_create_with_facility_id)
    values = address.values

    assert "patient_id" in values
    assert "facility_id" in values
    assert "facility_name" not in values


def test_values_includes_facility_creation_fields(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_all_fields: dict[str, Any],
) -> None:
    """Test values includes all facility creation fields when set."""
    address = PatientFacilityAddress(**valid_create_with_all_fields)
    values = address.values

    assert "patient_id" in values
    assert "facility_name" in values
    assert "facility_city" in values
    assert "facility_state_code" in values
    assert "facility_postal_code" in values
    assert "facility_line1" in values
    assert "facility_line2" in values
    assert "facility_npi_number" in values
    assert "room_number" in values
    assert "address_type" in values
    assert "facility_id" not in values


def test_values_excludes_unset_fields(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_new_facility: dict[str, Any],
) -> None:
    """Test values excludes fields that were not set."""
    address = PatientFacilityAddress(**valid_create_with_new_facility)
    values = address.values

    assert "room_number" not in values
    assert "address_type" not in values
    assert "facility_line1" not in values
    assert "facility_npi_number" not in values


# =============================================================================
# Meta Class Tests
# =============================================================================


def test_effect_type_is_patient_facility_address() -> None:
    """Test Meta.effect_type is set correctly."""
    assert PatientFacilityAddress.Meta.effect_type == "PATIENT_FACILITY_ADDRESS"


# =============================================================================
# Address Type Tests
# =============================================================================


def test_address_type_enum_values() -> None:
    """Test AddressType enum has correct values."""
    assert AddressType.PHYSICAL.value == "physical"
    assert AddressType.BOTH.value == "both"


@pytest.mark.parametrize(
    "address_type_value", [AddressType.PHYSICAL, "physical"], ids=["enum", "string"]
)
def test_address_type_physical_is_valid(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
    address_type_value: AddressType,
) -> None:
    """Test 'physical' address type is valid."""
    address = PatientFacilityAddress(
        **valid_create_with_facility_id,
        address_type=address_type_value,
    )
    errors = address._get_error_details("create")
    assert not any("address_type" in str(e) for e in errors)


@pytest.mark.parametrize("address_type_value", [AddressType.BOTH, "both"], ids=["enum", "string"])
def test_address_type_both_is_valid(
    mock_db_queries: dict[str, MagicMock],
    valid_create_with_facility_id: dict[str, Any],
    address_type_value: AddressType,
) -> None:
    """Test 'both' address type is valid."""
    address = PatientFacilityAddress(
        **valid_create_with_facility_id,
        address_type=address_type_value,
    )
    errors = address._get_error_details("create")
    assert not any("address_type" in str(e) for e in errors)


# =============================================================================
# UUID Tests
# =============================================================================


def test_id_accepts_string() -> None:
    """Test id accepts a string."""
    address = PatientFacilityAddress(
        id="abc-123-def",
    )
    assert address.id == "abc-123-def"


def test_id_accepts_uuid() -> None:
    """Test id accepts a UUID."""
    from uuid import UUID

    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    address = PatientFacilityAddress(
        id=uuid_val,
    )
    assert address.id == uuid_val


def test_patient_id_accepts_uuid() -> None:
    """Test patient_id accepts a UUID."""
    from uuid import UUID

    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    address = PatientFacilityAddress(
        patient_id=uuid_val,
    )
    assert address.patient_id == uuid_val


def test_facility_id_accepts_uuid() -> None:
    """Test facility_id accepts a UUID."""
    from uuid import UUID

    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    address = PatientFacilityAddress(
        facility_id=uuid_val,
    )
    assert address.facility_id == uuid_val


# =============================================================================
# Helper Method Tests
# =============================================================================


def test_has_facility_creation_fields_true_with_name() -> None:
    """Test _has_facility_creation_fields returns True when facility_name is set."""
    address = PatientFacilityAddress(facility_name="Test")
    assert address._has_facility_creation_fields() is True


def test_has_facility_creation_fields_true_with_city() -> None:
    """Test _has_facility_creation_fields returns True when facility_city is set."""
    address = PatientFacilityAddress(facility_city="Boston")
    assert address._has_facility_creation_fields() is True


def test_has_facility_creation_fields_false_when_none() -> None:
    """Test _has_facility_creation_fields returns False when no facility fields set."""
    address = PatientFacilityAddress(patient_id="patient-123")
    assert address._has_facility_creation_fields() is False


def test_has_facility_creation_fields_false_with_only_optional() -> None:
    """Test _has_facility_creation_fields returns False with only optional facility fields."""
    address = PatientFacilityAddress(
        facility_line1="123 Main St",
        facility_npi_number="1234567890",
    )
    assert address._has_facility_creation_fields() is False
