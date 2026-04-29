"""Tests for the Staff metadata and external identifier effects."""

import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.staff import CreateStaffExternalIdentifier
from canvas_sdk.effects.staff_metadata import StaffMetadata


@pytest.fixture
def mock_staff_exists() -> Generator[MagicMock]:
    """Mock the Staff existence check to return True by default."""
    with patch("canvas_sdk.effects.staff_metadata.base.Staff.objects") as mock_staff:
        mock_staff.filter.return_value.exists.return_value = True
        yield mock_staff


def test_create_staff_external_identifier_create_serializes_payload() -> None:
    """CreateStaffExternalIdentifier.create() should produce a properly typed Effect."""
    effect = CreateStaffExternalIdentifier(
        value="employee-001", system="urn:oid:hr-system", staff_id="staff-key-1"
    ).create()

    assert effect.type == "CREATE_STAFF_EXTERNAL_IDENTIFIER"

    payload = json.loads(effect.payload)

    assert payload == {
        "data": {
            "value": "employee-001",
            "system": "urn:oid:hr-system",
            "staff_id": "staff-key-1",
        }
    }


def test_create_staff_external_identifier_allows_optional_fields() -> None:
    """system and staff_id are optional on the effect dataclass."""
    effect = CreateStaffExternalIdentifier(value="employee-002").create()

    payload = json.loads(effect.payload)

    assert payload["data"]["value"] == "employee-002"
    assert payload["data"]["system"] is None
    assert payload["data"]["staff_id"] is None


def test_staff_metadata_upsert_serializes_payload(mock_staff_exists: MagicMock) -> None:
    """StaffMetadata(...).upsert(value) emits an UPSERT_STAFF_METADATA effect."""
    effect = StaffMetadata(staff_id="staff-key-1", key="department").upsert("cardiology")

    assert effect.type == "UPSERT_STAFF_METADATA"

    payload = json.loads(effect.payload)

    assert payload["data"]["staff_id"] == "staff-key-1"
    assert payload["data"]["key"] == "department"
    assert payload["data"]["value"] == "cardiology"


def test_staff_metadata_validates_staff_exists() -> None:
    """StaffMetadata.upsert raises ValidationError if the staff does not exist."""
    with patch("canvas_sdk.effects.staff_metadata.base.Staff.objects") as mock_staff:
        mock_staff.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            StaffMetadata(staff_id="missing-staff", key="department").upsert("cardiology")

    error_str = str(exc_info.value)
    assert "Staff with id: missing-staff does not exist." in error_str
