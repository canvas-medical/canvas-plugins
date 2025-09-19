import factory

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    MedicationFactory,
    NoteFactory,
    PatientFactory,
)
from canvas_sdk.v1.data.stop_medication_event import StopMedicationEvent


class StopMedicationEventFactory(factory.django.DjangoModelFactory):
    """Factory for creating a StopMedicationEvent."""

    class Meta:
        model = StopMedicationEvent

    patient = factory.SubFactory(PatientFactory)
    note = factory.SubFactory(NoteFactory)
    medication = factory.SubFactory(MedicationFactory)
    entered_in_error = factory.SubFactory(CanvasUserFactory)
    committer = factory.SubFactory(CanvasUserFactory)
    originator = factory.SubFactory(CanvasUserFactory)
    rationale = factory.Faker("sentence")
