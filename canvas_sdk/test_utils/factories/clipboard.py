import factory

from canvas_sdk.v1.data import Clipboard


class ClipboardFactory(factory.django.DjangoModelFactory[Clipboard]):
    """Factory for creating a Clipboard."""

    class Meta:
        model = Clipboard

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    text = factory.Faker("paragraph")
