from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class AppointmentProgressStatus(models.TextChoices):
    """AppointmentProgressStatus."""

    UNCONFIRMED = "unconfirmed", "Unconfirmed"
    ATTEMPTED = "attempted", "Attempted"
    CONFIRMED = "confirmed", "Confirmed"
    ARRIVED = "arrived", "Arrived"
    ROOMED = "roomed", "Roomed"
    EXITED = "exited", "Exited"
    NOSHOWED = "noshowed", "No-showed"
    CANCELLED = "cancelled", "Cancelled"


class Appointment(IdentifiableModel):
    """Appointment."""

    class Meta:
        db_table = "canvas_sdk_data_api_appointment_001"

    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="appointments",
        null=True,
    )
    appointment_rescheduled_from = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        related_name="appointment_rescheduled_to",
        null=True,
    )
    provider = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, null=True)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    comment = models.TextField(null=True)
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, null=True)

    note_type = models.ForeignKey(
        "v1.NoteType", on_delete=models.DO_NOTHING, related_name="appointments", null=True
    )

    status = models.CharField(
        max_length=20,
        choices=AppointmentProgressStatus,
    )
    meeting_link = models.URLField(null=True, blank=True)
    telehealth_instructions_sent = models.BooleanField()
    location = models.ForeignKey("v1.PracticeLocation", on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(null=True, blank=True)


class AppointmentExternalIdentifier(IdentifiableModel):
    """AppointmentExternalIdentifier."""

    class Meta:
        db_table = "canvas_sdk_data_api_appointmentexternalidentifier_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    use = models.CharField(max_length=255)
    identifier_type = models.CharField(max_length=255)
    system = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiration_date = models.DateField()
    appointment = models.ForeignKey(
        Appointment, on_delete=models.DO_NOTHING, related_name="external_identifiers"
    )


__exports__ = (
    "AppointmentProgressStatus",
    "Appointment",
    "AppointmentExternalIdentifier",
)
