from canvas_sdk.effects.patient.create_patient_external_identifier import (
    CreatePatientExternalIdentifier,
)


def test_create_sets_delay_seconds() -> None:
    """create(delay_seconds=60) should set the field on the Effect."""
    effect = CreatePatientExternalIdentifier(value="12345", system="MRN").create(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_create_without_delay_seconds() -> None:
    """create() without delay_seconds should not set the field."""
    effect = CreatePatientExternalIdentifier(value="12345", system="MRN").create()
    assert not effect.HasField("delay_seconds")
