import factory
from django.utils import timezone

from canvas_sdk.v1.data import Appointment, AppointmentReminder
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus, AppointmentReminderStatus


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


class AppointmentReminderFactory(factory.django.DjangoModelFactory[AppointmentReminder]):
    """Factory for creating an AppointmentReminder, by default a text message that was sent."""

    class Meta:
        model = AppointmentReminder

    dbid = factory.Faker("uuid4", cast_to=None)
    id = factory.SelfAttribute("dbid")
    appointment = factory.SubFactory(AppointmentFactory)
    phone_number = "5555550100"
    email = None
    status = AppointmentReminderStatus.SENT
