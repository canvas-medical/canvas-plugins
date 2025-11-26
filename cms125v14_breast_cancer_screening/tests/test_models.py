from unittest.mock import Mock

from cms125v14_breast_cancer_screening.protocols.cms125v14_protocol import (
    ClinicalQualityMeasure125v14,
)

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data.discount import Discount


def test_protocol_responds_to_assess_command() -> None:
    """Test that the protocol responds correctly to ASSESS_COMMAND__CONDITION_SELECTED events."""
    mock_event = Mock()
    mock_event.type = EventType.ASSESS_COMMAND__CONDITION_SELECTED
    mock_event.context = {
        "note": {
            "uuid": "test-note-uuid-123",
        }
    }

    protocol = ClinicalQualityMeasure125v14(event=mock_event)

    effects = protocol.compute()

    assert len(effects) == 1

    assert effects[0].type == EffectType.LOG

    assert "test-note-uuid-123" in effects[0].payload
    assert protocol.NARRATIVE_STRING in effects[0].payload


def test_protocol_event_configuration() -> None:
    """Test that the protocol is configured to respond to the correct event type."""
    assert (
        EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
        == ClinicalQualityMeasure125v14.RESPONDS_TO
    )


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
