import factory

from canvas_sdk.v1.data import Coverage


class CoverageFactory(factory.django.DjangoModelFactory[Coverage]):
    """Factory for creating a Coverage."""

    class Meta:
        model = Coverage

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    plan = "Healthy Families of California"
    group = "San Francisco Mail Carriers"
    coverage_rank = 1
    id_number = "1098659867"
    coverage_start_date = factory.Faker("date")
