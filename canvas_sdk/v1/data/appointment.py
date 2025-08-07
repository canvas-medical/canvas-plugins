from django.db import models
from typing import TYPE_CHECKING

from canvas_sdk.v1.data.base import IdentifiableModel

if TYPE_CHECKING:
    from canvas_sdk.v1.data.command import Command
    from canvas_sdk.v1.data.reason_for_visit import ReasonForVisitSettingCoding


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

    @property
    def reason_for_visit(self) -> "ReasonForVisitSettingCoding | None":
        """
        Get the primary reason for visit coding for this appointment.
        
        Returns the first reason for visit coding found in the appointment's note commands,
        or None if no reason for visit is found.
        
        Returns:
            ReasonForVisitSettingCoding instance or None
        """
        reasons = self.get_reasons_for_visit()
        return reasons[0] if reasons else None

    def get_reasons_for_visit(self) -> list["ReasonForVisitSettingCoding"]:
        """
        Get all reason for visit codings for this appointment.
        
        Looks through the appointment's associated note commands to find all
        reason for visit commands and returns the associated ReasonForVisitSettingCoding objects.
        
        Returns:
            List of ReasonForVisitSettingCoding instances
        """
        if not self.note_id:
            return []
        
        from canvas_sdk.v1.data.command import Command
        from canvas_sdk.v1.data.reason_for_visit import ReasonForVisitSettingCoding
        
        # Get all reason for visit commands for this appointment's note
        rfv_commands = Command.objects.filter(
            note_id=self.note_id,
            schema_key="reasonForVisit"
        ).exclude(entered_in_error__isnull=False)
        
        reasons = []
        for command in rfv_commands:
            coding_data = command.data.get("coding")
            if coding_data:
                try:
                    # Handle both UUID strings and coding objects
                    if isinstance(coding_data, str):
                        # Direct reference by ID
                        reason_coding = ReasonForVisitSettingCoding.objects.get(id=coding_data)
                        reasons.append(reason_coding)
                    elif isinstance(coding_data, dict):
                        # Coding object with code and system
                        reason_coding = ReasonForVisitSettingCoding.objects.get(
                            code=coding_data.get("code"),
                            system=coding_data.get("system")
                        )
                        reasons.append(reason_coding)
                except ReasonForVisitSettingCoding.DoesNotExist:
                    # Skip invalid references
                    continue
        
        return reasons

    def get_reason_for_visit_commands(self) -> list["Command"]:
        """
        Get all reason for visit commands for this appointment.
        
        Returns the raw Command objects that contain reason for visit data,
        allowing access to additional fields like comment, structured flag, etc.
        
        Returns:
            List of Command instances with schema_key="reasonForVisit"
        """
        if not self.note_id:
            return []
        
        from canvas_sdk.v1.data.command import Command
        
        return list(Command.objects.filter(
            note_id=self.note_id,
            schema_key="reasonForVisit"
        ).exclude(entered_in_error__isnull=False))


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
