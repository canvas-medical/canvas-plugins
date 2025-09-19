import factory

from canvas_sdk.test_utils.factories import CanvasUserFactory, PatientFactory
from canvas_sdk.v1.data import Medication


class MedicationFactory(factory.django.DjangoModelFactory):
    """Factory for creating a Medication."""

    class Meta:
        model = Medication

    patient = factory.SubFactory(PatientFactory)
    deleted = False
    entered_in_error = factory.SubFactory(CanvasUserFactory)
    committer = factory.SubFactory(CanvasUserFactory)
    status = "active"
    start_date = factory.Faker("date_time_this_decade")
    end_date = factory.Faker("date_time_this_decade")
