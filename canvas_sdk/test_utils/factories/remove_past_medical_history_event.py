import factory

from canvas_sdk.v1.data import RemovePastMedicalHistoryEvent


class RemovePastMedicalHistoryEventFactory(
    factory.django.DjangoModelFactory[RemovePastMedicalHistoryEvent]
):
    """Factory for creating a RemovePastMedicalHistoryEvent."""

    class Meta:
        model = RemovePastMedicalHistoryEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    rationale = factory.Faker("sentence")
