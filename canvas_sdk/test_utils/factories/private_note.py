import factory

from canvas_sdk.v1.data import PrivateNote


class PrivateNoteFactory(factory.django.DjangoModelFactory[PrivateNote]):
    """Factory for creating a PrivateNote."""

    class Meta:
        model = PrivateNote

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
