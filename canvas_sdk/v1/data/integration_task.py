from typing import Self
from uuid import UUID

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
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


class IntegrationTaskQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """QuerySet for IntegrationTask with custom filter methods."""

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


class IntegrationTaskReviewQuerySet(BaseQuerySet):
    """QuerySet for IntegrationTaskReview with custom filter methods."""

    def for_task(self, task_id: str) -> Self:
        """Filter reviews by task ID."""
        return self.filter(task__id=task_id)

    def junked(self) -> Self:
        """Filter to junked reviews."""
        return self.filter(junked=True)

    def not_junked(self) -> Self:
        """Filter to non-junked reviews."""
        return self.filter(junked=False)

    def active(self) -> Self:
        """Filter to active (non-junked) reviews."""
        return self.not_junked()

    def by_reviewer(self, reviewer_id: str | UUID) -> Self:
        """Filter reviews by reviewer ID."""
        return self.filter(reviewer__id=reviewer_id)

    def by_team(self, team_id: str) -> Self:
        """Filter reviews by team reviewer ID."""
        return self.filter(team_reviewer__id=team_id)


class IntegrationTask(TimestampedModel, IdentifiableModel):
    """IntegrationTask - represents incoming documents that need processing.

    This includes faxes, document uploads, lab results, and patient portal submissions.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_integrationtask_001"

    objects = models.Manager.from_queryset(IntegrationTaskQuerySet)()

    status = models.CharField(
        max_length=3,
        choices=IntegrationTaskStatus.choices,
        default=IntegrationTaskStatus.UNREAD,
        db_index=True,
    )
    type = models.CharField(max_length=125, blank=True, default="")
    title = models.CharField(max_length=256, blank=True, default="")
    document = models.FileField(max_length=255)
    channel = models.CharField(max_length=50, choices=IntegrationTaskChannel.choices, db_index=True)
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


class IntegrationTaskReview(TimestampedModel, IdentifiableModel):
    """IntegrationTaskReview - represents a review assignment for an integration task.

    Reviews track who is responsible for processing a document and its current state.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_integrationtaskreview_001"

    objects = models.Manager.from_queryset(IntegrationTaskReviewQuerySet)()

    task = models.ForeignKey(
        IntegrationTask,
        on_delete=models.DO_NOTHING,
        related_name="reviews",
    )
    template_name = models.CharField(max_length=1000, null=True)
    document_key = models.CharField(max_length=250, null=True, blank=True)
    reviewer = models.ForeignKey(
        "v1.Staff",
        on_delete=models.DO_NOTHING,
        related_name="integration_task_reviews",
        null=True,
    )
    team_reviewer = models.ForeignKey(
        "v1.Team",
        on_delete=models.DO_NOTHING,
        related_name="integration_task_team_reviews",
        null=True,
        blank=True,
    )
    junked = models.BooleanField(default=False)

    @property
    def is_active(self) -> bool:
        """Check if this review is active (not junked)."""
        return not self.junked


__exports__ = (
    "IntegrationTask",
    "IntegrationTaskStatus",
    "IntegrationTaskChannel",
    "IntegrationTaskQuerySet",
    "IntegrationTaskReview",
    "IntegrationTaskReviewQuerySet",
)
