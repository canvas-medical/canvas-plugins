from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.effects.patient.base import PatientPreferredPharmacy
from canvas_sdk.effects.patient.create_patient_preferred_pharmacies import (
    CreatePatientPreferredPharmacies,
)


@pytest.fixture
def mock_patient_exists() -> Generator[MagicMock]:
    """MockPatientExists."""
    with patch(
        "canvas_sdk.effects.patient.create_patient_preferred_pharmacies.Patient.objects"
    ) as mock:
        mock.filter.return_value.exists.return_value = True
        yield mock


def test_create_sets_delay_seconds(mock_patient_exists: MagicMock) -> None:
    """create(delay_seconds=60) should set the field on the Effect."""
    effect = CreatePatientPreferredPharmacies(
        patient_id="patient-123",
        pharmacies=[PatientPreferredPharmacy(ncpdp_id="1234567")],
    ).create(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_create_without_delay_seconds(mock_patient_exists: MagicMock) -> None:
    """create() without delay_seconds should not set the field."""
    effect = CreatePatientPreferredPharmacies(
        patient_id="patient-123",
        pharmacies=[PatientPreferredPharmacy(ncpdp_id="1234567")],
    ).create()
    assert not effect.HasField("delay_seconds")
