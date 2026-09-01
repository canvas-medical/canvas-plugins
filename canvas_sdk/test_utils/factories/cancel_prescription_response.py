import factory

from canvas_sdk.v1.data import CancelPrescriptionResponse


class CancelPrescriptionResponseFactory(
    factory.django.DjangoModelFactory[CancelPrescriptionResponse]
):
    """Factory for creating a CancelPrescriptionResponse."""

    class Meta:
        model = CancelPrescriptionResponse

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    request = factory.SubFactory("canvas_sdk.test_utils.factories.CancelPrescriptionFactory")
    message_id = factory.Sequence(lambda n: f"cancel-resp-{n}")
