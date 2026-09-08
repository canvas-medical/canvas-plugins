import factory

from canvas_sdk.v1.data import ResolveConditionEvent


class ResolveConditionEventFactory(factory.django.DjangoModelFactory[ResolveConditionEvent]):
    """Factory for creating a ResolveConditionEvent."""

    class Meta:
        model = ResolveConditionEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    rationale = factory.Faker("sentence")
