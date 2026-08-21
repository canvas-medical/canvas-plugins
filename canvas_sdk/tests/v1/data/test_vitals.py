import pytest
from django.db import models

from canvas_sdk.test_utils.factories import VitalSignFactory
from canvas_sdk.v1.data.vitals import VitalSign, VitalSignReading


def test_vital_sign_reading_has_patient_note_and_date() -> None:
    """VitalSignReading carries the patient/note FKs and date_recorded."""
    assert VitalSignReading._meta.get_field("patient") is not None
    assert VitalSignReading._meta.get_field("note") is not None
    assert isinstance(VitalSignReading._meta.get_field("date_recorded"), models.DateTimeField)


def test_vital_sign_measurement_fields() -> None:
    """VitalSign exposes the measurement fields (loinc/sign/value/units/source)."""
    for name in ("loinc_num", "sign", "value", "units", "source"):
        assert isinstance(VitalSign._meta.get_field(name), models.CharField)


def test_vital_sign_links_back_via_signs() -> None:
    """VitalSign links to VitalSignReading with a `signs` reverse accessor."""
    accessor = VitalSign._meta.get_field("reading").remote_field.get_accessor_name()
    assert accessor == "signs"
    assert hasattr(VitalSignReading, "signs")


@pytest.mark.django_db
def test_vital_sign_factory_builds_with_reading() -> None:
    """The SDK VitalSignFactory creates a VitalSign reachable via its reading's `signs`."""
    sign = VitalSignFactory.create(value="120/80", units="mmHg")
    assert sign.value == "120/80"
    assert sign.reading.patient_id is not None
    assert list(sign.reading.signs.all()) == [sign]
