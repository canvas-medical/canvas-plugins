"""Tests for the Staff SDK data classes (StaffMetadata, StaffExternalIdentifier)."""

import datetime
from unittest.mock import patch

import pytest

from canvas_sdk.v1.data.staff import Staff, StaffExternalIdentifier, StaffMetadata


def test_signature_url_with_signature() -> None:
    """signature_url returns a presigned URL when signature is set."""
    staff = Staff()
    staff.signature = "signatures/staff_abc.png"

    with patch(
        "canvas_sdk.v1.data.staff.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert staff.signature_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("signatures/staff_abc.png")


def test_signature_url_returns_none_when_empty() -> None:
    """signature_url returns None when signature is empty."""
    staff = Staff()
    staff.signature = ""

    assert staff.signature_url is None


def test_signature_url_returns_none_when_null() -> None:
    """signature_url returns None when signature is None."""
    staff = Staff()
    staff.signature = None

    assert staff.signature_url is None


@pytest.mark.django_db
def test_staff_metadata_supports_large_values() -> None:
    """StaffMetadata.value can store and retrieve up to 1000 characters."""
    large_value = "a" * 1000
    metadata = StaffMetadata.objects.create(key="test_key", value=large_value)

    metadata.refresh_from_db()

    assert metadata.value == large_value
    assert len(metadata.value) == 1000


@pytest.mark.django_db
def test_staff_metadata_round_trip() -> None:
    """StaffMetadata persists and re-fetches key/value as expected."""
    metadata = StaffMetadata.objects.create(key="department", value="cardiology")

    metadata.refresh_from_db()

    assert metadata.key == "department"
    assert metadata.value == "cardiology"


@pytest.mark.django_db
def test_staff_external_identifier_round_trip() -> None:
    """StaffExternalIdentifier persists FHIR-like fields end-to-end."""
    identifier = StaffExternalIdentifier.objects.create(
        use="official",
        identifier_type="urn:oid:1.2.3",
        system="urn:oid:hr-system",
        value="employee-123",
        issued_date=datetime.date(2024, 1, 1),
        expiration_date=datetime.date(2034, 1, 1),
    )

    identifier.refresh_from_db()

    assert identifier.use == "official"
    assert identifier.value == "employee-123"
    assert identifier.system == "urn:oid:hr-system"
    assert identifier.issued_date == datetime.date(2024, 1, 1)
    assert identifier.expiration_date == datetime.date(2034, 1, 1)
