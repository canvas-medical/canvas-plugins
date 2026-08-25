import factory

from canvas_sdk.v1.data import RemoveAllergyEvent


class RemoveAllergyEventFactory(factory.django.DjangoModelFactory[RemoveAllergyEvent]):
    """Factory for creating a RemoveAllergyEvent."""

    class Meta:
        model = RemoveAllergyEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    rationale = factory.Faker("sentence")
