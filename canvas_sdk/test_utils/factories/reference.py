import factory

from canvas_sdk.v1.data import Reference


class ReferenceFactory(factory.django.DjangoModelFactory[Reference]):
    """Factory for creating a Reference."""

    class Meta:
        model = Reference

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    name = factory.Sequence(lambda n: f"Reference {n}")
