import factory

from canvas_sdk.v1.data import HistoryOfPresentIllness


class HistoryOfPresentIllnessFactory(factory.django.DjangoModelFactory[HistoryOfPresentIllness]):
    """Factory for creating HistoryOfPresentIllness."""

    class Meta:
        model = HistoryOfPresentIllness

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    legacy_narrative = factory.Faker("paragraph")
