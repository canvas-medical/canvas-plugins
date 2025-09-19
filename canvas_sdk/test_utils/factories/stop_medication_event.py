import factory

from canvas_sdk.v1.data.stop_medication_event import StopMedicationEvent


class StopMedicationEventFactory(factory.django.DjangoModelFactory):
    """Factory for creating a StopMedicationEvent."""

    class Meta:
        model = StopMedicationEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    medication = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    entered_in_error = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    committer = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    rationale = factory.Faker("sentence")
