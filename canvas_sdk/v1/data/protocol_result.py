from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class ProtocolResultStatus(models.TextChoices):
    """Constants for ProtocolResultStatus."""

    STATUS_DUE = "due"
    STATUS_SATISFIED = "satisfied"
    STATUS_NOT_APPLICABLE = "not_applicable"
    STATUS_PENDING = "pending"
    STATUS_NOT_RELEVANT = "not_relevant"


class ProtocolResult(TimestampedModel):
    """ProtocolResult."""

    class Meta:
        abstract = True

    title = models.TextField(blank=True, default="")
    narrative = models.TextField(blank=True, default="")
    result_identifiers = ArrayField(base_field=models.TextField())
    types = ArrayField(base_field=models.TextField())
    protocol_key = models.TextField(default="")
    plugin_name = models.TextField(null=True, blank=True)
    status = models.TextField(
        choices=ProtocolResultStatus.choices, default=ProtocolResultStatus.STATUS_NOT_APPLICABLE
    )
    due_in = models.IntegerField(null=True, default=-1)
    days_of_notice = models.IntegerField(default=30)
    snoozed = models.BooleanField(default=False)
    sources = models.JSONField(default=dict)
    recommendations = models.JSONField(default=dict)
    top_recommendation_key = models.TextField(blank=True, default="")
    next_review = models.DateTimeField(null=True)
    feedback_enabled = models.BooleanField(default=False)
    plugin_can_be_snoozed = models.BooleanField(default=False)


__exports__ = (
    "ProtocolResult",
    "ProtocolResultStatus",
)
