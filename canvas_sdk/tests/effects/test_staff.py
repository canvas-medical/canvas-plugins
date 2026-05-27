"""Tests for the Staff metadata and external identifier effects."""

import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.staff import StaffExternalIdentifier
from canvas_sdk.effects.staff_metadata import StaffMetadata


@pytest.fixture
def mock_staff_exists() -> Generator[MagicMock]:
    """Mock the Staff existence check to return True by default."""
    with patch("canvas_sdk.effects.staff_metadata.base.Staff.objects") as mock_staff:
        mock_staff.filter.return_value.exists.return_value = True
        yield mock_staff


@pytest.fixture
def mock_external_id_targets() -> Generator[tuple[MagicMock, MagicMock]]:
    """Mock the Staff and StaffExternalIdentifier existence checks to return True."""
    with (
        patch("canvas_sdk.effects.staff.staff_external_identifier.Staff.objects") as mock_staff,
        patch(
            "canvas_sdk.effects.staff.staff_external_identifier.StaffExternalIdentifierModel.objects"
        ) as mock_identifier,
    ):
        mock_staff.filter.return_value.exists.return_value = True
        mock_identifier.filter.return_value.exists.return_value = True
        yield mock_staff, mock_identifier


def test_staff_external_identifier_create_serializes_payload(
    mock_external_id_targets: tuple[MagicMock, MagicMock],
) -> None:
    """StaffExternalIdentifier.create() should produce a properly typed Effect."""
    effect = StaffExternalIdentifier(
        value="employee-001", system="urn:oid:hr-system", staff_id="staff-key-1"
    ).create()

    assert effect.type == EffectType.CREATE_STAFF_EXTERNAL_IDENTIFIER

    payload = json.loads(effect.payload)

    assert payload == {
        "data": {
            "id": None,
            "value": "employee-001",
            "system": "urn:oid:hr-system",
            "staff_id": "staff-key-1",
        }
    }


def test_staff_external_identifier_create_requires_staff_id() -> None:
    """create() raises if staff_id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        StaffExternalIdentifier(value="employee-002").create()

    assert "'staff_id' is required" in str(exc_info.value)


def test_staff_external_identifier_update_serializes_payload(
    mock_external_id_targets: tuple[MagicMock, MagicMock],
) -> None:
    """StaffExternalIdentifier.update() should produce an UPDATE effect keyed by id."""
    effect = StaffExternalIdentifier(
        id="00000000-0000-0000-0000-000000000001",
        value="employee-005",
    ).update()

    assert effect.type == EffectType.UPDATE_STAFF_EXTERNAL_IDENTIFIER

    payload = json.loads(effect.payload)
    assert payload["data"]["id"] == "00000000-0000-0000-0000-000000000001"
    assert payload["data"]["value"] == "employee-005"


def test_staff_external_identifier_update_requires_id() -> None:
    """update() raises if id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        StaffExternalIdentifier(value="employee-006").update()

    assert "'id' is required to update" in str(exc_info.value)


def test_staff_external_identifier_delete_serializes_payload(
    mock_external_id_targets: tuple[MagicMock, MagicMock],
) -> None:
    """StaffExternalIdentifier.delete() should produce a DELETE effect with only id."""
    effect = StaffExternalIdentifier(id="00000000-0000-0000-0000-000000000002").delete()

    assert effect.type == EffectType.DELETE_STAFF_EXTERNAL_IDENTIFIER

    payload = json.loads(effect.payload)
    assert payload == {"data": {"id": "00000000-0000-0000-0000-000000000002"}}


def test_staff_external_identifier_delete_requires_id() -> None:
    """delete() raises if id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        StaffExternalIdentifier().delete()

    assert "'id' is required to delete" in str(exc_info.value)


def test_staff_external_identifier_create_rejects_id(
    mock_external_id_targets: tuple[MagicMock, MagicMock],
) -> None:
    """create() raises if id is set, since create assigns a new id."""
    with pytest.raises(ValidationError) as exc_info:
        StaffExternalIdentifier(
            id="00000000-0000-0000-0000-000000000099",
            value="employee-007",
            staff_id="staff-key-1",
        ).create()

    assert "ID should not be set when creating" in str(exc_info.value)


def test_staff_external_identifier_create_requires_value(
    mock_external_id_targets: tuple[MagicMock, MagicMock],
) -> None:
    """create() raises if value is missing."""
    with pytest.raises(ValidationError) as exc_info:
        StaffExternalIdentifier(staff_id="staff-key-1").create()

    assert "'value' is required" in str(exc_info.value)


def test_staff_external_identifier_create_validates_staff_exists() -> None:
    """create() raises when the referenced staff does not exist."""
    with patch("canvas_sdk.effects.staff.staff_external_identifier.Staff.objects") as mock_staff:
        mock_staff.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            StaffExternalIdentifier(value="employee-008", staff_id="missing-staff").create()

    assert "Staff with id: missing-staff does not exist." in str(exc_info.value)


def test_staff_external_identifier_update_validates_identifier_exists() -> None:
    """update() raises when no identifier matches the supplied id."""
    with patch(
        "canvas_sdk.effects.staff.staff_external_identifier.StaffExternalIdentifierModel.objects"
    ) as mock_identifier:
        mock_identifier.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            StaffExternalIdentifier(
                id="00000000-0000-0000-0000-000000000098", value="employee-009"
            ).update()

    assert "Staff external identifier with id:" in str(exc_info.value)


def test_staff_external_identifier_delete_validates_identifier_exists() -> None:
    """delete() raises when no identifier matches the supplied id."""
    with patch(
        "canvas_sdk.effects.staff.staff_external_identifier.StaffExternalIdentifierModel.objects"
    ) as mock_identifier:
        mock_identifier.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            StaffExternalIdentifier(id="00000000-0000-0000-0000-000000000097").delete()

    assert "Staff external identifier with id:" in str(exc_info.value)


def test_staff_metadata_upsert_serializes_payload(mock_staff_exists: MagicMock) -> None:
    """StaffMetadata(...).upsert(value) emits an UPSERT_STAFF_METADATA effect."""
    effect = StaffMetadata(staff_id="staff-key-1", key="department").upsert("cardiology")

    assert effect.type == EffectType.UPSERT_STAFF_METADATA

    payload = json.loads(effect.payload)

    assert payload["data"]["staff_id"] == "staff-key-1"
    assert payload["data"]["key"] == "department"
    assert payload["data"]["value"] == "cardiology"


def test_staff_metadata_delete_serializes_payload(mock_staff_exists: MagicMock) -> None:
    """StaffMetadata(...).delete() emits a DELETE_STAFF_METADATA effect keyed by (staff_id, key)."""
    effect = StaffMetadata(staff_id="staff-key-1", key="department").delete()

    assert effect.type == EffectType.DELETE_STAFF_METADATA

    payload = json.loads(effect.payload)
    assert payload["data"]["staff_id"] == "staff-key-1"
    assert payload["data"]["key"] == "department"


def test_staff_metadata_validates_staff_exists() -> None:
    """StaffMetadata.upsert raises ValidationError if the staff does not exist."""
    with patch("canvas_sdk.effects.staff_metadata.base.Staff.objects") as mock_staff:
        mock_staff.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            StaffMetadata(staff_id="missing-staff", key="department").upsert("cardiology")

    error_str = str(exc_info.value)
    assert "Staff with id: missing-staff does not exist." in error_str
