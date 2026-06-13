import factory

from canvas_sdk.v1.data import ChartSectionReview


class ChartSectionReviewFactory(factory.django.DjangoModelFactory[ChartSectionReview]):
    """Factory for creating ChartSectionReview."""

    class Meta:
        model = ChartSectionReview

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
