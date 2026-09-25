import factory

from canvas_sdk.v1.data import CustomCommand


class CustomCommandFactory(factory.django.DjangoModelFactory[CustomCommand]):
    """Factory for creating a CustomCommand."""

    class Meta:
        model = CustomCommand

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
