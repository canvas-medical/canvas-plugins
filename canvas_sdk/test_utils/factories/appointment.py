import factory
from django.utils import timezone

from canvas_sdk.v1.data import Appointment
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus


class AppointmentFactory(factory.django.DjangoModelFactory[Appointment]):
    """Factory for creating an Appointment."""

    class Meta:
        model = Appointment

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    start_time = factory.LazyFunction(timezone.now)
    duration_minutes = 30
    status = AppointmentProgressStatus.CONFIRMED
    telehealth_instructions_sent = False
