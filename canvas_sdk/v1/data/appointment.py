from django.db import models


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
        db_table = "canvas_sdk_data_api_appointment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
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


class AppointmentExternalIdentifier(models.Model):
    """AppointmentExternalIdentifier."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_appointmentexternalidentifier_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    use = models.CharField()
    identifier_type = models.CharField()
    system = models.CharField()
    value = models.CharField()
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
