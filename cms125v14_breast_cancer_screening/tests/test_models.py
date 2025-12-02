from cms125v14_breast_cancer_screening.protocols.cms125v14_protocol import (
    ClinicalQualityMeasure125v14,
)

from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data.discount import Discount


def test_protocol_event_configuration() -> None:
    """Test that the protocol is configured to respond to multiple events."""
    # Check that PATIENT_UPDATED is in the list of events
    assert EventType.Name(EventType.PATIENT_UPDATED) in ClinicalQualityMeasure125v14.RESPONDS_TO
    # Check that CONDITION_CREATED is in the list of events
    assert EventType.Name(EventType.CONDITION_CREATED) in ClinicalQualityMeasure125v14.RESPONDS_TO


def test_factory_example() -> None:
    """Test that a patient can be created using the PatientFactory."""
    patient = PatientFactory.create()
    assert patient.id is not None


def test_model_example() -> None:
    """Test that a Discount instance can be created."""
    Discount.objects.create(name="10%", adjustment_group="30", adjustment_code="CO", discount=0.10)
    discount = Discount.objects.first()
    assert discount is not None
    assert discount.pk is not None
