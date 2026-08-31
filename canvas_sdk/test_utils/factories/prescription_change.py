import factory

from canvas_sdk.v1.data import PrescriptionChangeRequest, PrescriptionChangeResponse


class PrescriptionChangeRequestFactory(
    factory.django.DjangoModelFactory[PrescriptionChangeRequest]
):
    """Factory for creating a PrescriptionChangeRequest."""

    class Meta:
        model = PrescriptionChangeRequest

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    type_code = "G"


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
    request = factory.SubFactory(
        PrescriptionChangeRequestFactory,
        patient=factory.SelfAttribute("..patient"),
    )
    response_type = "A"
    status = "open"
