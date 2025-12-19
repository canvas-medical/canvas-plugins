from typing import Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    TimestampedModel,
)


class IntegrationTaskStatus(models.TextChoices):
    """Status choices for IntegrationTask."""

    UNREAD = "UNR", "Unread"
    UNREAD_ERROR = "UER", "Unread Error"
    READ = "REA", "Read"
    ERROR = "ERR", "Error"
    PROCESSED = "PRO", "Processed"
    REVIEWED = "REV", "Reviewed"
    JUNK = "JUN", "Junk"


class IntegrationTaskChannel(models.TextChoices):
    """Channel choices for IntegrationTask."""

    FAX = "fax", "Fax"
    DOCUMENT_UPLOAD = "document_upload", "Document Upload"
    FROM_INTEGRATION_ENGINE = "from_integration_engine", "From Integration Engine"
    FROM_PATIENT_PORTAL = "from_patient_portal", "From Patient Portal"


class IntegrationTaskQuerySet(BaseQuerySet, ForPatientQuerySetMixin):
    """QuerySet for IntegrationTask with custom filter methods."""

    def for_patient(self, patient_id: str) -> Self:
        """Filter tasks by patient ID."""
        return self.filter(patient__id=patient_id)

    # Status filters
    def unread(self) -> Self:
        """Filter to unread tasks."""
        return self.filter(status=IntegrationTaskStatus.UNREAD)

    def pending_review(self) -> Self:
        """Filter to tasks pending review (UNREAD or READ)."""
        return self.filter(status__in=[IntegrationTaskStatus.UNREAD, IntegrationTaskStatus.READ])

    def processed(self) -> Self:
        """Filter to processed tasks (PROCESSED or REVIEWED)."""
        return self.filter(
            status__in=[IntegrationTaskStatus.PROCESSED, IntegrationTaskStatus.REVIEWED]
        )

    def with_errors(self) -> Self:
        """Filter to tasks with errors (ERROR or UNREAD_ERROR)."""
        return self.filter(
            status__in=[IntegrationTaskStatus.ERROR, IntegrationTaskStatus.UNREAD_ERROR]
        )

    def junked(self) -> Self:
        """Filter to junked tasks."""
        return self.filter(status=IntegrationTaskStatus.JUNK)

    def not_junked(self) -> Self:
        """Filter to non-junked tasks."""
        return self.exclude(status=IntegrationTaskStatus.JUNK)

    # Channel filters
    def faxes(self) -> Self:
        """Filter to fax tasks."""
        return self.filter(channel=IntegrationTaskChannel.FAX)

    def uploads(self) -> Self:
        """Filter to document upload tasks."""
        return self.filter(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)

    def from_integration_engine(self) -> Self:
        """Filter to tasks from integration engine."""
        return self.filter(channel=IntegrationTaskChannel.FROM_INTEGRATION_ENGINE)

    def from_patient_portal(self) -> Self:
        """Filter to tasks from patient portal."""
        return self.filter(channel=IntegrationTaskChannel.FROM_PATIENT_PORTAL)


IntegrationTaskManager = models.Manager.from_queryset(IntegrationTaskQuerySet)


class IntegrationTask(TimestampedModel):
    """IntegrationTask - represents incoming documents that need processing.

    This includes faxes, document uploads, lab results, and patient portal submissions.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_integrationtask_001"

    objects = cast(IntegrationTaskQuerySet, IntegrationTaskManager())

    id = models.IntegerField(unique=True)
    status = models.CharField(max_length=3, choices=IntegrationTaskStatus.choices)
    type = models.CharField(max_length=125)
    title = models.CharField(max_length=256)
    channel = models.CharField(max_length=50, choices=IntegrationTaskChannel.choices)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, null=True, related_name="integration_tasks"
    )
    service_provider = models.ForeignKey(
        "v1.ServiceProvider",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="integration_tasks",
    )

    @property
    def is_fax(self) -> bool:
        """Check if this is a fax task."""
        return self.channel == IntegrationTaskChannel.FAX

    @property
    def is_pending(self) -> bool:
        """Check if this task is pending review."""
        return self.status in [IntegrationTaskStatus.UNREAD, IntegrationTaskStatus.READ]

    @property
    def is_processed(self) -> bool:
        """Check if this task has been processed."""
        return self.status in [IntegrationTaskStatus.PROCESSED, IntegrationTaskStatus.REVIEWED]

    @property
    def has_error(self) -> bool:
        """Check if this task has an error."""
        return self.status in [IntegrationTaskStatus.ERROR, IntegrationTaskStatus.UNREAD_ERROR]

    @property
    def is_junked(self) -> bool:
        """Check if this task is junked."""
        return self.status == IntegrationTaskStatus.JUNK


__exports__ = (
    "IntegrationTask",
    "IntegrationTaskStatus",
    "IntegrationTaskChannel",
    "IntegrationTaskQuerySet",
)
