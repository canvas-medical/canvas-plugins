import factory

from canvas_sdk.v1.data import PrescriptionChangeResponse


class PrescriptionChangeResponseFactory(
    factory.django.DjangoModelFactory[PrescriptionChangeResponse]
):
    """Factory for creating a PrescriptionChangeResponse."""

    class Meta:
        model = PrescriptionChangeResponse

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    response_type = "A"
    status = "open"
