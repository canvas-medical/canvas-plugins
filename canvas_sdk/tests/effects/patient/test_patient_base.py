import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.patient.base import (
    Patient,
    PatientAddress,
    PatientContactPoint,
    PatientExternalIdentifier,
)
from canvas_sdk.v1.data.common import (
    AddressType,
    AddressUse,
    ContactPointSystem,
    ContactPointUse,
    PersonSex,
)


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.patient.base.PatientModel.objects") as mock_patient,
        patch("canvas_sdk.effects.patient.base.PracticeLocation.objects") as mock_location,
        patch("canvas_sdk.effects.patient.base.Staff.objects") as mock_staff,
    ):
        # Setup default behaviors - objects exist
        mock_patient.filter.return_value.exists.return_value = True
        mock_location.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True

        yield {
            "patient": mock_patient,
            "location": mock_location,
            "staff": mock_staff,
        }


@pytest.fixture
def valid_patient_data() -> dict[str, Any]:
    """Valid data for creating a Patient."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "birthdate": datetime.date(1990, 1, 1),
        "sex_at_birth": PersonSex.SEX_MALE,
    }


@pytest.fixture
def patient_address() -> PatientAddress:
    """Create a PatientAddress for testing."""
    return PatientAddress(
        line1="123 Main St",
        line2="Apt 4B",
        country="US",
        city="New York",
        state_code="NY",
        postal_code="10001",
    )


@pytest.fixture
def patient_contact_point() -> PatientContactPoint:
    """Create a PatientContactPoint for testing."""
    return PatientContactPoint(
        system=ContactPointSystem.PHONE, value="555-1234", use=ContactPointUse.HOME, rank=1
    )


def test_patient_address_to_dict_with_all_fields(patient_address: PatientAddress) -> None:
    """Test PatientAddress.to_dict() with all fields populated."""
    result = patient_address.to_dict()

    assert result == {
        "line1": "123 Main St",
        "line2": "Apt 4B",
        "country": "US",
        "use": AddressUse.HOME.value,
        "type": AddressType.BOTH.value,
        "city": "New York",
        "district": None,
        "state_code": "NY",
        "postal_code": "10001",
        "longitude": None,
        "latitude": None,
    }


def test_patient_address_to_dict_minimal_fields() -> None:
    """Test PatientAddress.to_dict() with only required fields."""
    address = PatientAddress(line1="456 Oak Ave", country="CA")
    result = address.to_dict()

    assert result == {
        "line1": "456 Oak Ave",
        "line2": None,
        "country": "CA",
        "use": AddressUse.HOME.value,
        "type": AddressType.BOTH.value,
        "city": None,
        "district": None,
        "state_code": None,
        "postal_code": None,
        "longitude": None,
        "latitude": None,
    }


def test_patient_contact_point_to_dict(patient_contact_point: PatientContactPoint) -> None:
    """Test PatientContactPoint.to_dict() method."""
    result = patient_contact_point.to_dict()

    assert result == {
        "system": ContactPointSystem.PHONE.value,
        "value": "555-1234",
        "use": ContactPointUse.HOME.value,
        "rank": 1,
        "has_consent": None,
    }


def test_patient_external_identifier_to_dict() -> None:
    """Test PatientExternalIdentifier.to_dict() method."""
    identifier = PatientExternalIdentifier(system="MRN", value="12345")
    result = identifier.to_dict()

    assert result == {
        "system": "MRN",
        "value": "12345",
    }


def test_patient_values_includes_contact_points_when_set(
    mock_db_queries: dict[str, MagicMock],
    valid_patient_data: dict[str, Any],
    patient_contact_point: PatientContactPoint,
) -> None:
    """Test that values includes contact_points when they are provided."""
    patient = Patient(**valid_patient_data, contact_points=[patient_contact_point])
    values = patient.values

    assert "contact_points" in values
    assert values["contact_points"] == [patient_contact_point.to_dict()]


def test_patient_values_includes_addresses_when_set(
    mock_db_queries: dict[str, MagicMock],
    valid_patient_data: dict[str, Any],
    patient_address: PatientAddress,
) -> None:
    """Test that values includes addresses when they are provided."""
    patient = Patient(**valid_patient_data, addresses=[patient_address])
    values = patient.values

    assert "addresses" in values
    assert values["addresses"] == [patient_address.to_dict()]


def test_patient_values_excludes_collections_when_not_dirty(
    mock_db_queries: dict[str, MagicMock],
    valid_patient_data: dict[str, Any],
    patient_contact_point: PatientContactPoint,
) -> None:
    """Test that values excludes collections that are not marked as dirty."""
    patient = Patient(**valid_patient_data)
    values = patient.values

    assert "contact_points" not in values


def test_patient_values_handles_none_collections(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that values handles None collections properly."""
    patient = Patient(
        **valid_patient_data, contact_points=None, addresses=None, external_identifiers=None
    )
    values = patient.values

    assert values.get("contact_points") is None
    assert values.get("addresses") is None
    assert values.get("external_identifiers") is None


