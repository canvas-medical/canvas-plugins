import factory

from canvas_sdk.v1.data import CancelPrescription


class CancelPrescriptionFactory(factory.django.DjangoModelFactory[CancelPrescription]):
    """Factory for creating a CancelPrescription."""

    class Meta:
        model = CancelPrescription

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    message_id = factory.Sequence(lambda n: f"cancel-{n}")
