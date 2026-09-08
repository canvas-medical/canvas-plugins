import factory

from canvas_sdk.v1.data.plan import Plan


class PlanFactory(factory.django.DjangoModelFactory[Plan]):
    """Factory for creating a Plan."""

    class Meta:
        model = Plan

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    legacy_narrative = factory.Faker("text", max_nb_chars=500)
