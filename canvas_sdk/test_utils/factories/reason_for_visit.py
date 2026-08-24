import factory

from canvas_sdk.v1.data import ReasonForVisit


class ReasonForVisitFactory(factory.django.DjangoModelFactory[ReasonForVisit]):
    """Factory for creating a ReasonForVisit."""

    class Meta:
        model = ReasonForVisit

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    legacy_narrative = factory.Faker("paragraph")
