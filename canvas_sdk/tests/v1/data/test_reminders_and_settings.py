import pytest

from canvas_sdk.test_utils.factories import (
    AppointmentFactory,
    AppointmentReminderFactory,
    BusinessLineFactory,
    BusinessLineSettingFactory,
    OrganizationFactory,
    OrganizationSettingFactory,
)
from canvas_sdk.v1.data import (
    AppointmentReminder,
    BusinessLineSetting,
    OrganizationSetting,
)
from canvas_sdk.v1.data.appointment import AppointmentReminderStatus


@pytest.mark.django_db
def test_appointment_reminders_are_read_from_the_appointment() -> None:
    """An appointment lists one reminder per channel tried, with its recipient and status."""
    appointment = AppointmentFactory.create()
    text = AppointmentReminderFactory.create(appointment=appointment)
    email = AppointmentReminderFactory.create(
        appointment=appointment,
        phone_number=None,
        email="patient@example.com",
        status=AppointmentReminderStatus.FAILED,
    )
    AppointmentReminderFactory.create()

    reminders = {r.id: r for r in appointment.reminders.all()}

    assert set(reminders) == {text.id, email.id}
    assert reminders[text.id].phone_number == "5555550100"
    assert reminders[text.id].status == AppointmentReminderStatus.SENT
    assert reminders[email.id].email == "patient@example.com"
    assert reminders[email.id].status == AppointmentReminderStatus.FAILED
    assert AppointmentReminder.objects.get(id=text.id).appointment == appointment


@pytest.mark.django_db
def test_appointment_reminder_status_is_null_before_the_send_finishes() -> None:
    """A reminder row exists before its send attempt sets a status."""
    reminder = AppointmentReminderFactory.create(status=None)

    assert AppointmentReminder.objects.get(id=reminder.id).status is None


@pytest.mark.django_db
def test_organization_settings_are_read_from_the_organization() -> None:
    """The organization's reminder schedule and message customization are readable."""
    organization = OrganizationFactory.create()
    OrganizationSettingFactory.create(organization=organization)
    OrganizationSettingFactory.create(
        organization=organization,
        name="appointmentReminderCustomization",
        value="Please bring your insurance card.",
    )

    values = {s.name: s.value for s in organization.settings.all()}

    assert values == {
        "appointmentReminders": {"daysAhead": 4, "hourOfDay": 13},
        "appointmentReminderCustomization": "Please bring your insurance card.",
    }
    assert OrganizationSetting.objects.get(name="appointmentReminders").organization == (
        organization
    )


@pytest.mark.django_db
def test_business_line_settings_are_read_from_the_business_line() -> None:
    """A business line's reminder message text, template variables included, is readable."""
    business_line = BusinessLineFactory.create()
    BusinessLineSettingFactory.create(
        business_line=business_line, value="Hi {{PATIENT_FIRST_NAME}}, see you soon."
    )
    BusinessLineSettingFactory.create()

    settings = list(business_line.settings.all())

    assert [(s.name, s.value) for s in settings] == [
        ("appointmentReminderCustomization", "Hi {{PATIENT_FIRST_NAME}}, see you soon.")
    ]
    assert BusinessLineSetting.objects.get(dbid=settings[0].dbid).business_line == business_line
