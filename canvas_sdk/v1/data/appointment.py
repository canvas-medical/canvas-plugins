from django.db import models

from canvas_sdk.v1.data import PracticeLocation
from canvas_sdk.v1.data.note import Note, NoteType
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.user import CanvasUser


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


class Appointment(models.Model):
    """Appointment."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_appointment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        related_name="appointments",
        null=True,
    )
    appointment_rescheduled_from = models.ForeignKey(
        "Appointment",
        on_delete=models.DO_NOTHING,
        related_name="appointment_rescheduled_to",
        null=True,
    )
    provider = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, null=True)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    comment = models.TextField(null=True)
    note = models.ForeignKey(Note, on_delete=models.DO_NOTHING, null=True)

    note_type = models.ForeignKey(
        NoteType, on_delete=models.DO_NOTHING, related_name="appointments", null=True
    )

    status = models.CharField(
        max_length=20,
        choices=AppointmentProgressStatus,
    )
    meeting_link = models.URLField(null=True, blank=True)
    telehealth_instructions_sent = models.BooleanField()
    location = models.ForeignKey(PracticeLocation, on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(null=True, blank=True)