def test_patient_create_validation_with_patient_id_error(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that create validation fails when patient_id is provided."""
    patient = Patient(patient_id="123", **valid_patient_data)

    with pytest.raises(ValidationError) as exc_info:
        patient.create()

    errors = exc_info.value.errors()
    assert any("Patient ID should not be set when creating a new patient" in str(e) for e in errors)


def test_patient_update_validation_missing_patient_id(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that update validation fails when patient_id is missing."""
    patient = Patient(**valid_patient_data)

    with pytest.raises(ValidationError):
        patient.update()


def test_patient_update_validation_nonexistent_patient(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that update validation fails when patient doesn't exist."""
    # Mock patient not existing
    mock_db_queries["patient"].filter.return_value.exists.return_value = False

    patient = Patient(patient_id="nonexistent", **valid_patient_data)

    with pytest.raises(ValidationError):
        patient.update()


def test_patient_validation_invalid_location(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test validation fails when default_location_id doesn't exist."""
    # Mock location not existing
    mock_db_queries["location"].filter.return_value.exists.return_value = False

    patient = Patient(
        patient_id="123", default_location_id="invalid_location", **valid_patient_data
    )

    with pytest.raises(ValidationError):
        patient.update()


def test_patient_validation_invalid_provider(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test validation fails when default_provider_id doesn't exist."""
    # Mock provider not existing
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    patient = Patient(
        patient_id="123", default_provider_id="invalid_provider", **valid_patient_data
    )

    with pytest.raises(ValidationError):
        patient.update()


def test_patient_create_effect(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that create() generates correct effect."""
    patient = Patient(**valid_patient_data)

    effect = patient.create()

    # Test the payload data instead of effect type enum
    payload_data = json.loads(effect.payload)
    assert payload_data["data"]["first_name"] == "John"
    assert payload_data["data"]["last_name"] == "Doe"
    assert payload_data["data"]["birthdate"] == "1990-01-01"
    assert payload_data["data"]["sex_at_birth"] == PersonSex.SEX_MALE.value


def test_patient_update_effect(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that update() generates correct effect."""
    patient = Patient(patient_id="123", **valid_patient_data)

    effect = patient.update()

    # Test the payload data
    payload_data = json.loads(effect.payload)
    assert payload_data["data"]["first_name"] == "John"
    assert payload_data["data"]["last_name"] == "Doe"


def test_patient_create_with_complex_data(
    mock_db_queries: dict[str, MagicMock],
    patient_address: PatientAddress,
    patient_contact_point: PatientContactPoint,
) -> None:
    """Test creating patient with addresses and contact points."""
    external_identifier = PatientExternalIdentifier(system="MRN", value="12345")

    patient = Patient(
        first_name="Jane",
        last_name="Smith",
        addresses=[patient_address],
        contact_points=[patient_contact_point],
        external_identifiers=[external_identifier],
        previous_names=["Jane Johnson"],
    )

    effect = patient.create()

    payload_data = json.loads(effect.payload)
    assert payload_data["data"]["first_name"] == "Jane"
    assert payload_data["data"]["last_name"] == "Smith"
    assert len(payload_data["data"]["addresses"]) == 1
    assert len(payload_data["data"]["contact_points"]) == 1
    assert len(payload_data["data"]["external_identifiers"]) == 1
    assert payload_data["data"]["previous_names"] == ["Jane Johnson"]


def test_patient_validation_all_valid_references(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test validation passes when all foreign key references exist."""
    patient = Patient(
        patient_id="123",
        default_location_id="valid_location",
        default_provider_id="valid_provider",
        **valid_patient_data,
    )

    # Should not raise validation error
    effect = patient.update()
    # Just check that it returned an effect without error
    assert effect is not None


def test_patient_multiple_validation_errors(
    mock_db_queries: dict[str, MagicMock], valid_patient_data: dict[str, Any]
) -> None:
    """Test that multiple validation errors are collected together."""
    # Mock all foreign keys as not existing
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["location"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    patient = Patient(
        patient_id="nonexistent",
        default_location_id="invalid_location",
        default_provider_id="invalid_provider",
        **valid_patient_data,
    )

    with pytest.raises(ValidationError) as exc_info:
        patient.update()

    errors = exc_info.value.errors()
    assert len(errors) == 3  # Patient, location, and provider errors
